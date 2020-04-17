############################ IMPORT ############################

import pdb
import pandas as pd
import numpy as np
import pyomo.environ as pe
import time
import matplotlib.pyplot as plt
from scipy.sparse import diags
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import pairwise_distances

############################ TIME AGGREGATION ############################

class time_serie:
  """
  A class to represent a time serie
  """

  def __init__(self,data):
    """
    Constructs all the necessary attributes for the time_serie object.

    Parameters
    ----------
    data(dataframe): pandas data frame with time serie data
    """
    self.df = data
  
  def agg(self,nper=168,method='chrono',plot=False): 
    """
    Aggregate the time serie data.

    Parameters
    ----------
    nper(int, default = 168): number of time periods of the aggregated time serie
    method(str, default = 'chrono'): method used to aggregate the time serie
        - 'days': the original time series is aggregated using nper/24 represenative days
        - 'weeks': the original time series is aggregated using nper/168 represenative weeks
        - 'chrono': the original time series is aggregated using nper chronological periods of different durations
    plot(boolean, default = 'False'): if True, it plots the comparison of the original time serie and the aggregated one

    Returns
    -------
    aggregation(dataframe): aggregation results including
        - value of the parameter for each aggregated time period
        - tau: duration of the aggregated time period (equal to 1 for 'weeks' and 'days')
        - weg: weight of the aggregated time period (equal to 1 for 'chrono')
        - chr: chronologial information
    approximation(dataframe): approximated time series according to the selected aggregation method
    """  

    if method=='chrono':
      clus = 'chrono'
      dur = 1
    elif method=='days':
      clus = 'hier'
      dur = 24
    elif method=='week':
      clus = 'hier'
      dur = 168
  
    arr0 = self.df.values.reshape(int(self.df.shape[0]/dur),int(self.df.shape[1]*dur))
    nclus = int(nper/dur)
    arr1 = np.zeros((nclus,arr0.shape[1]))
    arr2 = np.zeros((int(self.df.shape[0]/dur),arr0.shape[1]))
  
    if clus=='chrono':     
      conec = diags([np.ones(arr0.shape[0]-1),np.ones(arr0.shape[0]-1)], [-1, 1])
      model = AgglomerativeClustering(linkage='ward',connectivity=conec,n_clusters=nclus, compute_full_tree=False)  
      model.fit(StandardScaler().fit_transform(arr0))    
      res = np.unique(model.labels_,return_index=True,return_counts=True) 
      for i in res[0]:
        arr1[i,:] = arr0[model.labels_==i,:].mean(axis=0)
      for i,j in enumerate(model.labels_):
        arr2[i,:] = arr1[j,:] 
      arr1 = arr1[model.labels_[np.sort(res[1])],:]
      arr1 = np.column_stack((arr1,np.repeat(res[2][model.labels_[np.sort(res[1])]],dur)))
      arr1 = np.column_stack((arr1,np.ones(nclus)))
      arr1 = np.column_stack((arr1,np.append(nclus-1,np.zeros(nclus-1))))   
         
    elif clus=='hier':
      model = AgglomerativeClustering(linkage='ward',n_clusters=nclus,compute_full_tree=False)
      model.fit(StandardScaler().fit_transform(arr0))
      res = np.unique(model.labels_,return_index=True,return_counts=True) 
      for i in res[0]:
        index = np.argmin(pairwise_distances(arr0[model.labels_==i,:]).mean(axis=0))
        arr1[i,:] = arr0[model.labels_==i,:][index,:]  
      for i,j in enumerate(model.labels_):
        arr2[i,:] = arr1[j,:]    
      arr1 = arr1.reshape(nclus*dur,self.df.shape[1])
      arr2 = arr2.reshape(self.df.shape[0],self.df.shape[1])
      arr1 = np.column_stack((arr1,np.ones(nclus*dur)))
      arr1 = np.column_stack((arr1,np.repeat(res[2][model.labels_[np.sort(res[1])]],dur)))
      arr1 = np.column_stack((arr1,np.zeros(nclus*dur)))    
      arr1[np.array(range(0,nclus*dur,dur)),-1] = np.array(range(0,nclus*dur,dur))-1+dur       
  
    self.aggregation = pd.DataFrame(arr1,columns=np.append(self.df.columns.values,('tau','weg','chr')))
    self.approximation = pd.DataFrame(arr2,columns=self.df.columns)

    if plot:
      for k in self.approximation.columns:
        df3 = pd.concat([self.df[k],self.approximation[k]],axis=1)   
        df3.columns = ['original', 'aggregated']     
        df3.plot(title=k)   
        plt.show()

