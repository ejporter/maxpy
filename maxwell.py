import datetime as t
import os







#====================================================================================================================
"""
    Master class for handling all of the other classes so that it is able to create a more modular 
    environment. Will contain the lower level classes and write to the text file as needed.
"""   
#-------------------------------------------------------------------------------------------------------------------


class Maxwell():

    def __init__(self, fileName):
        self.gds = None
        self.mode = "Magnetostatic"
        self.fileName = fileName + '.py'

        # other classes for handling the actual writing
        self.initializer = MaxInit(self.fileName)
        self.sim = MaxSim()
        self.geometry = MaxGeo(self.fileName)
        self.setup = MaxSetup(self.fileName)
        self.firstLines()

        

        #handling for importing the right layers
        self.layerCount = 1

        self.signals = {}  # dict going from layer to all signals in that layer
        self.allSignals = []  # list for convenience



    def setGDS(self, fileName):
        self.gds = fileName + '.gds'

    def setFile(self, fileName):
        self.fileName = fileName + '.py'

    def setMode(self, mode):
        self.mode = mode

    def firstLines(self):
        
        self.initializer.get_creation_info()
        self.initializer.initial_text()

    def setProject(self, projectName):
        self.initializer.renameProject(projectName)


    def insertDesign(self, designName):
        self.initializer.openDesign(designName, mode=self.mode)

    def setDesign(self, designName):
        if self.initializer.designName is None:
            self.initializer.openDesign(designName, mode=self.mode)
        else:
            self.initializer.setDesign(designName)

    def importGDS(self, importgds=None):
        importgds = self.gds
        assert importgds is not None, 'No GDS file specified'
        self.setup.importGDS(importgds)

    def GDSLayers(self, info):
        for layer, num in info:
            self.signals[layer] = []
            for i in range(num):
                name = 'Signal'+str(layer)+'_'+str(self.layerCount)
                self.signals[layer].append(name)
                self.allSignals.append(name)
                self.layerCount += 1
        self.setup.allSignals = self.allSignals
        self.setup.setSignals(self.signals)

    def addLayerInfo(self, info):  # format: list of tuples in form (layer (int), height (str), thickness (str))
        for layer, height, thickness in info:
            self.layerGuide[layer] = (height, thickness)

    
    def prepare(self):
        """
         This class is for the prepartion of your GDS file. It will thicken layers, move them accordingly, and assign materials
        """

        self.setup.zero()
        self.setup.initialThicken(self.signals, self.geometry)
        self.setup.position(self.signals, self.geometry)
        self.setup.initialAssign(self.signals, self.geometry)
    





#====================================================================================================================
"""
    The only thing this class does is write the initialization procedure for a maxwell script. Things
    like setting active windows, renaming projects, setting mode, etc.
"""   
#-------------------------------------------------------------------------------------------------------------------



class MaxInit():

    def __init__(self, fileName):
        self.projectName = "Project1"
        self.designName = None
        self.mode = "Magnetostatic"  """ options are:
                                Magnetostatic, Electrostatic, EddyCurrent,
                                Transient, DCConduction, ElectricTransient"""
        self.fileName = fileName


    def get_creation_info(self):
        """
        Writes header info for the script
        """
        with open(self.fileName, 'a') as script:
            td = str(t.datetime.now())  # gets current time info
            time = td[td.index(' ')+1 : td.index('.')]  # picks out the current time
            date = td[ : td.index(' ')]  # picks out the current data
            script.write('''
            # ----------------------------------------------
            # Script written by maxpy Version 2.0
            # ''' + time + ' ' + date + '''
            # ----------------------------------------------\n\n''')

    def initial_text(self):
        """
        Write first few lines of necessary info
        """
        with open(self.fileName, 'a') as script:
            script.write('import ScriptEnv\n')
            script.write('ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")\n')
            script.write('oDesktop.RestoreWindow()\n')
            script.write('oProject = oDesktop.SetActiveProject("Project1")\n')

    def renameProject(self, projectName):
        self.projectName = projectName
        with open(self.fileName, 'a') as script:
            script.write('oProject.Rename("' + os.getcwd().replace('\\', '\\\\') + '\\\\' + self.projectName + '.aedt", True)\n')  

    def openDesign(self, designName, mode):
        self.designName = designName
        with open(self.fileName, 'a') as script:
            script.write('oProject.InsertDesign("Maxwell 3D", "'+ designName + '", "' + mode + '", "")\n')
            script.write('oDesign = oProject.SetActiveDesign("' + designName + '")\n')
            script.write('oEditor = oDesign.SetActiveEditor("3D Modeler")\n')

    def setDesign(self, designName):
        self.designName = designName
        with open(self.fileName, 'a') as script:
            script.write('oDesign = oProject.SetActiveDesign("' + designName + '")\n')
            script.write('oEditor = oDesign.SetActiveEditor("3D Modeler")\n')


   
        


#====================================================================================================================
"""
    This class will be used for importing gds files, centering to zero, handling standard layer
    info, assigning materials, etc. Will have to handle element names
"""   
#-------------------------------------------------------------------------------------------------------------------


