import pdb
import pandas as pd
import numpy as np
import pyomo.environ as pe

class system:
    def __init__(self,gen_file,lin_file,dem_file,ren_file,shed_cost=1000):
        self.gen = pd.read_csv(gen_file)
        self.lin = pd.read_csv(lin_file)
        self.dem = pd.read_csv(dem_file)
        self.ren = pd.read_csv(ren_file)
        self.ng = len(self.gen)
        self.nl = len(self.lin)
        self.nb = self.dem.shape[1]
        self.nt = self.dem.shape[0]
        self.cs = shed_cost

    def solve(self,solver='cplex',neos=False,network=True,commit=True):
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
        self.time = res['Solver'][0]['Time']
        self.output = m
        self.prod = pyomo2df(m.pro,m.g,m.t).T
        self.stat = pyomo2df(m.u,m.g,m.t).T
        self.flow = pyomo2df(m.flw,m.l,m.t).T
        self.shed = pyomo2df(m.shd,m.b,m.t).T
        self.spil = pyomo2df(m.spl,m.b,m.t).T

def pyomo2df(pyomo_var,index1,index2):
    mat = []
    for i in index1:
        row = []
        for j in index2:
            row.append(pyomo_var[i,j].value)
        mat.append(row)
    return pd.DataFrame(mat)