############################ UNIT COMMITMENT ############################

'''
This Python code solves a multi-period network-constrained unit-commitment problem as a mixed-integer linear programming problem.

The power system data must be provided using a .xlsx file with four different sheets:
- gen: thermal unit data (location, cost, minimum and maximum output)
- lin: line transmission data (susceptance and capacity)
- dem: electricity demand at each node for each time period
- ren: renewable electricity production at each node for each time period

Results are provided in file output.xlsx. These results include the unit power production, unit commitment, power flows through the transmission lines, shed load and spilage of renewable production for each time period

The options of the solve function are:
- solver (default=CPLEX): the mixed-integer optimization software used to solve the model
- neos (default=True): it allows the access to the solvers hosted in the NEOS server. More info [here](https://neos-server.org/neos/)
- network (default=True): If True, the model is solved considering the network constraints. If False, the model is solved assuming that network congestion does not occur.
- commit (default=True): If True, binary variables are used to model the on/off status of thermal units. If False, the minimum output of thermal units are disregarded and the model is solved as a linear model.

The output file includes:
- pro: production level of generating units
- u: commitment status of generating units
- flw: power flow through transmission lines
- shd: load shedding at each but
- spl: spillage of renewable generation at each bus
'''

class system:

    def __init__(self,file_data,shed_cost=1000):

        self.file_data = file_data

        self.gen = pd.read_excel(file_data,sheet_name='gen')
        self.lin = pd.read_excel(file_data,sheet_name='lin')
        self.dem = pd.read_excel(file_data,sheet_name='dem')
        self.ren = pd.read_excel(file_data,sheet_name='ren')

        self.ng = len(self.gen)
        self.nl = len(self.lin)
        self.nb = self.dem.shape[1]
        self.nt = self.dem.shape[0]
        self.cs = shed_cost

    def solve_uc(self,solver='cplex',neos=True,network=True,commit=True,excel=True):

        #Define the model
        m = pe.ConcreteModel()

        #Define the sets
        m.g = pe.Set(initialize=list(range(self.ng)),ordered=True)
        m.l = pe.Set(initialize=list(range(self.nl)),ordered=True)
        m.b = pe.Set(initialize=list(range(self.nb)),ordered=True)
        m.t = pe.Set(initialize=list(range(self.nt)),ordered=True)

        #Define variables
        m.z = pe.Var()
        m.pro = pe.Var(m.g,m.t,within=pe.NonNegativeReals)
        if commit:
          m.u = pe.Var(m.g,m.t,within=pe.Binary)
        else:
          m.u = pe.Var(m.g,m.t,within=pe.NonNegativeReals,bounds=(0,1))
        m.shd = pe.Var(m.b,m.t,within=pe.NonNegativeReals)
        m.spl = pe.Var(m.b,m.t,within=pe.NonNegativeReals)
        m.ang = pe.Var(m.b,m.t)
        m.flw = pe.Var(m.l,m.t)

        #Objective function
        def obj_rule(m):
            return m.z
        m.obj = pe.Objective(rule=obj_rule)

        #Definition cost
        def cost_def_rule(m):
            return m.z == sum(self.gen['cost'][g]*m.pro[g,t] for g in m.g for t in m.t) + sum(self.cs*m.shd[b,t] for b in m.b for t in m.t)
        m.cost_def = pe.Constraint(rule=cost_def_rule)

        #Energy balance
        def bal_rule(m,b,t):
            return sum(m.pro[g,t] for g in m.g if self.gen['bus'][g] == b) + self.ren.iloc[t,b] + m.shd[b,t] + sum(m.flw[l,t] for l in m.l if self.lin['to'][l] == b) == self.dem.iloc[t,b] + m.spl[b,t] + sum(m.flw[l,t] for l in m.l if self.lin['from'][l] == b)
        m.bal = pe.Constraint(m.b, m.t, rule=bal_rule)

        #Minimum generation
        def min_gen_rule(m,g,t):
            return m.pro[g,t] >= m.u[g,t]*self.gen['min'][g]
        m.min_gen = pe.Constraint(m.g, m.t, rule=min_gen_rule)

        #Maximum generation
        def max_gen_rule(m,g,t):
            return m.pro[g,t] <= m.u[g,t]*self.gen['max'][g]
        m.max_gen = pe.Constraint(m.g, m.t, rule=max_gen_rule)

        #Maximum spilage
        def max_spil_rule(m,b,t):
            return m.spl[b,t] <= self.ren.iloc[t,b]
        m.max_spil = pe.Constraint(m.b, m.t, rule=max_spil_rule)

        #Maximum shedding
        def max_shed_rule(m,b,t):
            return m.shd[b,t] <= self.dem.iloc[t,b]
        m.max_shed = pe.Constraint(m.b, m.t, rule=max_shed_rule)

        #Power flow definition
        def flow_rule(m,l,t):
            return m.flw[l,t] == self.lin['sus'][l]*(m.ang[self.lin['from'][l],t] - m.ang[self.lin['to'][l],t])
        m.flow = pe.Constraint(m.l, m.t, rule=flow_rule)

        #Max power flow
        def max_flow_rule(m,l,t):
            if network:
              return m.flw[l,t] <= self.lin['cap'][l]
            else:
              return pe.Constraint.Skip
        m.max_flow = pe.Constraint(m.l, m.t, rule=max_flow_rule)

        #Min power flow
        def min_flow_rule(m,l,t):
            if network:
              return m.flw[l,t] >= -self.lin['cap'][l]
            else:
              return pe.Constraint.Skip
        m.min_flow = pe.Constraint(m.l, m.t, rule=min_flow_rule)

        #We solve the optimization problem
        solver_manager = pe.SolverManagerFactory('neos')
        opt = pe.SolverFactory('cplex')
        opt.options['threads'] = 1
        opt.options['mipgap'] = 1e-9
        if neos:
          res = solver_manager.solve(m,opt=opt,symbolic_solver_labels=True,tee=True)
        else:
          res = opt.solve(m,symbolic_solver_labels=True,tee=True)
        print(res['Solver'][0])

        #We save the results
        self.pro = [[round(m.pro[g,t].value,2) for t in m.t] for g in m.g]
        self.u = [[round(m.u[g,t].value,2) for t in m.t] for g in m.g]
        self.flw = [[round(m.flw[l,t].value,2) for t in m.t] for l in m.l]
        self.shd = [[round(m.shd[b,t].value,2) for t in m.t] for b in m.b]
        self.spl = [[round(m.spl[b,t].value,2) for t in m.t] for b in m.b]

        #Export to Excel
        if excel:
            with pd.ExcelWriter(self.file_data[:-5]+'_output.xlsx') as writer:
                pd.DataFrame(self.pro).T.to_excel(writer,'pro')
                pd.DataFrame(self.u).T.to_excel(writer,'u')
                pd.DataFrame(self.flw).T.to_excel(writer,'flw')
                pd.DataFrame(self.shd).T.to_excel(writer,'shd')
                pd.DataFrame(self.spl).T.to_excel(writer,'spl')