class MaxSetup():

    def __init__(self, fileName):
        self.signals = None
        self.allSignals = None
        self.layerGuide={ 
                        5: ('0', '250nm'), #format~ layer: (height, thickness)
                        18: ('0', '250nm'), 
                        11: ('250nm', '250nm'),
                        30: ('250nm', '1.6um'), 
                        31: ('1850nm', '250nm')
                        }
        self.fileName = fileName
    
    def setSignals(self, signals):
        self.signals = signals

    def importGDS(self, gdsfile):
        """
        imports desired layers into the maxwell 3D design
        """
        layerInput = ''
        orderInput = '['
        counter = 0

        # formats all structures as necessary
        for layer in self.signals:
            nextInput = '''
                    [
                        "NAME:LayerMapInfo",
                        "LayerNum:="		,   '''  + str(layer) + ''',
                        "DestLayer:="		,   "Signal''' + str(layer) + '''",
                        "layer_type:="		,   "signal"
                    ]
                    '''
            layerInput += ', ' + nextInput

            nextOrder = '''"entry:=", ["order:=", ''' + str(counter) + ''', "layer:=", "Signal''' + str(layer) + '''"], '''
            orderInput += nextOrder
            counter += 1

        # final small touches    
        layerInput += ']'
        orderInput = orderInput.rstrip(', ')
        orderInput += ']'

        #now puts into string with corrent format we constructed earlier
        importInfo = '''[
            "NAME:options",
            "FileName:="		, "''' + gdsfile.replace('\\', '\\\\') + '''",
            "FlattenHierarchy:="	, True,
            "ImportMethod:="	, 1,
            [
                "NAME:LayerMap"''' + layerInput + ''',
            "OrderMap:="		, ''' + orderInput + '''

        ]'''

        # now write to our file
        with open(self.fileName, 'a') as script:
            script.write('oEditor.ImportGDSII(\n      ' + importInfo + ')\n')

    def zero(self):
        """
        moves the model to the origin if it is not already
        """
        
        with open(self.fileName, 'a') as script:
            script.write('\nbound_box = oEditor.GetModelBoundingBox()\n')
            script.write('''oEditor.Move(
            [
                "NAME:Selections",
                "Selections:="		, "''' + ','.join(self.allSignals) + '''",
                "NewPartsModelFlag:="	, "Model"
            ], 
            [
                "NAME:TranslateParameters",
                "TranslateVectorX:="	,  str(-1*float(bound_box[0])) + 'mm',
                "TranslateVectorY:="	,  str(-1*float(bound_box[1])) + 'mm',
                "TranslateVectorZ:="	,  str(-1*float(bound_box[2])) + 'mm'
            ])   \n''')

    def position(self, signals, geohandler):
        for layer in signals:
            geohandler.move(signals[layer], ['0','0', self.layerGuide[layer][0]])


    def initialThicken(self, signals, geohandler):
        for layer in signals:
            geohandler.thicken(signals[layer], self.layerGuide[layer][1])

    def initialAssign(self, signals, geohandler):
        allSignals = [item for sublist in [j for j in signals.values()] for item in sublist]
        geohandler.assignMaterial(allSignals, 'perfect conductor')






#====================================================================================================================
"""
    This class has the primary goal of handling all of the geometric needs for a maxwell script
    It handles things such as moving object, drawing new objects, assigning excitations and 
    boundary conditions, etc. Most of it will be based off of coordinate position, but it should
    have basic knowledge of element name so that it will be able to refer to things via name.
"""   
#------------------------------------------------------------------------------------------------------------------


class MaxGeo():

    def __init__(self, fileName):
        self.fileName = fileName

    def move(self, signals, vector):
        """
        moves each of the signals in signals up by vector: both are lists of strings
        """
        if ['0']*3 == vector:
            return -1
        moveInfo = '''["NAME:Selections",
            "Selections:="		,   "''' + ','.join(signals) + '''",
            "NewPartsModelFlag:="	       , "Model"
            ],
            [
            "NAME:TranslateParameters",
                "TranslateVectorX:="	, "''' + vector[0] + '''",
                "TranslateVectorY:="	, "''' +  vector[1] + '''",
                "TranslateVectorZ:="	, "''' + vector[2] +'''"
        ]'''

        with open(self.fileName, 'a') as script:
            script.write('oEditor.Move(\n         ' + moveInfo + ')\n')

    def thicken(self, signals, thickness):
        '''
        thickens each of the signals by the desired thickness
        '''
        with open(self.fileName, 'a') as script:
            script.write('''oEditor.ThickenSheet(
            [
                "NAME:Selections",
                "Selections:="		, "''' + ','.join(signals) + '''",
                "NewPartsModelFlag:="	, "Model"
            ], 
            [
                "NAME:SheetThickenParameters",
                "Thickness:="		, "''' +  thickness + '''",
                "BothSides:="		, False
            ])\n''')

    def assignMaterial(self, signals, material):
        with open(self.fileName, 'a') as script:
            script.write('''oEditor.AssignMaterial(
            [
                "NAME:Selections",
                "AllowRegionDependentPartSelectionForPMLCreation:=", True,
                "AllowRegionSelectionForPMLCreation:=", True,
                "Selections:="		, "''' + ','.join(signals) + '''"
            ], 
            [
                "NAME:Attributes",
                "MaterialValue:="	, "''' + '\\' + '''"''' + material + '\\' + '''"",
                "SolveInside:="		, False,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="	, False
            ])\n''')




        
        



#====================================================================================================================
"""
    The primary purpose of this class is to setup the simulation for maxwell and potentially
    run the file to get results as well. 
"""   
#-------------------------------------------------------------------------------------------------------------------

class MaxSim():


    def __init__(self):
        pass 


