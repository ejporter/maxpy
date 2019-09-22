# maxpy - A platform for automating the process of writing scripts run by ANSYS Maxwell.

The maxpy package is designed to compliment the already existing gdspy, cdes, and sonpy packages (the latter two also having been created by MIT EQuS). The primary purpose of maxpy is to create an easy to use platform that generates a script to be run in Maxwell, automated the many tedious tasks required for Maxwell simulations. It currently contains to simple, yet useful classes, Maxwell() and maxParse(). 

## Maxwell()
Maxwell() can be used to create simple ANSYS Maxwell files in the electrostatic mode for simulatinf capacitance and capacitive coupling coefficient matrices. Limited knowledge of Lincoln Lab standards for layer name and thickness conventions are known by the class, but if non-standard layers are used, information must be updated when being run. Basic functionalities include inputting a gds file that can be set up with material and thickness information and then simulated. The data can then be exported to a outside txt file.

## maxParse()
Once the simulation has been run, maxParse() can then be used extract necessary information from the txt file that was written. The class has only one parameter and one method, fileName and update, respectively. If you would like to change the fileName of one particular instance of maxParse, do so through the update method so the information will be recalculated before being output.

## Examples
For a more detailed look at the functionality of maxpy, please see the example jupyter notebook that comes with this package. It shows you how to fully integrate maxpy with cdes and sonpy into one cohesive file that calculates all information from cdes code specifying a specific chip design. 
