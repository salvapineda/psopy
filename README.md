# Power System Optimization in PYthon (PSOPY)

This repository includes Python codes for different power system related problems.

## Installation

```python
git clone https://github.com/salvapineda/psopy.git
```

## Unit Commitment

Multi-period network-constrained unit-commitment problem as a mixed-integer linear programming problem

```python
  # import system class
  from psopy import system

  # load system data
  sys1 = system('data/3bus.xlsx',shed_cost=1000)

  # solve unit commitment
  sys1.solve_uc(solver='cplex',neos=True,network=True,commit=True,excel=True)
```

## Time Aggregation

Time period aggregation using representative days or chronological clustering

```python
  # import time_serie class
  from psopy import time_serie

  # load wind time series
  ts1 = time_serie('data/wind1.xlsx')

  # time series is aggregated
  ts1.agg(48,method='chrono')

  # aggregated time series is plotted
  ts1.plot(1,168)
```
