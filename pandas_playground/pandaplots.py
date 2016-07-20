import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

mycmap = 'viridis'


data = pd.read_json('pathways_anatomy_vanni.json', orient='index')

# Create 2D data
plotdata = dict()
plotdata['markram_mean_synapses'] = data.pivot_table('mean_number_of_synapse_per_connection', index='markram_pre', columns='markram_post', aggfunc = sum) # Meaningless as there is nothing to aggregate
plotdata['vanni_mean_synapses'] = data.pivot_table('mean_number_of_synapse_per_connection', index='vanni_pre', columns='vanni_post', aggfunc = sum) # Should be weighted
plotdata['synapses_btw_layers'] = data.pivot_table('total_synapse_count', index='layer_pre', columns='layer_post', aggfunc=sum).fillna(0).T

plot_these = ['markram_mean_synapses', 'vanni_mean_synapses', 'synapses_btw_layers']


# Plot it
plt.close() # In case something is open
plotobj = dict()

for p in plot_these:
	plotobj[p] = sns.heatmap(plotdata[p], cmap=mycmap)
	plt.tick_params(axis="both", labelsize=6)
	plt.setp(plotobj[p].get_xticklabels(), rotation=90)
	plt.setp(plotobj[p].get_yticklabels(), rotation=0)
	plt.savefig(p+'.png', dpi=100)
	plt.close()

