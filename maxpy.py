import datetime as t
import os



class Maxwell():

    def __init__(self, fileName, project, design, gds, clear=False, mode = 'Electrostatic'):
        self.gds = gds  # name of gds file to import
        self.mode = mode  # mode for maxwell simulation, defaults to 'Electrostatic' for capacitance measurements
        self.fileName = fileName  # file to write script to
        self.project = project  # name of project
        self.design = design  # name of design
        self.signalCount = 1  # counter for signal naming
        self.signals = {}  # dict going from layer to all signals in that layer
        self.allSignals = []  # list for convenience of every signal
        self.layerGuide={ 
                        5: ('0', '250nm'), #format~ layer: (height, thickness), follows LL standards
                        18: ('0', '250nm'), 
                        11: ('250nm', '250nm'),
                        30: ('250nm', '1.6um'), 
                        31: ('1850nm', '250nm')
                        }

        if clear:
            open(self.fileName, 'w').close()  # clears file 
    
        

    def initialize(self):
        """
        writes the header of the written script
        info for what and when it was written
        also initial imports and object creation that maxwell uses
        """
        with open(self.fileName, 'a') as script:
            td = str(t.datetime.now())  # gets current time info
            time = td[td.index(' ')+1 : td.index('.')]  # picks out the current time
            date = td[ : td.index(' ')]  # picks out the current data

            # necessary imports and header prints
            script.write(f'''
            # ----------------------------------------------
            # Script written by maxpy Version 1.3
            # {time} {date}
            # ----------------------------------------------\n\n''')
            script.write('import ScriptEnv\n')
            script.write('ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")\n')
            script.write('oDesktop.RestoreWindow()\n')
            script.write('oProject = oDesktop.NewProject()\n')
            script.write('oProject.Rename("' + os.getcwd().replace('\\', '\\\\') + '\\\\' + self.project + '.aedt", True)\n')
            script.write(f'oProject.InsertDesign("Maxwell 3D", "{self.design}", "{self.mode}", "")\n')
            script.write(f'oDesign = oProject.SetActiveDesign("{self.design}")\n')
            script.write('oEditor = oDesign.SetActiveEditor("3D Modeler")\n')
            

    def addLayers(self, layerDict):
        """
        tells maxwell whichi layers from the input you would like to import
        layerDict - dictionary of form {layer: elements} where elements is the number of discrete elements in each layer
        """
        for layer in layerDict:
            for signal in range(layerDict[layer]):
                self.allSignals.append(f'Signal{str(layer)}_{str(self.signalCount)}')
                if layer in self.signals:
                    self.signals[layer].append(f'Signal{str(layer)}_{str(self.signalCount)}')
                else:
                    self.signals[layer] = [f'Signal{str(layer)}_{str(self.signalCount)}']
                self.signalCount += 1

    def addLayerInfo(self, info):
        """
        used for adding information to the layer guide for layers that may not be standard
        info - list of new layers to add in format: (layer (int), height (str), thickness (str))
        """ 
        if type(info) == tuple:
            info = [info]
        for layer, height, thickness in info:
            self.layerGuide[layer] = (height, thickness)

    def importGDS(self):
        """
        imports desired layers into the maxwell 3D design
        """
        layerInput = ''
        orderInput = '['
        counter = 0

        # formats all structures as necessary
        for layer in self.signals:
            nextInput = f'''
                    [
                        "NAME:LayerMapInfo",
                        "LayerNum:="		,   {str(layer)},
                        "DestLayer:="		,   "Signal{str(layer)}",
                        "layer_type:="		,   "signal"
                    ]
                    '''
            layerInput += ', ' + nextInput

            nextOrder = f'''"entry:=", ["order:=", {str(counter)}, "layer:=", "Signal{str(layer)}"], '''
            orderInput += nextOrder
            counter += 1

        # final small touches    
        layerInput += ']'
        orderInput = orderInput.rstrip(', ')
        orderInput += ']'

        #now puts into string with corrent format we constructed earlier
        importInfo = f'''[
            "NAME:options",
            "FileName:="		, "''' + self.gds.replace('\\', '\\\\') + f'''",
            "FlattenHierarchy:="	, True,
            "ImportMethod:="	, 1,
            [
                "NAME:LayerMap"{layerInput},
            "OrderMap:="		, {orderInput}

        ]'''

        # now write to our file
        with open(self.fileName, 'a') as script:
            script.write('oEditor.ImportGDSII(\n      ' + importInfo + ')\n')

        # move the model to the origin, thickens, assigns materials, and moves to correct height
        self.zero()
        for layer in self.signals:
            self.thicken(self.signals[layer], self.layerGuide[layer][1])
            self.move(self.signals[layer], ['0','0', self.layerGuide[layer][0]])
        self.assignMaterial(self.allSignals, 'Perfect Conductor')
        
            

    def zero(self):
        """
        moves the model to the origin
        """
        
        with open(self.fileName, 'a') as script:
            script.write('\nbound_box = oEditor.GetModelBoundingBox()\n')
            script.write(f'''oEditor.Move(
            [
                "NAME:Selections",
                "Selections:="		, "{','.join(self.allSignals)}",
                "NewPartsModelFlag:="	, "Model"
            ], 
            [
                "NAME:TranslateParameters",
                "TranslateVectorX:="	,  str(-1*float(bound_box[0])) + 'mm',
                "TranslateVectorY:="	,  str(-1*float(bound_box[1])) + 'mm',
                "TranslateVectorZ:="	,  str(-1*float(bound_box[2])) + 'mm'
            ])   \n''')

            script.write(f'''oEditor.CreateBox(
            [
                "NAME:BoxParameters",
                "XPosition:="		, "0",
                "YPosition:="		, "0",
                "ZPosition:="		, "0",
                "XSize:="		,  str(float(bound_box[3])-float(bound_box[0])) + 'mm' ,
                "YSize:="		,  str(float(bound_box[4])-float(bound_box[1])) + 'mm',
                "ZSize:="		, "-350um"
            ], 
            [
                "NAME:Attributes",
                "Name:="		, "substrate",
                "Flags:="		, "",
                "Color:="		, "(143 175 143)",
                "Transparency:="	, 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\\"{'silicon'}\\"",
                "SurfaceMaterialValue:=", "\\"\\"",
                "SolveInside:="		, True,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="	, False
            ])
            \n''')
        
    def thicken(self, signals, thickness):
        '''
        thickens each of the signals by the desired thickness
        '''
        with open(self.fileName, 'a') as script:
            script.write(f'''oEditor.ThickenSheet(
            [
                "NAME:Selections",
                "Selections:="		, "{','.join(signals)}",
                "NewPartsModelFlag:="	, "Model"
            ], 
            [
                "NAME:SheetThickenParameters",
                "Thickness:="		, "{thickness}",
                "BothSides:="		, False
            ])\n''')

    def move(self, signals, vector):
        """
        moves each of the signals in signals up by vector: both are lists of strings
        """
        if ['0']*3 == vector:
            return -1
        moveInfo = f'''["NAME:Selections",
            "Selections:="		,   "{','.join(signals)}",
            "NewPartsModelFlag:="	       , "Model"
            ],
            [
            "NAME:TranslateParameters",
                "TranslateVectorX:="	, "{vector[0]}",
                "TranslateVectorY:="	, "{vector[1]}",
                "TranslateVectorZ:="	, "{vector[2]}"
        ]'''

        with open(self.fileName, 'a') as script:
            script.write('oEditor.Move(\n         ' + moveInfo + ')\n')


    def assignMaterial(self, signals, material):
        """
        assigns material to every signal in list signals
        """
        with open(self.fileName, 'a') as script:
            script.write(f'''oEditor.AssignMaterial(
            [
                "NAME:Selections",
                "AllowRegionDependentPartSelectionForPMLCreation:=", True,
                "AllowRegionSelectionForPMLCreation:=", True,
                "Selections:="		, "{','.join(signals)}"
            ], 
            [
                "NAME:Attributes",
                "MaterialValue:="	, "\\"{material}\\"",
                "SolveInside:="		, False,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="	, False
            ])\n''')


    def unite(self, signals):
        """
        unites every element in signals
        """
        with open(self.fileName, 'a') as script:
            script.write(f'''oEditor.Unite(
	        [
		        "NAME:Selections",
		        "Selections:="		, "{','.join(signals)}"
            ], 
            [
                "NAME:UniteParameters",
                "KeepOriginals:="	, False
            ])
            \n''')

    def voltage(self, v, signal, name ):
        """ 
        assigns voltage to signal with name for excitations
        """
        with open(self.fileName, 'a') as script:
            script.write('oModule = oDesign.GetModule("BoundarySetup")\n')
            script.write(f'''oModule.AssignVoltage(
	[
		"NAME:{name}",
		"Objects:="		, ["{signal}"],
		"Voltage:="		, "{v}",
		"CoordinateSystem:="	, ""
	])
            \n''') 

    def rename(self, signal, name):
        """
        renames one signal with given name
        """
        with open(self.fileName, 'a') as script:
            script.write(f'''oEditor.ChangeProperty(
	        [
		"NAME:AllTabs",
		[
			"NAME:Geometry3DAttributeTab",
			[
				"NAME:PropServers", 
				"{signal}"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:Name",
					"Value:="		, "{name}"
				]
			]
		]
	])
            \n''')

    def problemRegion(self, height=300):
        """
        makes a problem region with the given height, defaults ot 300
        """

        with open(self.fileName, 'a') as script:
            script.write(f'''oEditor.CreateRegion(
	[
		"NAME:RegionParameters",
		"+XPaddingType:="	, "Percentage Offset",
		"+XPadding:="		, "0",
		"-XPaddingType:="	, "Percentage Offset",
		"-XPadding:="		, "0",
		"+YPaddingType:="	, "Percentage Offset",
		"+YPadding:="		, "0",
		"-YPaddingType:="	, "Percentage Offset",
		"-YPadding:="		, "0",
		"+ZPaddingType:="	, "Percentage Offset",
		"+ZPadding:="		, "{str(height)}",
		"-ZPaddingType:="	, "Percentage Offset",
		"-ZPadding:="		, "0"
	], 
	[
		"NAME:Attributes",
		"Name:="		, "Region",
		"Flags:="		, "Wireframe#",
		"Color:="		, "(143 175 143)",
		"Transparency:="	, 0,
		"PartCoordinateSystem:=", "Global",
		"UDMId:="		, "",
		"MaterialValue:="	, "\\"vacuum\\"",
		"SurfaceMaterialValue:=", "\\"\\"",
		"SolveInside:="		, True,
		"IsMaterialEditable:="	, True,
		"UseMaterialAppearance:=", False,
		"IsLightweight:="	, False
	])
            \n''')

    
    def matrix(self, excitations, name):
        """
        given a list of excitation names we would like to include, set up the capacitance matrix simulation, naming the matrix with name
        """
        entries = ''
        for each in excitations:
            entries += f'''              [
                "NAME:MatrixEntry",
                "Source:="		, "{each}",
                "NumberOfTurns:="	, "1"
            ],\n'''

        with open(self.fileName, 'a') as script:
            script.write('oModule = oDesign.GetModule("MaxwellParameterSetup")\n')
            script.write(f'''oModule.AssignMatrix(
        [
            "NAME:{name}",
            [
                "NAME:MatrixEntry",
                ''' + entries.rstrip(',\n') + '''
            ],
            [
                "NAME:MatrixGroup"
            ]
        ])
            \n''')
    
    def setup(self, name, minPass=2, maxPass=15, error=2):
        """
        does the setup so we can analyze the file
        """
        with open(self.fileName, 'a') as script:
            script.write('oModule = oDesign.GetModule("AnalysisSetup")\n')
            script.write(f'''oModule.InsertSetup("{self.mode}",
            [
		"NAME:{name}",
		"Enabled:="		, True,
		"MaximumPasses:="	, {str(maxPass)},
		"MinimumPasses:="	, {str(minPass)},
		"MinimumConvergedPasses:=", 1,
		"PercentRefinement:="	, 30,
		"SolveFieldOnly:="	, False,
		"PercentError:="	, {str(error)},
		"SolveMatrixAtLast:="	, True,
		"PercentError:="	, {str(error)},
		"UseIterativeSolver:="	, False,
		"RelativeResidual:="	, 1E-06,
		"NonLinearResidual:="	, 0.001
	])
 
            \n''')

    def analyze(self, setup, matrix, loc):
        with open(self.fileName, 'a') as script:
            script.write('oProject.Save()\n')
            script.write(f'oDesign.Analyze("{setup}")\n')
            script.write(f'oModule = oDesign.GetModule("AnalysisSetup")\n')
            script.write(f'''oModule.ExportSolnData("{setup} : LastAdaptive", "{matrix}", False, "", "{loc}")\n''')


class maxParse():

    def __init__(self, fileName):
        self.fileName = None
        self.units = None
        self.capacitance = {}
        self.coupling = {}
        self.update(fileName)

    def update(self, fileName):
        self.fileName = fileName
        with open(fileName, 'r') as output:
            data = output.read()
        data = data.split('\n')
        self.units = data[2][data[2].index(':')+2:]
        excitations = data[5].lstrip('\t').split('\t')
        for index in range(len(excitations)):
            rowcap = data[6+index].lstrip('\t').split('\t')
            rowcoup = data[9+len(excitations)+index].lstrip('\t').split('\t')
            newcap = {}
            newcoup = {}
            for col in range(len(excitations)):
                newcap[excitations[col]] = rowcap[1+col]
                newcoup[excitations[col]] = rowcoup[1+col]

            self.capacitance[excitations[index]] = newcap
            self.coupling[excitations[index]] = newcoup

    

