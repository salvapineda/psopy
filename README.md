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
  ```
3. Run the 3 instructions below or execute the file main.py. The first instruction imports the class sys. The second instruction loads the power system data into the object instance sys1. The last instruction solves the unit commitment problem according to the selected options.
```
from code import system
sys1 = system('3bus')
sys1.solve(solver='cplex',neos=True,network=True,commit=True)
```
4. Results are placed in the result folder. These results include the unit power production for each time period (prod.csv) and the power flows through the transmission lines for each time period (flow.csv)

The options of the solve function are:
- solver (default=CPLEX): the mixed-integer optimization software used to solve the model
- neos (default=True): it allows the access to the solvers hosted in the NEOS server. More info [here](https://neos-server.org/neos/)
- network (default=True): If True, the model is solved considering the network constraints. If False, the model is solved assuming that network congestion does not occur.
- commit (default=True): If True, binary variables are used to model the on/off status of thermal units. If False, the minimum output of thermal units are disregarded and the model is solved as a linear model.
