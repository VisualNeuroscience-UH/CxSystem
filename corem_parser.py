'''
The program is distributed under the terms of the GNU General Public License
Copyright 2017 Vafa Andalibi, Simo Vanni, Henri Hokkanen.
'''

from brian2 import *

corem_root_dir = '../COREM/COREM/'
corem_results_dir = corem_root_dir + 'results/'
corem_retina_scripts_dir = corem_root_dir + 'Retina_scripts/'


# class Corem_retina(retina_script_name, timestep)

# def run_retina_script()
# Run the retina script

# def read_results(file_prefixes)
# Go through all files with prefix in file_prefixes (different cell types)
# results[cell_type][i] -> TimedArray -> Brian2 array of results that's flexible with time
