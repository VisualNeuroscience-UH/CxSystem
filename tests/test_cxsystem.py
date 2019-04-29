import pytest
import os
import sys
import CxSystem as cx
import numpy as np
import pdb
from mock import Mock
import inspect

'''
In windows I had problems with CxSystem import. I had to run pytest in shell: python -m pytest.
This will add the current directory to sys.path. If you get tired doing this, add
the repo to your pythonpath by adding PYTHONPATH environmental variable. 
Run pytest at CxSystem root, such as git repo root.
'''

cwd = os.getcwd()
path, file = os.path.split(cx.__file__)
anatomy_and_system_config = os.path.join(path, 'tests', 'config_files', 'pytest_COBAEIF_config.csv')
physiology_config = os.path.join(path, 'tests', 'config_files', 'pytest_Physiological_Parameters_for_COBAEIF.csv')
CM = cx.CxSystem(anatomy_and_system_config, physiology_config, instantiated_from_array_run=0)

def test_cwd():
	assert "CxSystem.py" in os.listdir(os.getcwd()) 

def test_anatomy_and_system_config_file_exist():
	assert os.path.isfile(anatomy_and_system_config)
	
def test_physiology_config_file_exist():
	assert os.path.isfile(physiology_config)
	
	
class TestInit:

	def test_csv_shape(self):
		assert CM.anat_and_sys_conf_df.shape[1] == 28
		
	def test_dataframe_delimiters(self):
		assert not ',' in CM.anat_and_sys_conf_df.to_string() # Comma is the delimiter in csv and should not remain in dataframe
		assert not ';' in CM.anat_and_sys_conf_df.to_string() # Windows local settings may save csv with semicolons

	def test_number_of_input_arguments(self):
		assert CM.__init__.__code__.co_argcount==8, "Number of arguments have changed"
		
	def test_local_variable_names(self):
		assert CM.__init__.__code__.co_varnames == \
		('self', 'anatomy_and_system_config', 'physiology_config', 'output_file_suffix', 
		'instantiated_from_array_run', 'cluster_run_start_idx', 'cluster_run_step', 'array_run_in_cluster', 
		'params_indices', 'row_idx', 'number_of_new_columns', 'number_of_rows', 
		'existing_rows', 'new_columns', 'empty_dataframe', 'new_anat_and_sys_conf_df', 
		'row', 'check_array_run_anatomy', 'check_array_run_physiology', 'trials_per_config'
		)
		
	def test_input_argument_types(self):
		assert isinstance(CM.StartTime_str, basestring) 
		# assert CM.array_run == bool(CM.array_run), "Indirect test for input arg instantiated_from_array_run"
		assert isinstance(CM.array_run, int), "Indirect test for input arg instantiated_from_array_run"
		assert isinstance(CM.cluster_run_start_idx, int) 
		assert isinstance(CM.cluster_run_step, int) 
		assert isinstance(CM.array_run_in_cluster, int) 
		
class TestConfigurationExecutor:

	def test_definition_lines_idx(self):
		'''Test that indeces are the same given the constant configuration file'''
		assert all(CM.anat_and_sys_conf_df.loc[:,0][CM.anat_and_sys_conf_df.loc[:,0]=='row_type'].index \
				== np.array([1, 5, 8, 12]))
	# def test_method_mapping(self):
		# 'device': [0,self.set_device],
		# 'save_generated_video_input_flag': [1,self.save_generated_video_input_flag],
		# 'runtime': [2,self._set_runtime],
		# 'sys_mode': [3,self._set_sys_mode],  # either "local" or "expanded"
		# 'scale': [4,self._set_scale],
		# 'grid_radius': [5,self._set_grid_radius],
		# 'min_distance': [6,self._set_min_distance],
		# 'do_init_vms': [7,self.do_init_vms],
		# 'default_clock': [8, self.set_default_clock],
		# 'output_path_and_filename': [9,self._set_output_path],
		# 'connections_saving_path_and_filename': [10,self._set_save_brian_data_path],
		# 'connections_loading_path_and_filename': [11,self._set_load_brian_data_path],
		# 'load_positions_only': [12,self.load_positions_only],
		# 'do_benchmark': [13,self.set_do_benchmark],
		# 'profiling': [14, self.set_profiling],
 
