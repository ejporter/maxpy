import datetime as t
import os







#====================================================================================================================
"""
    Master class for handling all of the other classes so that it is able to create a more modular 
    environment. Will contain the lower level classes and write to the text file as needed.
"""   
#-------------------------------------------------------------------------------------------------------------------


class Maxwell():

    def __init__(self, fileName, project, design, gds, clear=False, mode = 'Electrostatic'):
        self.gds = gds
        self.mode = mode
        self.fileName = fileName
        self.project = project
        self.design = design
        self.signals = None
        self.signalCount = 1
        self.signals = {}  # dict going from layer to all signals in that layer
        self.allSignals = []  # list for convenience
        self.layerGuide={ 
                        5: ('0', '250nm'), #format~ layer: (height, thickness)
                        18: ('0', '250nm'), 
                        11: ('250nm', '250nm'),
                        30: ('250nm', '1.6um'), 
                        31: ('1850nm', '250nm')
                        }

        if clear:
            open(self.fileName, 'w').close()  # clears file 
    
        

    def initialize(self):
        with open(self.fileName, 'a') as script:
            td = str(t.datetime.now())  # gets current time info
            time = td[td.index(' ')+1 : td.index('.')]  # picks out the current time
            date = td[ : td.index(' ')]  # picks out the current data
            script.write('''
            # ----------------------------------------------
            # Script written by maxpy Version 2.0
            # ''' + time + ' ' + date + '''
            # ----------------------------------------------\n\n''')
            script.write('import ScriptEnv\n')
            script.write('ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")\n')
            script.write('oDesktop.RestoreWindow()\n')
            script.write('oProject = oDesktop.NewProject()\n')
            script.write('oProject.Rename("' + os.getcwd().replace('\\', '\\\\') + '\\\\' + self.project + '.aedt", True)\n')
            script.write(f'oProject.InsertDesign("Maxwell 3D", "{self.design}", "{self.mode}", "")\n')
            script.write(f'oDesign = oProject.SetActiveDesign("{self.design}")\n')
            script.write('oEditor = oDesign.SetActiveEditor("3D Modeler")\n')
            

    def add_layers(self, layerDict):
        for layer in layerDict:
            for signal in range(layerDict[layer]):
                self.allSignals.append(f'Signal{str(layer)}_{str(self.signalCount)}')
                if layer in self.signals:
                    self.signals[layer].append(f'Signal{str(layer)}_{str(self.signalCount)}')
                else:
                    self.signals[layer] = [f'Signal{str(layer)}_{str(self.signalCount)}']
                self.signalCount += 1

    def addLayerInfo(self, info):  # format: list of tuples in form (layer (int), height (str), thickness (str))
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


        self.zero()
        for layer in self.signals:
            self.thicken(self.signals[layer], self.layerGuide[layer][1])
            self.move(self.signals[layer], ['0','0', self.layerGuide[layer][0]])
        self.assignMaterial(self.allSignals, 'Perfect Conductor')
        
            

    def zero(self):
        """
        moves the model to the origin if it is not already
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

        
            

        
















       


   


    


#     def simulate(self, name = 'Setup1', maxPasses=15, error=1, minPasses=2, percentRefinement=30, SolveMatrixAtLast=True, UseIterativeSolve=False, RelativeResidual = 1E-06, NonLinearResidual = 0.001):
#         self.sim.setup(name, self.mode, maxPasses, error, minPasses, percentRefinement=30, SolveMatrixAtLast=True, UseIterativeSolve=False, RelativeResidual = 1E-06, NonLinearResidual = 0.001)
    

#     def unite(self, signals):
#         self.geometry.unite(signals)

#     def box(self, pos, size, name, material='vacuum'):
#         self.geometry.box(pos, size, name, material)

#     def region(self, lengths, material='vacuum'):
#         self.geometry.region(lengths, material)






# #====================================================================================================================
# """
#     This class has the primary goal of handling all of the geometric needs for a maxwell script
#     It handles things such as moving object, drawing new objects, assigning excitations and 
#     boundary conditions, etc. Most of it will be based off of coordinate position, but it should
#     have basic knowledge of element name so that it will be able to refer to things via name.
# """   
# #------------------------------------------------------------------------------------------------------------------


# class MaxGeo():

#     def __init__(self, fileName):

#     def unite(self, signals):
#         with open(self.fileName, 'a') as script:
#             script.write('''oEditor.Unite(
# 	        [
# 		        "NAME:Selections",
# 		        "Selections:="		, "''' + ','.join(signals) + '''"
#             ], 
#             [
#                 "NAME:UniteParameters",
#                 "KeepOriginals:="	, False
#             ])
#             \n''')

#     def box(self,pos, size, name, material):
        
