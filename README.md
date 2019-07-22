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
3. Run the instructions below or execute the file main.py. The first instruction imports the class sys. The second instruction loads the power system data into the objects instance sys1. The last instruction solves the unit commitment problem according to the selected options.
4. Results are placed in the result folder
