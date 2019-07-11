from powpy import system

sys1 = system(gen_file='data/gen3bus.csv',
              lin_file='data/lin3bus.csv',
              dem_file='data/dem3bus.csv',
              ren_file='data/ren3bus.csv',
              shed_cost=1000)

sys1.solve(solver='cplex',
           neos=False,
           network=True,
           commit=True)

