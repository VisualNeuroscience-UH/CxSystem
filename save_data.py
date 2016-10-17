__author__ = 'V_AD'
import scipy.io
from brian_genn_version  import *
from numpy import *
import os
import re
from datetime import datetime
import hickle as hkl
import ntpath

class save_data(object):
    '''
    As the name implies, this module is used for gathering the data and saving the result.
    '''
    def __init__(self,save_path):
        '''
        The initialization method for save_data object.

        :param save_path: The path for saving the data.

        Main internal variables:

        * data: the main variable to be saved. It contains all the data about the positions of the NeuronGroup()s as well as the monitor results.
        * syntax_bank: Since the monitors are explicitly defined in the Globals(), extracting the data from them requires addressing their name explicitely. To automatize this process, the syntaxes for extracting the data from the target monitors are generated and saved in this variable, so that they can be run at the end of the simulation.
        '''
        self.save_path = save_path
        self.save_filename = ntpath.basename(self.save_path)
        self.save_pure_filename = os.path.basename(os.path.splitext(self.save_path)[0])

        self.save_folder = ntpath.dirname(self.save_path)
        self.save_extension = os.path.splitext(self.save_path)[1]
        if os.getcwd() in self.save_path:
            print "Info: the output of the system is saved in %s" %os.path.abspath(os.path.join(os.getcwd(), os.pardir))
            self.save_folder = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
            self.save_path = os.path.join(self.save_folder,self.save_filename)
        self.data = {}
        self.syntax_bank = []

    def creat_key(self,key):
        '''
        In case the user wants to save a peculiar variable, this method can be used to check and create a new key in data dictionary (if does not exist).

        :param key: name of the key to be created in the final data variable.
        '''
        if not key in self.data:
            self.data[key] = {}

    def gather_result(self,CX_system):
        for syntax in self.syntax_bank:
            exec syntax
        self.save_to_file()

    def save_to_file(self):
        '''
        The metohd for saving the data varibale in .mat file.
        '''

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        if os.path.isfile(self.save_path):
            # datetime_str = '_' + str(datetime.now()).replace('-','').replace(' ','_').replace(':','')[0:str(datetime.now()).replace('-','').replace(' ','_').replace(':','').index('.')]
            self.save_path = os.path.join(self.save_folder, self.save_pure_filename + '_new' + self.save_extension)

        if 'mat' in self.save_extension:
            scipy.io.savemat(self.save_path, self.data )
        elif 'h5' in self.save_extension:
            hkl.dump(self.data,self.save_path)
        # scipy.io.savemat(pars_save_path, self.pars) # this is in case you want to keep track of parameter changes

