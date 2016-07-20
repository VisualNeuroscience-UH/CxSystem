import pandas as pd

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

pre_group = 'L5_MC'
post_group = 'L5_PC'

data = pd.read_json('pathways_anatomy_vanni.json', orient='index')

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

N_possible = N_pre * N_post


# Calculate total synapse count for Vanni pair
tot_synapses = conn_groups.total_synapse_count.sum()


N_subgroups = dict()
s_subgroups_possible = dict()
N_expected = 0
s_possible = 0
for pre in pre_groups:
	for post in post_groups:
		conn = str(pre + ':' + post)
		try:
			N_subgroups[conn] = data.ix[conn].connection_probability * data.ix[conn].neuron_number_pre * data.ix[conn].neuron_number_post
			s_subgroups_possible[conn] = data.ix[conn].mean_number_of_synapse_per_connection * data.ix[conn].neuron_number_pre * data.ix[conn].neuron_number_post
		except KeyError:
			N_subgroups[conn] = 0
			s_subgroups_possible[conn] = 0

		N_expected += N_subgroups[conn]
		s_possible += s_subgroups_possible[conn]

s = s_possible/ (len(pre_groups)*len(post_groups))

conn_prob_oma = tot_synapses / s_possible

conn_prob = N_expected / N_possible

 