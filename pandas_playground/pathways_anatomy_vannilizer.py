# Sketchy code for adding parameters to Markram's set of connections according to Vanni simplification
# Creates a json file similar to the original pathways_anatomy_factsheets_simplified.json
# Henri Hokkanen 21 July 2016

import pandas as pd

file_pathways_anatomy_markram = 'pathways_anatomy_factsheets_simplified.json' # INPUT FILE, from https://bbp.epfl.ch/nmc-portal/downloads
file_pathways_anatomy_vannilized = 'pathways_anatomy_vannilized.json' # OUTPUT FILE


# Mapping from Markram et al cell groups to own cell groups
cell_group_dict = {
    'L1_DAC': 'L1_I', 'L1_DLAC': 'L1_I', 'L1_HAC': 'L1_I', 'L1_NGC-DA': 'L1_I', 'L1_NGC-SA': 'L1_I', 'L1_SLAC': 'L1_I',
    'L23_BP': 'L23_UM_I', 'L23_BTC': 'L23_UM_I', 'L23_ChC': 'L23_UM_I', 'L23_DBC': 'L23_UM_I', 'L23_LBC': 'L23_BC',
    'L23_MC': 'L23_MC', 'L23_NBC': 'L23_BC', 'L23_NGC': 'L23_UM_I', 'L23_PC': 'L23_PC', 'L23_SBC': 'L23_BC',
    'L4_BP': 'L4_UM_I', 'L4_BTC': 'L4_UM_I', 'L4_ChC': 'L4_UM_I', 'L4_DBC': 'L4_UM_I', 'L4_LBC': 'L4_BC',
    'L4_MC': 'L4_MC', 'L4_NBC': 'L4_BC', 'L4_NGC': 'L4_UM_I', 'L4_PC': 'L4_PC1', 'L4_SBC': 'L4_BC', 'L4_SP': 'L4_PC2',
    'L4_SS': 'L4_SS', 'L5_BP': 'L5_UM_I', 'L5_BTC': 'L5_UM_I', 'L5_ChC': 'L5_UM_I', 'L5_DBC': 'L5_UM_I',
    'L5_LBC': 'L5_BC', 'L5_MC': 'L5_MC', 'L5_NBC': 'L5_BC', 'L5_NGC': 'L5_UM_I', 'L5_SBC': 'L5_BC',
    'L5_STPC': 'L5_PC', 'L5_TTPC1': 'L5_PC', 'L5_TTPC2': 'L5_PC', 'L5_UTPC': 'L5_PC', 'L6_BP': 'L6_UM_I',
    'L6_BPC': 'L6_PC1', 'L6_BTC': 'L6_UM_I', 'L6_ChC': 'L6_UM_I', 'L6_DBC': 'L6_UM_I', 'L6_IPC': 'L6_PC1',
    'L6_LBC': 'L6_BC', 'L6_MC': 'L6_MC', 'L6_NBC': 'L6_BC', 'L6_NGC': 'L6_UM_I', 'L6_SBC': 'L6_BC',
    'L6_TPC_L1': 'L6_PC2', 'L6_TPC_L4': 'L6_PC1', 'L6_UTPC': 'L6_PC1',
    }

# Number of neurons of each Markram cell group
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


data = pd.read_json(file_pathways_anatomy_markram, orient='index') 

# Split connection names (eg. L6_UTPC:L6_IPC) into two columns -> markram_pre, markram_post
markram_to_vanni = data.index.str.extract('(.*):(.*)', expand=True)
markram_to_vanni.index = data.index
markram_to_vanni.columns = ['markram_pre', 'markram_post']

# Get corresponding Vanni neuron groups & create "Vanni index, eg. L6_PC1:L6_PC1"
markram_to_vanni['vanni_pre'] = markram_to_vanni['markram_pre'].map(cell_group_dict)
markram_to_vanni['vanni_post'] = markram_to_vanni['markram_post'].map(cell_group_dict)
markram_to_vanni['vanni_index'] = markram_to_vanni['vanni_pre'] + ':' + markram_to_vanni['vanni_post']

# Get number of neurons pre and post Markram neuron groups
markram_to_vanni['neuron_number_pre'] = markram_to_vanni['markram_pre'].map(cell_N_dict)
markram_to_vanni['neuron_number_post'] = markram_to_vanni['markram_post'].map(cell_N_dict)

# Also extract cell types (both Markram and Vanni) -- TODO!


# Extract layer & Markram cell type info
pre_layers = markram_to_vanni['markram_pre'].str.extract('^(\w{2,3})_(.*)$', expand=True)
post_layers = markram_to_vanni['markram_post'].str.extract('^(\w{2,3})_(.*)$', expand=True)

pre_layers.columns = ['layer_pre', 'markram_pre_celltype']
post_layers.columns = ['layer_post', 'markram_post_celltype']

# Extract Vanni cell type info
celltypes_post = markram_to_vanni['vanni_pre'].str.extract('^(\w{2,3})_(.*)$', expand=False)

celltypes_pre =  markram_to_vanni['vanni_post'].str.extract('^\w{2,3}_(.*)$', expand=False) 




# Join em all!
data = data.join(markram_to_vanni)
data = data.join(pre_layers)
data = data.join(post_layers)


data.astype(str).to_json(file_pathways_anatomy_vannilized, orient='index')