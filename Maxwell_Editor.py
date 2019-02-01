class Maxwell_Editor():

    def __init__(self, layers):
       
        self.layer_info =   {'5': ('0', '250nm'),  # default information about specific layer conventions. format~ layer: (height, thickness)
                            '18': ('0', '250nm'), 
                            '11': ('250nm', '250nm'),
                            '30': ('250nm', '1.6um'), 
                            '31': ('1850nm', '250nm')}

        self.layers = layers
        self.signals = {}  # dictionary of layer numbers to signals

        counter = 1  # counts upwards to keep track of the signal names
        for layer, components in self.layers:
            self.signals[layer] = []
            for _ in range(int(components)):
                self.signals[layer].append('Signal'+layer+'_'+str(counter))  # creates all of the names that Maxwell will make on import
                counter += 1

        self.all_signals = []  # list of every signal for convenience
        for elt in self.signals.values():
            self.all_signals.extend(elt)
    
    
    def add_conventions(self, extra_info):
        """used to create new layer conventions that may not already be known

            extra_info: tuple of form (layer, height, thickness). all strings
        """

        for layer, height, thickness in extra_info:
            self.layer_info[layer] = (height, thickness)  # stores new info given into layer_info dictionary


    def import_layers(self, file_name):
        """imports desired layers from .gds file into a Maxwell 3D design
        
            file: .gds file path to import 
        """
        layer_input = ''
        order_input = '['
        counter = 0

        for layer, comp in self.layers:  # forming the individual sections based on layers
            next_input = '''
                    [
                        "NAME:LayerMapInfo",
                        "LayerNum:="		,   '''  + layer + ''',
                        "DestLayer:="		,   "Signal''' + layer + '''",
                        "layer_type:="		,   "signal"
                    ]
                    '''
            layer_input += ', ' + next_input
        
            next_order = '''"entry:=", ["order:=", ''' + str(counter) + ''', "layer:=", "Signal''' + layer + '''"], '''
            order_input += next_order
            counter += 1
        layer_input += ']'
        order_input = order_input.rstrip(', ')
        order_input += ']'



        # putting together the info on file, layers, and the ordering of the layers
        import_info = '''[
            "NAME:options",
            "FileName:="		, "''' + file_name + '''",
            "FlattenHierarchy:="	, True,
            "ImportMethod:="	, 1,
            [
                "NAME:LayerMap"''' + layer_input + ''',
            "OrderMap:="		, ''' + order_input + '''

        ]'''

        return 'oEditor.ImportGDSII(\n      ' + import_info + ')'
        
    def move(self, dx, dy, dz, sig = [], all = False):
        """moves given signals by desired amount
        
            dx, dy, dz: strings representing displacement in the x, y, and z directions respectively
            unit: units of displacement, defaults to micrometers
            signals: list of signals to move, defaults to empty
            all: if entire drawing is to be moved
        """
        
        if all:
            sig = self.all_signals

        if sig != []:
            move_info = '''["NAME:Selections",
            "Selections:="		,   "''' + ','.join(sig) + '''",
            "NewPartsModelFlag:="	       , "Model"
            ],
            [
            "NAME:TranslateParameters",
                "TranslateVectorX:="	, "''' + dx + '''",
                "TranslateVectorY:="	, "''' +  dy + '''",
                "TranslateVectorZ:="	, "''' + dz +'''"
        ]'''

      
            return 'oEditor.Move(\n         ' + move_info + ')\n'  
        else:
            raise Exception('No signals given')
            
    def thicken(self, thickness, sig = [], all = False):
        """thickens 2D sheets in model, making them 3D components
        
            thickness: string, desired thickness
            signals: list of signals to thicken
            all: defaults to False, set to True to automaticall select all signals
        """
        if all:
            sig = self.all_signals
        if sig != []:    
            return '''oEditor.ThickenSheet(
            [
                "NAME:Selections",
                "Selections:="		, "''' + ','.join(sig) + '''",
                "NewPartsModelFlag:="	, "Model"
            ], 
            [
                "NAME:SheetThickenParameters",
                "Thickness:="		, "''' +  thickness + '''",
                "BothSides:="		, False
            ])\n'''
            
        else:
            raise Exception('No signals given')

    def assign_material(self, material, sig = [], all = False):
        """
        assigns material to 3D component of the model
        
        material: material to assign
        signals: list of signals to assign given material
        """
        if all:
            sig = self.all_signals

        if sig != []:    

            return '''oEditor.AssignMaterial(
            [
                "NAME:Selections",
                "AllowRegionDependentPartSelectionForPMLCreation:=", True,
                "AllowRegionSelectionForPMLCreation:=", True,
                "Selections:="		, "''' + ','.join(sig) + '''"
            ], 
            [
                "NAME:Attributes",
                "MaterialValue:="	, "''' + '\\' + '''"''' + material + '\\' + '''"",
                "SolveInside:="		, False,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="	, False
            ])\n'''

        
                
        
    def zero(self):
        """ moves all signals in the model to the origin
        """


        return '''oEditor.Move(
        [
            "NAME:Selections",
            "Selections:="		, "''' + ','.join(self.all_signals) + '''",
            "NewPartsModelFlag:="	, "Model"
        ], 
        [
            "NAME:TranslateParameters",
            "TranslateVectorX:="	,  str(-1*float(bound_box[0])) + 'mm',
            "TranslateVectorY:="	,  str(-1*float(bound_box[1])) + 'mm',
            "TranslateVectorZ:="	,  str(-1*float(bound_box[2])) + 'mm'
        ])   '''
    
    def make_substrate(self):
        """ creates 350um substrate below model
        """

        return '''oEditor.CreateBox(
	[
		"NAME:BoxParameters",
		"XPosition:="		, "0mm",
		"YPosition:="		, "0mm",
		"ZPosition:="		, "0mm",
		"XSize:="		, str(float(bound_box[3])) + 'mm',
		"YSize:="		, str(float(bound_box[4])) + 'mm',
		"ZSize:="		, "-0.35mm"
	], 
	[
		"NAME:Attributes",
		"Name:="		, "Substrate",
		"Flags:="		, "",
		"Color:="		, "(143 175 143)",
		"Transparency:="	, 0.9,
		"PartCoordinateSystem:=", "Global",
		"UDMId:="		, "",
		"MaterialValue:="	, "''' + '\\' + '''"silicon''' + '\\' + '''"",
		"SurfaceMaterialValue:=", "''' + '\\' + '"' + '\\' + '''"",
		"SolveInside:="		, True,
		"IsMaterialEditable:="	, True,
		"UseMaterialAppearance:=", False,
		"IsLightweight:="	, False
	])\n'''

    def make_vacuum(self):
        """creates vacuum space above model, uses twice the max y distance of the model as default
        """

        return '''oEditor.CreateBox(
	[
		"NAME:BoxParameters",
		"XPosition:="		, "0mm",
		"YPosition:="		, "0mm",
		"ZPosition:="		, "0mm",
		"XSize:="		, str(float(bound_box[3])) + 'mm',
		"YSize:="		, str(float(bound_box[4])) + 'mm',
		"ZSize:="		, str(2*float(bound_box[3])) + 'mm'
	], 
	[
		"NAME:Attributes",
		"Name:="		, "vacuum",
		"Flags:="		, "",
		"Color:="		, "(143 175 143)",
		"Transparency:="	, 0.9,
		"PartCoordinateSystem:=", "Global",
		"UDMId:="		, "",
		"MaterialValue:="	, "''' + '\\' + '''"vacuum''' + '\\' + '''"",
		"SurfaceMaterialValue:=", "''' + '\\' + '"' + '\\' + '''"",
		"SolveInside:="		, True,
		"IsMaterialEditable:="	, True,
		"UseMaterialAppearance:=", False,
		"IsLightweight:="	, False
	])\n'''

    def subtract(self):
        """substract out all metallization from the vacuum above so there are no intersections of parts.
        """

        return '''oEditor.Subtract(
	[
		"NAME:Selections",
		"Blank Parts:="		, "vacuum",
		"Tool Parts:="		, "''' + ','.join(self.all_signals) + '''"
	], 
	[
		"NAME:SubtractParameters",
		"KeepOriginals:="	, True
	])\n'''

    def make_region(self):
        """ creates a zero padding region around entire model to define the problem region for maxwell.
        """
        
        return '''oEditor.CreateRegion(
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
		"+ZPadding:="		, "0",
		"-ZPaddingType:="	, "Percentage Offset",
		"-ZPadding:="		, "0"
	], 
	[
		"NAME:Attributes",
		"Name:="		, "Region",
		"Flags:="		, "Wireframe#",
		"Color:="		, "(143 175 143)",
		"Transparency:="	, 1,
		"PartCoordinateSystem:=", "Global",
		"UDMId:="		, "",
		"MaterialValue:="	, "''' + '\\' + '''"vacuum''' + '\\' + '''"",
		"SurfaceMaterialValue:=", "''' + '\\' + '"' + '\\' + '''"",
		"SolveInside:="		, True,
		"IsMaterialEditable:="	, True,
		"UseMaterialAppearance:=", False,
		"IsLightweight:="	, False
    ])\n'''


    


