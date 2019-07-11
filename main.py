from powpy import system

sys1 = system(gen_file='3bus/gen.csv',
              lin_file='3bus/lin.csv',
              dem_file='3bus/dem.csv',
              ren_file='3bus/ren.csv',
              shed_cost=1000)

sys1.solve(solver='cplex',
           neos=False,
           network=True,
           commit=True)

