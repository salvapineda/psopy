# Power System Optimization in PYthon (PSOPY)

This Python code solves a multi-period network-constrained unit-commitment problem as a mixed-integer linear programming problem.

The power system data must be provided through 4 csv files contained in the same folder:
- gen.csv: thermal unit data (location, cost, minimum and maximum output)
- lin.csv: line transmission data (susceptance and capacity)
- dem.csv: electricity demand at each node for each time period
- ren.csv: renewable electricity production at each node for each time period

To use it follow the following steps:
1. Install Python 3.5 or higher
2. Clone the repository in your computer
```
git clone https://github.com/salvapineda/psopy.git
'''
3. 