#         with open(self.fileName, 'a') as script:
#             script.write('''oEditor.CreateBox(
#             [
#                 "NAME:BoxParameters",
#                 "XPosition:="		, "''' + str(pos[0]) + '''",
#                 "YPosition:="		, "''' + str(pos[1]) + '''",
#                 "ZPosition:="		, "''' + str(pos[2]) + '''",
#                 "XSize:="		, "''' + str(size[0]) + '''",
#                 "YSize:="		, "''' + str(size[1]) + '''",
#                 "ZSize:="		, "''' + str(size[2]) + '''"
#             ], 
#             [
#                 "NAME:Attributes",
#                 "Name:="		, "''' + name + '''",
#                 "Flags:="		, "",
#                 "Color:="		, "(143 175 143)",
#                 "Transparency:="	, 0,
#                 "PartCoordinateSystem:=", "Global",
#                 "UDMId:="		, "",
#                 "MaterialValue:="	, "''' + '\\' + '''"''' +material + '\\' + '''"",
#                 "SurfaceMaterialValue:=", "\\"\\"",
#                 "SolveInside:="		, True,
#                 "IsMaterialEditable:="	, True,
#                 "UseMaterialAppearance:=", False,
#                 "IsLightweight:="	, False
#             ])
#             \n''')

#     def region(self, lengths, material):
#         for i in range(len(lengths)):
#             lengths[i] = str(lengths[i])
        
#         with open(self.fileName, 'a') as script:
#             script.write('''oEditor.CreateRegion(
#             [
#                 "NAME:RegionParameters",
#                 "+XPaddingType:="	, "Percentage Offset",
#                 "+XPadding:="		, "'''+lengths[0] + '''",
#                 "-XPaddingType:="	, "Percentage Offset",
#                 "-XPadding:="		, "'''+lengths[1] + '''",
#                 "+YPaddingType:="	, "Percentage Offset",
#                 "+YPadding:="		, "'''+lengths[2] + '''",
#                 "-YPaddingType:="	, "Percentage Offset",
#                 "-YPadding:="		, "'''+lengths[3] + '''",
#                 "+ZPaddingType:="	, "Percentage Offset",
#                 "+ZPadding:="		, "'''+lengths[4] + '''",
#                 "-ZPaddingType:="	, "Percentage Offset",
#                 "-ZPadding:="		, "'''+lengths[5] + '''"
#             ], 
#             [
#                 "NAME:Attributes",
#                 "Name:="		, "Region",
#                 "Flags:="		, "Wireframe#",
#                 "Color:="		, "(143 175 143)",
#                 "Transparency:="	, 1,
#                 "PartCoordinateSystem:=", "Global",
#                 "UDMId:="		, "",
#                 "MaterialValue:="	, "''' + '\\' + '''"''' + str(material) + '\\' + '''"",
#                 "SurfaceMaterialValue:=", "''' + '\\' + '"' + '\\' + '''"",
#                 "SolveInside:="		, True,
#                 "IsMaterialEditable:="	, True,
#                 "UseMaterialAppearance:=", False,
#                 "IsLightweight:="	, False
#             ])\n''')

#     def current(self, name, cur, face, out):
#          with open(self.fileName, 'a') as script:
#             script.write('''oModule = oDesign.GetModule("BoundarySetup")''')
#             script.write('''oModule.AssignCurrent(
#                 [
#                     "NAME:'''+name+'''",
#                     "Faces:="		, ['''+str(face)+'''],
#                     "Current:="		, "'''+str(cur)+'''",
#                     "IsSolid:="		, True,
#                     "Point out of terminal:=", '''+str(out)+'''
#                 ])
#             \n''')

#     def insulate(self, body, name):
#         with open(self.fileName, 'a') as script:
#             script.write('''oModule.AssignInsulating(
#             [
#                 "NAME:'''+name+'''",
#                 "Objects:="		, ["'''+str(body)+'''"]
#             ])\n''')



        
        



# #====================================================================================================================
# """
#     The primary purpose of this class is to setup the simulation for maxwell and potentially
#     run the file to get results as well. 
# """   
# #-------------------------------------------------------------------------------------------------------------------

# class MaxSim():


#     def __init__(self, fileName):
#         self.fileName = fileName

#     def setup(self, name, mode, maxPasses, error, minPasses, percentRefinement, SolveMatrixAtLast, UseIterativeSolve, RelativeResidual, NonLinearResidual):
#         with open(self.fileName, 'a') as script:
#             script.write('oModule = oDesign.GetModule("AnalysisSetup")\n')
#             script.write('''oModule.InsertSetup("''' + mode +'''", 
# 	[
# 		"NAME:''' + name + '''",
# 		"Enabled:="		, True,
# 		"MaximumPasses:="	, ''' + str(maxPasses)  + ''',
# 		"MinimumPasses:="	, ''' + str(minPasses)+''',
# 		"MinimumConvergedPasses:=", 1,
# 		"PercentRefinement:="	, '''+str(percentRefinement)+''',
# 		"SolveFieldOnly:="	, False,
# 		"PercentError:="	, '''+str(error)+''',
# 		"SolveMatrixAtLast:="	, ''' + str(SolveMatrixAtLast)+''',
# 		"PercentError:="	, '''+str(error)+''',
# 		"UseIterativeSolver:="	, '''+str(UseIterativeSolve)+''',
# 		"RelativeResidual:="	, '''+str(RelativeResidual)+''',
# 		"NonLinearResidual:="	, ''' + str(NonLinearResidual) +'''
# 	])\n''')

