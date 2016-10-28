__author__ = 'V_AD'
import cPickle as pickle
import zlib
from brian_genn_version  import *
from numpy import *
import os
import re
from datetime import datetime
import ntpath

class save_data(object):
    '''
    As the name implies, this module is used for gathering the data and saving the result.
    '''
    def __init__(self,save_path,datetime_str):
        '''
        The initialization method for save_data object.

        :param save_path: The path for saving the data.

        Main internal variables:

        * data: the main variable to be saved. It contains all the data about the positions of the NeuronGroup()s as well as the monitor results.
        * syntax_bank: Since the monitors are explicitly defined in the Globals(), extracting the data from them requires addressing their name explicitely. To automatize this process, the syntaxes for extracting the data from the target monitors are generated and saved in this variable, so that they can be run at the end of the simulation.
        '''
        self.save_path = save_path
        self.datetime_str = datetime_str
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
        print "Saving data to file."
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        self.save_path = os.path.join(self.save_folder, self.save_pure_filename + self.datetime_str + self.save_extension)
        while os.path.isfile(self.save_path):
            idx = 1
            self.save_path = os.path.join(self.save_folder,
                                          self.save_pure_filename + self.datetime_str  + '_%d'%idx + self.save_extension)
            idx +=1

        if 'gz' in self.save_extension:
            with open(self.save_path, 'wb') as fp:
                fp.write(zlib.compress(pickle.dumps(self.data , pickle.HIGHEST_PROTOCOL), 9))
        # if 'mat' in self.save_extension:
        #     scipy.io.savemat(self.save_path, self.data )
        # elif 'h5' in self.save_extension:
        #     hkl.dump(self.data,self.save_path)
        # scipy.io.savemat(pars_save_path, self.pars) # this is in case you want to keep track of parameter changes

