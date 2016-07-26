# Sketchy code for creating config file for connections btw Vanni neuron groups
# Henri Hokkanen 21 July 2016

import pandas as pd

file_pathways_anatomy_vannilized = 'pathways_anatomy_vannilized.json' # INPUT
file_pathways_anatomy_vanni = 'pathways_anatomy_vanni.json' # OUTPUT


def get_vanni_connection_params(connection_index):

	print 'Working on ' + connection_index + '\n'

	cell_N_dict = {
	    'L1_DAC': 58, 'L1_DLAC': 24, 'L1_HAC': 91, 'L1_NGC-SA': 52, 'L1_NGC-DA': 72, 'L1_SLAC': 41, 'L23_DBC': 106+69,
	    'L23_BP': 16+12, 'L23_LBC': 277+179, 'L23_NGC': 34+22, 'L23_NBC': 160+108, 'L23_SBC': 99+67, 'L23_ChC': 37+24,
	    'L23_BTC': 63+41, 'L23_PC': 2421+3456, 'L23_MC': 202+131, 'L4_ChC': 8, 'L4_NBC': 96, 'L4_LBC': 122, 'L4_MC': 118,
	    'L4_SS': 406, 'L4_SBC': 60, 'L4_DBC': 40, 'L4_SP': 1098, 'L4_PC': 2674, 'L4_BTC': 20, 'L4_BP': 8, 'L4_NGC': 6,
	    'L5_DBC': 96, 'L5_BP': 34, 'L5_LBC': 210, 'L5_STPC': 302, 'L5_NGC': 8, 'L5_SBC': 25, 'L5_NBC': 201, 'L5_ChC': 19,
	    'L5_BTC': 76, 'L5_TTPC1': 2403, 'L5_MC': 395, 'L5_UTPC': 342, 'L5_TTPC2': 2003, 'L6_MC': 336, 'L6_ChC': 16,
	    'L6_SBC': 67, 'L6_NGC': 17, 'L6_LBC': 463, 'L6_BTC': 54, 'L6_NBC': 198, 'L6_BPC': 3174, 'L6_IPC': 3476,
	    'L6_TPC_L1': 1637, 'L6_DBC': 31, 'L6_TPC_L4': 1440, 'L6_UTPC': 1735, 'L6_BP': 7
	    }

	data = pd.read_json(file_pathways_anatomy_vannilized, orient='index')

	pre_group, post_group = connection_index.split(':')

	conn_groups = data[data.vanni_pre == pre_group][data.vanni_post == post_group]
	pre_groups = conn_groups.markram_pre.unique()
	post_groups = conn_groups.markram_post.unique()

	# Calculate number of neurons in pre & post Markram groups
	N_pre = 0
	N_post = 0

	for pre in pre_groups:
		N_pre += cell_N_dict[pre]

	for post in post_groups:
		N_post += cell_N_dict[post]

	N_possible = N_pre * N_post # Total number of possible connections


	# Calculate total synapse count for Vanni pair
	tot_synapses = conn_groups.total_synapse_count.sum()


	# Calculate connection probability (*)
	N_subgroups = dict()

	for pre in pre_groups:
		for post in post_groups:
			conn = str(pre + ':' + post)
			try:
				N_subgroups[conn] = data.ix[conn].connection_probability * data.ix[conn].neuron_number_pre * data.ix[conn].neuron_number_post
			except KeyError:
				N_subgroups[conn] = 0


	N_expected = sum(N_subgroups.values())
	conn_prob = N_expected / N_possible


	# IIa Calculate weighted average of the means of synapses per connection (** weighing by N_neurons_pre * N_neurons_post, Simo & Vafa)
	weighted_spcs = dict()

	for pre in pre_groups:
		for post in post_groups:
			conn = str(pre + ':' + post) 
			try:
				weighted_spcs[conn] = data.ix[conn].mean_number_of_synapse_per_connection * data.ix[conn].neuron_number_pre * data.ix[conn].neuron_number_post
			except KeyError:
				weighted_spcs[conn] = 0


	sum_weighted_spc = sum(weighted_spcs.values())
	weighted_spc = sum_weighted_spc / N_possible

	po = tot_synapses / (weighted_spc * N_pre * N_post)


	# IIb Calculate weighted average of the means of synapses per connection (*** weighing by N_neurons_pre * N_neurons_post, Henri)
	weighted_spcs2 = dict()

	for pre in pre_groups:
		for post in post_groups:
			conn = str(pre + ':' + post) 
			try:
				weighted_spcs2[conn] = data.ix[conn].connection_probability * data.ix[conn].mean_number_of_synapse_per_connection * data.ix[conn].neuron_number_pre * data.ix[conn].neuron_number_post
			except KeyError:
				weighted_spcs2[conn] = 0


	sum_weighted_spc2 = sum(weighted_spcs2.values())

	spc2_div = dict()
	for pre in pre_groups:
		for post in post_groups:
			conn = str(pre + ':' + post) 
			try:
				spc2_div[conn] = data.ix[conn].connection_probability * data.ix[conn].neuron_number_pre * data.ix[conn].neuron_number_post
			except KeyError:
				spc2_div[conn] = 0

	spc2_divider = sum(spc2_div.values())
	weighted_spc2 = sum_weighted_spc2 / spc2_divider


	# Testing... => IIa and IIb produce roughly the same results - why?
	po = tot_synapses / (N_possible * weighted_spc)
	po2 = tot_synapses / (N_possible * weighted_spc2)

	conn_params = pd.DataFrame(data={'connection_probability': po, 'mean_number_of_synapses_per_connection': weighted_spc, 'total_synapse_count': tot_synapses},index=[connection_index])
	
	return conn_params


# Main

data = pd.read_json(file_pathways_anatomy_vannilized, orient='index')
vanni_connections = data.vanni_index.unique()

frames = [ get_vanni_connection_params(conn) for conn in vanni_connections ]
result = pd.concat(frames)

result.astype(str).to_json(file_pathways_anatomy_vanni, orient='index')