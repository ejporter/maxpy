
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# NOTE: This script will only get you so far in your simulation, some steps are still required
#
#           1: Unite all objects that should be connected and/or form a conduction path.
#           2: Define excitations appropriately.
#           3: Set up parameters and analysis for your specific needs.
#           4: validate and run simulation.
#
#   This script will not do the above and must be done by the user.
#   Information about how to do so can be found on the Maxwell page of the EQuS WIKI: https://sebastians/dokuwiki/doku.php?id=maxwell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


from Maxwell_Editor import *
import datetime as t

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# prompts user for necessary info to create the write Maxwell setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


write_to = input("Name your script file (e.g. test_script):  ")

file_name = input("Full path to your gds file? ")
file_name = file_name.replace('\\', '/')  # fixes slashes in file name that causes errors when writing to new file

project = input("What is your project name:  ")
while ' ' in project:
    print('Invalid Name!')
    project = input("What is your project name:  ")

design = input('What is your design name:  ')
while ' ' in design:
    print('Invalid Name!')
    design = input("What is your design name:  ")

mode = input("What mode of Maxwell are you using (Magnetostatic or Electrostatic):  ")
while mode not in ['Magnetostatic', 'Electrostatic']:
    print('Invalid Mode!')
    mode = input("What mode of Maxwell are you using (Magnetostatic or Electrostatic):  ")


with open(write_to, 'w') as sf:  # creates new script file

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # time/version info for creating header
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    td = str(t.datetime.now())
    time = td[td.index(' ')+1:td.index('.')]
    date = td[:td.index(' ')]
    sf.write('''# ----------------------------------------------\n''')
    sf.write('''# Script Written by maxwell_scripter.py Version 1.0 \n''')
    sf.write('''# ''' + time + ' ' + date + '''\n''')
    sf.write('''# ----------------------------------------------\n''')


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # initial imports, creating a new design file, and setting active objects
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    sf.write('import ScriptEnv\nScriptEnv.Initialize("Ansoft.ElectronicsDesktop")\noDesktop.RestoreWindow()\n')
    sf.write('oProject = oDesktop.SetActiveProject("' + project + '")\n')
    sf.write('oProject.InsertDesign("Maxwell 3D", "' + design + '", "' + mode +'", "")\n')
    sf.write('oDesign = oProject.SetActiveDesign("' + design + '")\n')
    sf.write('oEditor = oDesign.SetActiveEditor("3D Modeler")\n')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # gathers info on the gds file and puts in the correct format
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    layers = input('Which layers would you like to import (e.g. 18 30 31):  ')
    layers = layers.split(' ')

    extra_info = []  # certain layers have conventions predefined and stored in the Maxwell_Editor class, but if not, prompt user for their desired specs for that layer

    if len(list(set(layers) & {'5', '11', '18', '30', '31'})) != len(layers):  # if there are layers undefine, the intersection will be smaller
        print('\nSome of the layers you are importing do not have defined conventions, please do so now. (e.g. 250nm 1.6um)\n')
        for each in layers:
            if each not in ['5', '11', '18', '30', '31']:
                info = input('Height and thickness of ' + each + ':  ')
                info = info.split(' ')
                extra_info.append((each, info[0], info[1]))  # put in correct format and the stores within extra_info list to later add into the Maxwell_Editor object created

    print('\nHow many components are in each of the layers?')  # Maxwell needs to know the number of distinct object in each layer to appropriately name the signals for later reference
    for layer in layers:
        comp = input(layer + ':  ')
        layers[layers.index(layer)] = (layer, comp)  # puts the layers in the format Maxwell_Editor needs

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # creates Maxwell_Editor object, imports gds file given, and edits layers according to conventions and given specs
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    maxwell = Maxwell_Editor(layers)
    sf.write(maxwell.import_layers(file_name))
    
    sf.write('\nbound_box = oEditor.GetModelBoundingBox()\n')
    sf.write(maxwell.zero() + '\n')  # ensures model is placed at the origin

    if extra_info != []:
        maxwell.add_conventions(extra_info)  # adds in conventions if any were specified

    for layer, comp in maxwell.layers: # goes through each layer, thickening and moving into place
        thickness = maxwell.layer_info[layer][1]
        height =  maxwell.layer_info[layer][0]
        sf.write(maxwell.thicken(thickness, maxwell.signals[layer]))
        if height != '0':
            sf.write(maxwell.move("0mm", "0mm", height, sig = maxwell.signals[layer]))

    sf.write(maxwell.assign_material("perfect conductor", all = True))

    sf.write('bound_box = oEditor.GetModelBoundingBox()\n')  # makes new bound box on the model, required for the correct spacing of the substrate and vacuum layers

    # makes vacuum, substrate, and problem region for the final model
    sf.write(maxwell.make_substrate())
    sf.write(maxwell.make_vacuum())
    sf.write(maxwell.subtract())
    sf.write(maxwell.make_region())
