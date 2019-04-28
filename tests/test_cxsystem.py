import pytest
import os
import sys
import CxSystem as cx
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
anatomy_and_system_config = os.path.join(path,'config_files','pytest_COBAEIF_config.csv')
physiology_config = os.path.join(path, 'config_files', 'Physiological_Parameters_for_COBAEIF.csv')
CM = cx.CxSystem(anatomy_and_system_config, physiology_config)

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
		
