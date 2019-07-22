from code import system

sys1 = system('3bus')

sys1.solve(solver='cplex',
           neos=False,
           network=True,
           commit=True)

