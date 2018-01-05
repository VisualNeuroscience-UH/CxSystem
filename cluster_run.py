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
import getpass
import paramiko
from scp import SCPClient

class cluster_run(object):

    def __init__(self,array_run_obj, anat_file_address,physio_file_address):
        if sys.platform == "win32":
            raise Exception(u"❌  Cluster_run doesn't support windows OS yet.")
        if not os.path.exists('./_cluster_tmp'):
            os.mkdir('./_cluster_tmp')
        # with open('./_cluster_tmp/array_run_obj.pkl','wb') as fbb:
        #     pickle.dump(array_run_obj,fbb,pickle.HIGHEST_PROTOCOL)
        self.output_path_and_filename = self.parameter_finder(array_run_obj.anatomy_df, 'output_path_and_filename')
        try:
            self.remote_output_folder = self.parameter_finder(array_run_obj.anatomy_df, 'remote_output_folder')
        except NameError:
            print u"⚠   remote_output_folder is not defined in the configuration file, the default path is ./results [in cluster]"
            self.remote_output_folder = "./results"
        try:
            self.remote_repo_path = self.parameter_finder(array_run_obj.anatomy_df, 'remote_repo_path')
        except NameError:
            print u"⚠   remote_repo_path is not defined in the configuration file, the default value is home directory ~"
            self.remote_repo_path = "."
        try:
            self.remote_repo_path = int(self.parameter_finder(array_run_obj.anatomy_df, 'auto_download_result'))
        except NameError:
            print u"⚠   auto_download_results is not defined in the configuration file, the default value is 1"
            self.auto_download_results = 1
        try:
            self.cluster_address = self.parameter_finder(array_run_obj.anatomy_df, 'cluster_address')
        except NameError:
            raise Exception("cluster_address is not defined for running CxSystem on cluster")
        try:
            self.username = self.parameter_finder(array_run_obj.anatomy_df, 'username')
        except NameError:
            self.username = raw_input('username: ')
        self.password = getpass.getpass('password: ')

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy)
        self.client.connect(self.cluster_address, port=22, username=self.username, password=self.password)
        print u"✅ Connected to %s"%self.cluster_address
        scp = SCPClient(self.client.get_transport())
        if 'CxSystem.py' in self.ssh_commander('cd %s;ls'%self.remote_repo_path,0): # path is to CxSystem folder
            pass
        elif 'CxSystem' in self.ssh_commander('cd %s;ls'%self.remote_repo_path,0): # path is to CxSystem root folder
            self.remote_repo_path = os.path.join(self.remote_repo_path, 'CxSystem')
        else: # no CxSystem ==> cloning the repo
            if self.remote_repo_path.endswith('CxSystem'):
                self.remote_repo_path = self.remote_repo_path.rstrip('/CxSystem')
            self.ssh_commander('mkdir %s;cd %s;git clone https://github.com/sivanni/CxSystem' % (self.remote_repo_path,self.remote_repo_path),0)
            self.remote_repo_path = os.path.join(self.remote_repo_path, '/CxSystem')
            print u"✅ CxSystem cloned in cluster."
        scp.put(anat_file_address, os.path.join(self.remote_repo_path, '_tmp_anat_config.csv'))
        scp.put(physio_file_address, os.path.join(self.remote_repo_path, '_tmp_physio_config.csv'))
        print u"✅ config files transfered to cluster"
        # ask user to set the number of nodes, time and memory:
        raw_input("Please check the default slurm.job file and set the number of nodes, time, memory and email address, then press a key to contiue ...")

        # building slurm :
        if not os.path.isdir('./_cluster_tmp'):
            os.mkdir('./_cluster_tmp')
        for item_idx, item in enumerate(array_run_obj.clipping_indices):
            with open("./slurm.job",'r') as sl1:
                with open ("./_cluster_tmp/_tmp_slurm_%d.job"%item_idx,'w') as sl2:
                    for line in sl1:
                        sl2.write(line)
                    # for item_idx,item in enumerate(array_run_obj.clipping_indices):
                    try:
                        sl2.write('python CxSystem.py _tmp_anat_config.csv _tmp_physio_config.csv %d %d\n'%(
                            item,array_run_obj.clipping_indices[item_idx+1]-array_run_obj.clipping_indices[item_idx]))
                    except IndexError:
                        sl2.write('python CxSystem.py _tmp_anat_config.csv _tmp_physio_config.csv %d %d\n' % (
                        item, array_run_obj.total_configs - array_run_obj.clipping_indices[item_idx]))
                    # sl2.write('wait\n')
            scp.put('./_cluster_tmp/_tmp_slurm_%d.job'%item_idx, os.path.join(self.remote_repo_path, './_tmp_slurm_%d.job'%item_idx))
        print u"✅ Slurm file generated and copied to cluster"
        self.chan = self.client.invoke_shell()
        self.chan.send('cd %s\n'%self.remote_repo_path)
        # for item_idx, item in enumerate(array_run_obj.clipping_indices):
        #     self.chan.send('sbatch _tmp_slurm_%d.job\n' %item_idx)
        # print u"✅ Slurm job successfully submitted"
        self.spawner()


    def checker_downloader_cleaner(self):
        def ssh_commander(client,command, print_flag):
            stdin, stdout, stderr = client.exec_command(command)
            out = stdout.read(),
            if print_flag:
                print out[0]
            return out[0]
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(self.cluster_address, port=22, username=self.username, password=self.password)
        scp = SCPClient(client.get_transport())
        print u"✅ Checker_downloader_cleaner Connected to %s"%self.cluster_address
        # time.sleep(15)
        local_folder = os.path.dirname(self.output_path_and_filename)
        if not os.path.isdir(local_folder):
            os.mkdir(local_folder)
        remote_result_abs_path = ssh_commander(client,'cd %s;cd %s; pwd' % (self.remote_repo_path,
                                                                     self.remote_output_folder), 1).rstrip('\r\n')
        waiting_flag = True
        print "waiting"
        while waiting_flag:
            if not ssh_commander(client,'cd %s; ls -d */' % (remote_result_abs_path), 0) and 'metadata' in ssh_commander(client,'cd %s; ls' % (remote_result_abs_path), 0):
                #just to double check:
                if not self.username in  ssh_commander(client,'squeue -l -u %s'%self.username , 0):
                # here it means there is no folder in result folder and therefore all simulations are done
                # so we copy back the result and remove the files on cluster
                    for item in ssh_commander(client,'cd %s; ls' % (remote_result_abs_path), 0).split('\n'):
                        if item != '':
                            scp.get(os.path.join(remote_result_abs_path,item),os.path.join(local_folder,item))
                    # cleaning
                    ssh_commander(client,'cd %s; rm auto_cluster_job*;rm _tmp_*;rm -rf %s' % (self.remote_repo_path, remote_result_abs_path), 0)
                    waiting_flag = False
            time.sleep(5)
            print "iteration"
        self.client.close()
        print u"✅ Results downloaded and remote cleaned."
        shutil.rmtree('./_cluster_tmp')
        print u"✅ Local environment cleaned."
        print u"✅ Results available in: %s" %local_folder



    def spawner(self):
        '''
        Spawns processes each dedicated to an instance of CxSystem.
        '''
        print u"ℹ️ checker_downloader_cleaner process started"
        p = multiprocessing.Process(target=self.checker_downloader_cleaner, args=())
        p.start()
        p.join()

    def ssh_commander(self,command,print_flag):
        stdin, stdout, stderr = self.client.exec_command(command,get_pty=True)
        out= stdout.read(),
        if print_flag:
            print out[0]
        return out[0]

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


