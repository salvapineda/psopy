# Power System Optimization in PYthon (PSOPY)

This repository includes Python codes for different power system related problems.

## Installation

```python
git clone https://github.com/salvapineda/psopy.git

cd psopy
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

Time period aggregation using representative days or chronological clustering [1]

```python
  # Import pandas and time_serie class
  import pandas as pd
  from psopy import time_serie

  # Create time_serie object from xlsx file. Further info: help(time_serie)
  ts1 = time_serie(pd.read_excel('data/wind1.xlsx'))

  # Time series is aggregated in 48 time periods according to chrono method. Further info: help(time_serie.agg)
  ts1.agg(nper=48,method='chrono',plot=True)
```

## References

[1]  S. Pineda and J. M. Morales, "Chronological Time-Period Clustering for Optimal Capacity Expansion Planning With Storage," in IEEE Transactions on Power Systems, vol. 33, no. 6, pp. 7162-7170, Nov. 2018.

## Do you want to contribute?
 
 Any feedback is welcome so feel free to ask or comment anything you want via a Pull Request in this repo. If you need extra help, you can ask Salvador Pineda (spinedamorente@gmail.com).
 
 ## Contributors 🌬☀
 
 * [OASYS group](http://oasys.uma.es) -  groupoasys@gmail.com
 
 ## Developed by 👨‍💻👨‍💻👩‍💻
 * [Salvador Pineda](https://www.researchgate.net/profile/Salvador_Pineda) - spinedamorente@gmail.com
