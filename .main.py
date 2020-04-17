
code = 'time_aggregation'

#######################  UNIT COMMITMENT  ##########################

if code=='unit_commitment':

  # import system class
  from psopy import system

  # load system data
  sys1 = system('data/3bus.xlsx',shed_cost=1000)

  # solve unit commitment
  sys1.solve_uc(solver='cplex',neos=True,network=True,commit=True,excel=True)

#######################  TIME AGGREGATION  ##########################

if code=='time_aggregation':

  # Import pandas and time_serie class
  import pandas as pd
  from psopy import time_serie

  # Create time_serie object from xlsx file. Further info: help(time_serie)
  ts1 = time_serie(pd.read_excel('data/wind1.xlsx'))

  # Time series is aggregated in 48 time periods according to chrono method. Further info: help(time_serie.agg)
  ts1.agg(nper=48,method='chrono',plot=True)

