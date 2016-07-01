__author__ = 'V_AD'
import scipy.io
from brian2 import *
from numpy import *
import os

class save_data(object):
    def __init__(self,save_path):
        self.save_path = save_path
        self.data = {}
        self.syntax_bank = []

    def creat_key(self,key):
        if not key in self.data:
            self.data[key] = {}

    def gather_result(self,CX_system):
        for syntax in self.syntax_bank:
            exec syntax
        self.save_to_file()

    def save_to_file(self):
        data_save_path = os.path.join(self.save_path, 'data.mat')
        # pars_save_path = os.path.join(self.save_path, 'pars.mat')
        scipy.io.savemat(data_save_path, self.data )
        # scipy.io.savemat(pars_save_path, self.pars) # this is in case you want to keep track of parameter changes

