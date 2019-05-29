# ---------------------------------------------------------------------------------------------------------
# imports
# ---------------------------------------------------------------------------------------------------------
from maxpy import maxwell
import os



# ---------------------------------------------------------------------------------------------------------
# project initialization
# ---------------------------------------------------------------------------------------------------------
mw = maxwell.Maxwell('MutualInductanceScript', clear=True)  # initializes the maxwell handler object
mw.setMode('Magnetostatic')  # sets mode to magnetostatic for mutual inductance measurements
mw.setProject('MutualInductance')  # switches projects or creates a new one if does not exist already
mw.setDesign('Example')  # switches design within project or creates a new one if does not exist already
mw.setGDS('crossTalkSim')  # name of the GDS file to import
mw.GDSLayers([(5, 5 ), (11, 2), (30, 34), (31, 17)])  # sets the number of elements in each GDS layer
mw.importGDS() # imports the GDS file specified previously with the layers given
mw.prepare()  # centers the design, thickens sheets, moves into place, and assigns materials




# ---------------------------------------------------------------------------------------------------------
# boundary conditions
# ---------------------------------------------------------------------------------------------------------


mw.unite(['Signal11_6', 'Signal5_3', 'Signal5_5'])  # unites the given signals, keeping the name of the first one
mw.unite(['Signal11_7', 'Signal5_4', 'Signal5_2'])
mw.insulate('Signal11_7', 'Insulating1')  # assigns boundary condition 'insulating' to given signal
mw.insulate('Signal11_6', 'Insulating2')
mw.region([0, 200, 200, 0, 300, 300])


# ---------------------------------------------------------------------------------------------------------
# simulation setup
# ---------------------------------------------------------------------------------------------------------

mw.simulate(maxPasses=20, error=2)  # simulation setup. to see full kwrd arguements see maxwell.py



print(mw.fileName + ' has been written to ' + os.getcwd())



