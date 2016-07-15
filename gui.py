# -*- coding: utf-8 -*-
'''
Created on Sat May 28 16:39:58 2016
@author: Alex Diebold
'''

import sys
sys.path.append('C:\\Users\\adiebold\\Documents\\GitHub\\DogBone')

import os
import constants as c
import matplotlib                   #for 3D model
from collections import namedtuple

#if using the Spyder console, matplotlib is already imported and the backend cannot be changed with .use() as is needed
#to change the backend to TkAgg, go to Tools > Preferences > Console > External modules > Matplotlib GUI backend
#be sure to mind the caps in TkAgg
'''
backend = matplotlib.get_backend()
if backend != 'TkAgg' and backend != 'module://ipykernel.pylab.backend_inline':
    matplotlib.use('TkAgg')             #backend of matplotlib, used for putting in GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
'''
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from tkinter import *               #GUI module
from tkinter import ttk             #for styling purposing
from tkinter import filedialog      #window for saving and uploading files
import json                         #for saving and uploading files
from main import Main        #for converting to Gcode

class GUI(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        
        Tk.iconbitmap(self, 'UW_Madison_icon.ico')
        Tk.title(self, '3D Printer Parameter Setter')
        #format window size -- width=450, height=475, 100px from left of screen, 100px from top of screen
        #Tk.geometry(self, '450x475+100+100')
        
        #set up frame
        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid(row=0,column=0)
        
        #create menubar
#        menubar = Menu(container)
#        filemenu = Menu(menubar, tearoff=0)
#        filemenu.add_command(label='Save', command=lambda: Page_Variables.save(Page_Variables))
#        filemenu.add_command(label='Upload', command=lambda: Page_Variables.upload(Page_Variables))
#        menubar.add_cascade(label='File', menu=filemenu)
#        
#        Tk.config(self, menu=menubar)
        
        #dictionary of Frames
        self.frames = {}
        
        self.shapes = {Page_Variables : '425x525+150+100',       
                       Page_Model : '600x500+150+100'}
        
        #add Frames to dictionary
#        for F in (Page_Variables):
#        
#            frame = F(self.container, self)
#            
#            self.frames[F] = frame
#            
#            frame.grid(row=0, column=0, sticky='nsew')
        frame = Page_Variables(self.container, self)
        self.frames[Page_Variables] = frame
        frame.grid(row=0, column=0, sticky='nsew')
            
        
        #show initial Frame
        Tk.geometry(self, self.shapes[Page_Variables])
        self.show_frame(Page_Variables)
       
    #show frame
    def show_frame(self, cont, delete=False, cont_to_del = None):
        
        if cont not in self.frames:
            frame = cont(self.container, self)
            self.frames[cont] = frame
            frame.grid(row=0, column=0, sticky='nsew')
            
        Tk.geometry(self, self.shapes[cont])        
        frame = self.frames[cont]
        frame.tkraise() 
        
        if delete:
            del self.frames[cont_to_del]
        
class Page_Variables(Frame):
    
    COMMON = 0
    PART = 1
    LAYER = 2
    FILE = 3
    PRINT = 4
    
    INT_LIST = 0
    FLOAT_LIST = 1
    
    Menu = namedtuple('Menu', 'name group')
    menus = [
            Menu('Common', COMMON),
            Menu('Part', PART),
            Menu('Layer', LAYER),
            Menu('File', FILE),
            Menu('Print', PRINT)
            ]

    menus.sort(key=lambda x : x.group)             

             
    Par = namedtuple('Parameter', 'label data_type groups')
    parameters = [
                Par('outline', str, (COMMON, PART)),
                Par('stl_file', str, (COMMON, PART)),
                Par('solidityRatio', FLOAT_LIST, (COMMON, PART)),
                Par('printSpeed', INT_LIST, (COMMON, PART)),
                Par('shiftX', FLOAT_LIST, (COMMON, PART)),
                Par('shiftY', FLOAT_LIST, (COMMON, PART)),
                Par('firstLayerShiftZ', float, (PART,)),
                Par('numLayers', INT_LIST, (COMMON, PART)),
                Par('pattern', None, (PART,)),
                Par('designType', int, (PART,)),
                Par('infillAngleDegrees', FLOAT_LIST, (COMMON, LAYER)),
                Par('pathWidth', FLOAT_LIST, (LAYER,)),
                Par('layerHeight', FLOAT_LIST, (LAYER,)),
                Par('infillShiftX', FLOAT_LIST, (LAYER,)),
                Par('infillShiftY', FLOAT_LIST, (LAYER,)),
                Par('numShells', INT_LIST, (COMMON, LAYER)),
                Par('trimAdjust', FLOAT_LIST, (LAYER,)),
                Par('start_Gcode_FileName', str, (FILE,)),
                Par('end_Gcode_FileName', str, (FILE,)),
                Par('bed_temp', int, (COMMON, PRINT)),
                Par('extruder_temp', int, (COMMON, PRINT)),
                ]
                
    OUTPUTFILENAME = 'outputFileName'
    CURRPATH = os.path.dirname(os.path.realpath(__file__))
    GCODEPATH = CURRPATH + '\\Gcode\\'
    JSONPATH = CURRPATH + '\\JSON\\'
    OUTPUTSUBDIRECTORY = 'outputSubDirectory'
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        ########################
        #   class variables    #
        ########################
        
        #string that is the filename of the current file
        self.filename = ''
        
        #dictionary with variable name as key and StringVar as value
        self.text_variable = {} 
        
        #dictionary with variable name as key and Label as value        
        self.labels = {}
                   
        #dictionary with variable name as key and Entry as value
        self.entries = {}
        
        #array of Strings of the variables
#        self.texts = [self.STL_FILE, self.SOLIDITYRATIO, self.PRINTSPEED, self.SHIFTX,            #part parameters
#                 self.SHIFTY, self.FIRSTLAYERSHIFTZ, self.NUMLAYERS,                         #part parameters
#                 self.PATTERN, self.DESIGNTYPE,                                           #part parameters
#                 self.INFILLANGLEDEGREES, self.PATHWIDTH, self.LAYERHEIGHT,                  #layer parameters
#                 self.INFILLSHIFTX, self.INFILLSHIFTY, self.NUMSHELLS, self.TRIMADJUST,         #layer parameters
#                 self.START_GCODE_FILENAME, self.END_GCODE_FILENAME,                      #file parameters
#                 self.BEDTEMP, self.EXTRUDERTEMP]                                           #print parameters
        self.texts = [i.label for i in self.parameters]
        
        
        self.fields = []
        for menu in self.menus:
            self.fields.append([par for par in self.parameters if menu.group in par.groups])
           
        defaults_path = self.JSONPATH + 'DEFAULT.json'   
        if os.path.isfile(defaults_path):
            with open(defaults_path, 'r') as fp:
                self.defaults = json.load(fp)
        else:
            self.defaults = {}
            
        for key in self.texts:
            if key not in self.defaults:
                self.defaults[key] = ''
                    
        self.create_var_page()
              
    ##########################################################
    #   methods that create labels, entries, and/or buttons  #
    ##########################################################
              
    #initial creation of labels
    def set_labels(self):        
        #create all labels
        for x in range(len(self.texts)):
            #create label
            self.labels[self.texts[x]] = Label(self, text=self.texts[x])
        
        for x, par in enumerate(self.fields[self.COMMON]):
            self.labels[par.label].grid(row=x+1,column=0)  
            
    #initial creation of entries
    def set_entries(self):

        #create all StringVars
        for x, label in enumerate(self.texts):
            self.text_variable[label] = StringVar(self, value=self.defaults[label])
            
        #create all entries
        for x, label in enumerate(self.texts):
            #create entry 
            self.entries[label] = ttk.Entry(self, textvariable=self.text_variable[label])
            
        #show commonly used variables
        for x, par in enumerate(self.fields[self.COMMON]):
            #use grid() after creating entry or dictionary value will be 'NoneType'
            self.entries[par.label].grid(row=x+1,column=1)
        
    #creates button for saving all values
    def save_option(self): 
        
        #create button
        buttonSave = ttk.Button(self,text='Save (exclude .json)',command=lambda: self.save()).grid(row=0,column=1)
    
    #creates label, entry, and button for uploading all values    
    def upload_option(self):   
        
        #create button
        buttonUpload = ttk.Button(self,text='Upload',command=lambda: self.upload()).grid(row=0,column=0)
        
    #create menu of label and buttons to switch between tabs
    def tab_buttons(self):
        
        #label for parameters
        labelParameters = Label(self,text='Parameters',font='-weight bold')
        labelParameters.grid(row=0,column=2)

        #button to display all variables
        buttonAll = ttk.Button(self,text='All',command=self.command(self.parameters))
        buttonAll.grid(row=1,column=2)
        
        for x, menu in enumerate(self.menus):
            button = ttk.Button(self, text=menu.name, command=self.command(self.fields[menu.group]))
            button.grid(row=2+x, column=2)
            
    def command(self, params):
        def inner_command():
            for text in self.texts:
                self.labels[text].grid_forget()      
                self.entries[text].grid_forget()
            for x, param in enumerate(params):
                self.labels[param.label].grid(row=x+1, column=0)
                self.entries[param.label].grid(row=x+1, column=1)
        return inner_command
        
    #create label and buttons for different preset values of parameters
    def presets(self):
        
        #label for presets
        labelPresets = Label(self,text='Presets',font='-weight bold')
        labelPresets.grid(row=0,column=3)
        #button for dogbone
        buttonDogbone = ttk.Button(self,text='Dogbone',command=lambda: self.dogbone())
        buttonDogbone.grid(row=1,column=3)
    
    #create button to convert to Gcode
    def gcode(self):
        
        buttonGcode = ttk.Button(self,text='Convert to Gcode',command=lambda: self.convert())
        buttonGcode.grid(row=len(self.texts)+1,column=1)
        
    #all set up functions together
    def create_var_page(self):
        
        self.set_labels()
        self.set_entries()
        self.save_option()
        self.upload_option()
        self.tab_buttons()
        self.presets()
        self.gcode()
        self.model_page()
        self.g_robot()
    
    #create button to switch to 3D model page
    def model_page(self):  
        
        #button to switch to 3D model page
        buttonModel = ttk.Button(self, text='3D Model', 
                             command=lambda: self.to_model())
        buttonModel.grid(row=len(self.texts)+1,column=0)
        
    #create radiobutton to switch between gcode and robotcode
    def g_robot(self):
        
        self.g_robot_var = IntVar()
        self.g_robot_var.set(0)
        
        ttk.Radiobutton(self, text='Gcode', variable=self.g_robot_var, value=c.GCODE).grid(row=len(self.texts)+2,column=0)
        ttk.Radiobutton(self, text='RobotCode', variable=self.g_robot_var, value=c.ROBOTCODE).grid(row=len(self.texts)+2,column=1)
        
    #############################################
    #   methods that are called from buttons    #
    #############################################
                
    def save(self, name = None):
        
        #only saving JSON
        if name == None:
            savePath = filedialog.asksaveasfilename()
            savePath = self.check_end(savePath)
            gcodeName = savePath.split('/')[len(savePath.split('/'))-1] + '.gcode'
            self.filename = savePath + '.json'  
        
        #converting to gcode -- create temp json file with same name as gcode file
        elif name == 'gcode':
            savePath = filedialog.asksaveasfilename()
            savePath = self.check_end(savePath)
            self.filename = self.JSONPATH + savePath.split('/')[len(savePath.split('/'))-1] + '.json'
            gcodeName = savePath + '.gcode'
            
        #switching to 3D model page -- create temp json file
        else:
            savePath = 'blank'
            gcodeName = self.GCODEPATH + name + '.gcode'
            self.filename = self.JSONPATH + name + '.json'          
        
        data = {}               #dictionary to put String value of StringVar values in
        #check if the user cancelled saving the file
        if self.filename:
                                                       #variables with type None
            data[self.OUTPUTFILENAME] = gcodeName
            data[self.OUTPUTSUBDIRECTORY] = savePath
            
            for label, data_type, _ in self.parameters:
                if data_type is str:
                    data[label] = self.text_variable[label].get()
                elif data_type is None:
                    data[label] = None
                elif data_type is int or data_type is float:
                    data[label] = data_type(self.text_variable[label].get())
                else:
                    value = self.text_variable[label].get()            
                    if ' ' in value:
                        value = value.replace(' ', ',')                
                    if ',,' in value:
                        value = value.replace(',,', ',')                         
                    if data_type == self.INT_LIST:
                        data[label] = [int(i) for i in value.split(',')]     
                    elif data_type == self.FLOAT_LIST:
                        data[label] = [float(i) for i in value.split(',')]    
            
            if not os.path.isdir(self.JSONPATH):
                os.makedirs(self.JSONPATH)
            with open(self.filename, 'w') as fp:
                json.dump(data, fp)    #save JSON file
    
    def check_end(self, pathName):
        
        if pathName.endswith('.json'):
            pathName = pathName[:-5]
        elif pathName.endswith('.gcode'):
            pathName = pathName[:-6]
    
        return pathName
        
    #uploads dictionary from JSON file to replace current StringVar values, opens window to find file       
    def upload(self):

        data = {}               #new dictionary that will be replaced with dictionary from JSON file
        uploadname = filedialog.askopenfilename()     #creates window to find file
        
        if uploadname != '':
            with open(uploadname, 'r') as fp:
                data = json.load(fp)    #upload JSON file
                
            for key in data:
                if data[key] == None:
                    self.text_variable[key].set('None') #replace current StringVar with String 'None'
                elif key in self.text_variable.keys():
                    value = str(data[key])
                    value = value.replace('[','')
                    value = value.replace(']','')
                    self.text_variable[key].set(value)   #replace current StringVar values with data from JSON file
        
    #change values to dogbone preset    
    def dogbone(self):
        
        dogbone_data = ['Arch3.stl', '1.09', '2000', '10, 50',                     #part parameters
                '10, 35, 60', '0', '8',                                                 #part parameters
                'None', '0',                                                            #part parameters
                '0, -45, 90, 45, 45, 90, -45', '0.5', '0.4',                            #layer parameters
                '0', '0', '13,1,1,0,0,1,1',  '0.0002',                             #layer parameters
                'Start_Gcode_Taz5.txt', 'End_Gcode_Taz5.txt',                      #file parameters
                '999', '999']                                                       #print parameters
                
        for x in range(len(self.texts)):
            self.text_variable[self.texts[x]].set(dogbone_data[x])        #change values to dogbone values
    
    #create Gcode file                    
    def convert(self, name = None):
        
        if name == None:
            self.save('gcode')
        else:
            self.save(name)
        
        #check if the user cancelled converting to Gcode
        if self.filename != '':
            #convert to Gcode
            conversion = Main(self.filename, self.g_robot_var.get())
            conversion.run()
            os.remove(self.filename)
            
    
    #convert to gcode, switch to Page_Model        
    def to_model(self):
# TODO: uncomment these        
        self.convert('temp')
        
        self.controller.show_frame(Page_Model)
        
        os.remove(self.GCODEPATH + 'temp.gcode')
        


class Page_Model(Frame):    
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.get_data()
        
    def get_data(self):
        
        data = []
        counter = 0
        self.xar = []
        self.yar = []
        self.zar = []
        self.layer_part = []
        
        with open('data_points.txt', 'r') as f:
            for line in f:
                if 'start' in line:
                    print('start ', counter)
                    start = counter
                elif 'layer_number' in line:
                    print(line)
                    print(counter)
                    self.layer_part.append([line.split(':')[1], line.split(':')[3], start, counter])
                else:
                    data.append(line)      
                    data[counter] = data[counter].split(',')
                    for y in range(0,len(data[counter])):
                        data[counter][y] = float(data[counter][y])
                    self.xar.append([data[counter][0], data[counter][3]])
                    self.yar.append([data[counter][1], data[counter][4]])
                    self.zar.append([data[counter][2], data[counter][5]])     
                    counter += 1
                    
        self.setup()
    
    def show_labels(self):
        
        labelIntro = Label(self, text='Choose the start and end layers of the model:')
        labelIntro.grid(row=0,column=1)
        
        labelStart = Label(self, text='Start')
        labelStart.grid(row=1,column=0)
        
        labelEnd = Label(self, text='End')
        labelEnd.grid(row=2,column=0)
        
    def show_scales(self):
        
        self.scaleStart = Scale(self, from_=0, to=len(self.xar), length=500, orient=HORIZONTAL)
        self.scaleStart.grid(row=1,column=1)
        
        self.scaleEnd = Scale(self, from_=0, to=len(self.xar), length=500, tickinterval=5000, orient=HORIZONTAL)
        self.scaleEnd.grid(row=2,column=1)
        
    def show_buttons(self):
        
        buttonSubmit = ttk.Button(self, text='Create Model', command=lambda: 
            self.make_graph(self.scaleStart.get(), self.scaleEnd.get()))
        buttonSubmit.grid(row=3,column=1)
        
        buttonVariables = ttk.Button(self, text='Variables', 
                     command=lambda: self.to_variables())
        buttonVariables.grid(row=0,column=0)
    
#        self.buttonUpdate = ttk.Button(self, text='Update from Variables', command=lambda: self.get_data())
#        self.buttonUpdate.grid(row=4,column=1)

#        self.radiobuttons = {}
#        x = 0
#        y = 0
#        z = 0
#        selection = IntVar()
#        
#        for id_array in self.layer_part:
#            rb_text = 'Part:' + str(id_array[1] + ' Layer:' + str(id_array[0]))
#            self.radiobuttons[str(id_array)] = ttk.Radiobutton(self, text=rb_text, variable=selection, value=x)
#            self.radiobuttons[str(id_array)].grid(row=z+4,column=y)
#            x+=1
#            y = x//5
#            z = x%5 

        self.intvar_layerparts = {}
        
        self.mb = ttk.Menubutton(self, text='testing')
        self.mb.grid()
        self.mb.menu = Menu (self.mb, tearoff=1)
        self.mb['menu'] = self.mb.menu
        
        for id_array in self.layer_part:
            self.intvar_layerparts[str(id_array)] = IntVar()
            self.rb_text = 'Part:' + str(id_array[1] + ' Layer:' + str(id_array[0]))
            self.mb.menu.add_checkbutton(label=self.rb_text, onvalue=1, offvalue=0, variable=self.intvar_layerparts[str(id_array)])
        
        self.mb.grid(row=5,column=1)
        
        buttonModel = ttk.Button(self, text='Create Model', command=lambda:
            self.make_model())
        buttonModel.grid(row=6,column=1)
        

    def setup(self):

        self.show_labels()
        self.show_scales()
        self.show_buttons()                
        
    def make_graph(self, start, end):
                
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.colors = []
        
        color_num = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        color_num2 = ['0','8']
        for one in color_num:
            for two in color_num2:
                for three in color_num2:
                    for four in color_num2:
                        for five in color_num2:
                            for six in color_num:
                                curr_color = '#' + one + two + three + four + five + six
                                self.colors.append(curr_color)
            
        for num in range(start, end):
            num_color = num%len(self.colors)
            self.ax.plot_wireframe(self.xar[num], self.yar[num], self.zar[num], color=self.colors[num_color])
            
        plt.show()
        
    def make_model(self):
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.colors = []
        
        color_num = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        color_num2 = ['0','8']
        for one in color_num:
            for two in color_num2:
                for three in color_num2:
                    for four in color_num2:
                        for five in color_num2:
                            for six in color_num:
                                curr_color = '#' + one + two + three + four + five + six
                                self.colors.append(curr_color)
         
#        for id_array in self.layer_part:
#            print(self.intvar_layerparts[id_array].get())
         
         
        counting = 0                       
        for id_array in self.layer_part:
            if self.intvar_layerparts[str(id_array)].get() == 1:
                for c in range(int(id_array[2]), int(id_array[3])):
                    num_color=c%len(self.colors)
                    self.ax.plot_wireframe(self.xar[c], self.yar[c], self.zar[c], color=self.colors[num_color])
                    
        plt.show()
        
    def to_variables(self):
        
        self.controller.show_frame(Page_Variables, True, Page_Model)
        
    
#class Page_Model(Frame):
#    
#    def __init__(self, parent, controller):
#        Frame.__init__(self, parent)
#        self.controller = controller
#        
#        labelExample = Label(self, text='HELLO')
#        labelExample.pack()
#        
#        self.to_variables()
#        
#        canvasExample = Canvas(self, width=200, height=100)
#        canvasExample.pack()      \
#        
#        canvasExample.create_rectangle(50, 20, 150, 80, fill='#476042')
#        canvasExample.create_line(0, 0, 50, 20, width=3)
#        
#        '''
#        f = Figure(figsize=(5,5), dpi=100)
#        a = f.add_subplot(111)
#        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
#        
#        canvas = FigureCanvasTkAgg(f, self)
#        canvas.show()
#        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
#        
#        toolbar = NavigationToolbar2TkAgg(canvas, self)
#        toolbar.update()
#        canvas._tkcanvas.pack()
#        '''
#        
#        
#    def to_variables(self):
#        
#        buttonVariable = ttk.Button(self, text='Variables', 
#                                command=lambda: self.controller.show_frame(Page_Variables))
#        buttonVariable.pack()
    
#only works if program is used as the main program, not as a module    
#if __name__ == '__main__':
    

#####################
#   GUI creation    #
#####################

#create GUI
gui = GUI()

#keeps GUI open, always necessary
gui.mainloop() 