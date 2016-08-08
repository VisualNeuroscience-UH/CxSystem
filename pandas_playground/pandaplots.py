import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

mycmap = 'viridis'


data = pd.read_json('pathways_anatomy_vanni.json', orient='index')

# Saving & reading messes with correct order! >.<
sort_order = ['layer_pre', 'is_inhibitory_pre', 'celltype_pre', 'layer_post', 'is_inhibitory_post', 'celltype_post']
data = data.sort_values(by=sort_order)

correct_order = data.neurongroup_pre.unique()

# Create 2D data
plotdata = dict()

plotdata['vanni_mean_synapses'] = data.pivot_table('mean_number_of_synapses_per_connection', index='neurongroup_pre', columns='neurongroup_post', aggfunc = sum)
plotdata['vanni_conn_probability'] = data.pivot_table('connection_probability', index='neurongroup_pre', columns='neurongroup_post', aggfunc=sum)

plot_these = ['vanni_mean_synapses', 'vanni_conn_probability']


# Plot it
plt.close() # In case something is open
plotobj = dict()
sns.set()

for p in plot_these:
	plotdata[p] = plotdata[p].reindex(index=correct_order, columns=correct_order) # Pivoting messes (=alphabetizes) the order
	plotdata[p].index.name = 'Presynaptic neuron group'
	plotdata[p].columns.name = 'Postsynaptic neuron group'
	plotobj[p] = sns.heatmap(plotdata[p], cmap=mycmap)
	plt.tick_params(axis="both", labelsize=8)
	plt.setp(plotobj[p].get_xticklabels(), rotation=90)
	plt.setp(plotobj[p].get_yticklabels(), rotation=0)
	plt.title(p)
	plt.tight_layout()
	plt.savefig('plots/'+p+'.png', dpi=100)
	plt.close()


# Todo:
# 1) Order neuron groups excitatory->inhibitory, then ab-lly
# 2) Create/modify class with above functionality (heatmap-method for mean-synapses,conn-probability)