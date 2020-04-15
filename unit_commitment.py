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
'''

############################ IMPORT ############################

import pdb
import pandas as pd
import numpy as np
import pyomo.environ as pe

############################ MAIN ############################

def main():

  # load system data
  sys1 = system('3bus.xlsx',shed_cost=1000)

  # solve unit commitment
  sys1.solve(solver='cplex',neos=True,network=True,commit=True)

############################ CODE ############################

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

    def solve(self,solver='cplex',neos=True,network=True,commit=True):

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
        with pd.ExcelWriter(self.file_data[:-5]+'_output.xlsx') as writer:
            pd.DataFrame([[round(m.pro[g,t].value,2) for t in m.t] for g in m.g]).T.to_excel(writer,'pro')
            pd.DataFrame([[round(m.u[g,t].value,2) for t in m.t] for g in m.g]).T.to_excel(writer,'u')
            pd.DataFrame([[round(m.flw[l,t].value,2) for t in m.t] for l in m.l]).T.to_excel(writer,'flw')
            pd.DataFrame([[round(m.shd[b,t].value,2) for t in m.t] for b in m.b]).T.to_excel(writer,'shd')
            pd.DataFrame([[round(m.spl[b,t].value,2) for t in m.t] for b in m.b]).T.to_excel(writer,'spl')

############################ RUN ############################

if __name__ == '__main__':
    main()

