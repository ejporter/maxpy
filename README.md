# maxpy - A platform for automating the process of writing scripts run by ANSYS Maxwell.

The maxpy package is designed to compliment the already existing gdspy, cdes, and sonpy packages (the latter two also having been created by MIT EQuS). The primary purpose of maxpy is to create an easy to use platform that generates a script to be run in Maxwell, automated the many tedious tasks required for Maxwell simulations. It is currently comprised of one main class (maxwell()) that calls and handles the underlying classes (maxInit(), maxSetup(), maxGeo(), and maxSim()). 

### Current features include:
* Handling of mulitple projects and designs at once
* Importing .gds files
* Intelligent Maxwell setup procedures (centering, thickening sheets, assigning materials, etc. according to EQuS circuit design specs.)
* Basic draw and movement features
* Simulation setups

### Features currently planned/ uncommitted
* Excitation assignment
* Boolean operations (subtraction, union, etx.)
* More in depth drawing procedures
* More advanced simulation setup
* Auto signal naming

More detailed documentation on individual class structure and usage will be available soon.
