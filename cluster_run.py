# -*- coding: utf-8 -*-
__author__ = 'Andalibi, V., Hokkanen H., Vanni, S.'

'''
The preliminary version of this software has been developed at Aalto University 2012-2015, 
and the full version at the University of Helsinki 2013-2017. The software is distributed 
under the terms of the GNU General Public License. 
Copyright 2017 Vafa Andalibi, Henri Hokkanen and Simo Vanni.
'''

import pip
import sys
import CxSystem as CX
from brian2 import *
import multiprocessing
import time
import shutil
import os
import pandas as pd
import zlib
import bz2
import cPickle as pickle
import sys
import itertools
if sys.platform != "win32":
    from pexpect import pxssh
import getpass



class cluster_run(object):

    def __init__(self, array_run_obj):
        if sys.platform == "win32":
            raise Exception(u"❌  Cluster_run doesn't support windows OS yet.")
        os.mkdir('./_cluster_tmp')
        with open('./_cluster_tmp/array_run_obj.pkl','wb') as fbb:
            pickle.dump(array_run_obj,fbb,pickle.HIGHEST_PROTOCOL)
        try:
            self.remote_path = int(self.parameter_finder(array_run_obj.anatomy_df, 'remote_path'))
        except NameError:
            raise ("remote_path [relative to home directory] is not defined for running CxSystem on cluster")
        try:
            self.remote_path = int(self.parameter_finder(array_run_obj.anatomy_df, 'auto_download_result'))
        except NameError:
            print u"⚠   auto_download_results is not defined in the configuration file, the default value is 1"
            self.auto_download_results = 1
        try:
            self.cluster_address = int(self.parameter_finder(array_run_obj.anatomy_df, 'cluster_address'))
        except NameError:
            raise ("cluster_address is not defined for running CxSystem on cluster")
        try:
            self.username = int(self.parameter_finder(array_run_obj.anatomy_df, 'username'))
        except NameError:
            self.username = raw_input('username: ')
        self.password = getpass.getpass('password: ')
        s = pxssh.pxssh()


    def parameter_finder(self,df,keyword):
        location = where(df.values == keyword)
        if location[0].size:
            counter = int(location[0])+1
            while counter < df.shape[0] :
                if '#' not in str(df.ix[counter][int(location[1])]):
                    value = df.ix[counter][int(location[1])]
                    break
                else:
                    counter+=1
            return value
        else:
            raise NameError('Variable %s not found in the configuration file.'%keyword)


