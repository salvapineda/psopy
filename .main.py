
code = 'unit_commitment'

#######################  UNIT COMMITMENT  ##########################

if code=='unit_commitment':

  # Import system class
  from psopy import system

  # Load system data. Further info: help(system)
  sys1 = system('data/3bus.xlsx',shed_cost=1000)

  # Solve unit commitment. Further info: help(system.solve_uc)
  sys1.solve_uc(solver='cplex',neos=True,network=True,commit=True,excel=True)

#######################  TIME AGGREGATION  ##########################

if code=='time_aggregation':

  # Import time_serie class
  from psopy import time_serie

  # Create time_serie object. Further info: help(time_serie)
  ts1 = time_serie('data/wind1.xlsx')

  # Time series is aggregated in 48 time periods according to chrono method. Further info: help(time_serie.agg)
  ts1.agg(nper=48,method='chrono',plot=True)

