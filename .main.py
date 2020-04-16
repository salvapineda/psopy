
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

  # import time_serie class
  from psopy import time_serie

  # load wind time series
  ts1 = time_serie('data/wind1.xlsx')

  # time series is aggregated
  ts1.agg(48,method='days')

  # aggregated time series is plotted
  ts1.plot(1,168)
