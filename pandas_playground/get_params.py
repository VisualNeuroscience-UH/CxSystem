(# Playing around with Pandas
# Importing connection params from CXSystem's brian2_obj_namespaces file

import brian2_obj_namespaces as ns
import pandas as pd

#### 1. Take raw parameters -> list of tuples (key, parameter) for each parameter

rawpars = ns.synapse_namespaces('') # from brian2_obj_namespaces obviously
par_names = ['sp', 'cw', 'dist']

par_values = dict() 
for param in par_names:
	exec('par_values[param] = rawpars.'+ param +'.items()')


#### 2. Because key above is in form parameter + synapse type, let's get rid of the param prefix to get proper keys

par_valuess = dict() # can't edit tuples, so create a new dict
for param in par_names:
	par_valuess[param] = []
	n = len(param)+1 # number of chars to rip out from the beginning

	for i in range(len(par_values[param]) ):
		par_valuess[param].append( (par_values[param][i][0][n:], par_values[param][i][1]) ) 

#### 3. Convert these lists to pandas dataframes

synapses_df = dict()
for param in par_names:
	synapses_df[param] = pd.DataFrame.from_records(par_valuess[param], columns=['synapse_type', param], index='synapse_type')

#### 4. Join these frames to get a big table with all the params!

synapses_dff = pd.concat(synapses_df, axis=1)

#### 5. Save as JSON or whatever feels nice
#### ...or use %pylab (in iPython) to plot, eg. synapse_dff.cw.astype(float).plot(kind='bar')

synapses_dff.astype(str).to_json('synapse_params.json', orient='index')
