***Scripting in ANSYS MAXWELL***

**Note:** The scripting procedure below is designed as a tool to save time while setting up a model in Maxwell. It is not intelligent enough so as to properly setup and verify boundary conditions, excitations, and conduction paths. Steps for doing so can be found in the other Maxwell wiki pages on inductance and capacitance matrices.

***Setup***

  * You will need to clone the following repository into a local directory: [[https://github.com/JBraumueller/maxpy.git|maxpy]]
  * The repo contains two files of use, only one of which you will actually be interacting with.
  * First is the Maxwell_Editor class. This class is what prepares the text strings in the given format that MAXWELL can work with. It also holds information provided about your gds file and uses that to intelligently create the syntax based on your specific model.
  * Next is maxwell_scripter.py. This is the file you will actually be running on your computer. It will prompt you with a few questions pertaining to your model and then, making use of the Maxwell_Editor class, will prepare a script for you to run within MAXWELL. This script will be saved into the directory you cloned the repo to.
  * Before you run the file, be sure to have a project open in Maxwell (not a design yet, just the Project folder) and have your gds file open in whatever software you prefer (you need this to give maxwell_scripter.py the relevant information).
  * Take note of the Project name in Maxwell. The script will not allow you to create a new Project, only add to one you have already created.


***Usage***

  * Now that you have the proper files and are ready to create your script, run the maxwell_scripter.py file from the cloned repo.
  * Upon running the file, you will be prompted a series of questions.
    * Pick a name for the script you will create.
    * Paste the full path to your gds file.
    * Type in the name of the Project that is already created in MAXWELL (be sure not to pick a new name here, only one from an already existent and open Project).
    * Name your design. Name can be any combination of alphanumeric characters and underscores. Be sure you have created a new name for the project, if the name already exists within the Project, the script will throw an error.
    * Tell the scripter which mode of MAXWELL you are using. There are six available modes: Magnetostatic, Eddy Current, Magnetic Transient, Electrostatic, DC Conduction, and Electric Transient. For almost all purposes, only Magnetostatic and electrostatic mode will be used. In general, use Magnetostatic for inductive measurements and Electrostatic for conductive measurements.
    * Denote the layers you would like to insert from the gds filed provided (delimited by spaces).
    * At this point, if you have told the scripter to import files it does not have information on (thickness and height specifically) it will prompt you to insert that information now. Do so in the format '250nm 1.6um' for example (it will default to mm if no units are given).
    * Now, you will be prompted for the number of disjoint components in each layers. You will be asked layer by layer, hit enter after each.
    * At this point, the script has been created and can be found in the cloned repo.

***Final Steps***

  * In MAXWELL, under the 'Automation' tab, click 'Run Script' and then select the file you just created. 
  * MAXWELL will now begin running your script piece by piece. It will first import your design file and then go through each component, assigning it the appropriate material and positioning it as defined by the layer convention.
  * Once the script has finished running, you have the 3D model fully created for you simulation, but you still must follow the correct setup up procedure explained within the inductance and capacitance MAXWELL pages. 
  * MAXWELL will not know to unite objects that, despite being a single object, were imported as disjoint objects. Be sure to connect all adjacent pieces and appropriate air bridges so they become a single entity. Do so by selecting all the desired objects and clicking 'Unite' in the 'Draw' menu. 
  * Sometimes MAXWELL will unassign materials after this procedure, so be sure to keep an eye out for this. All united objects must be of the same material.
