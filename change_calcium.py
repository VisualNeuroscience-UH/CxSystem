from __future__ import division
import numpy as np
from matplotlib import pyplot
import pandas as pd


class ChangeCalcium:
    # TODO create init or not depending how you want to use this class later, instantiation or not
    # steep_group includes all connections between exc cells and DBC, BTC, MC,BP, and between 2 exc cells, K1/2 = 2.79
    # shallow group includes all connections between exc cells and LBC, NBC, SBC, ChC, K1/2 = 1.09
    # all others, K = mean (2.79,1.09)
    # ks Markram cell 2015 suppl fig S11

    def __init__(self):
        # _cell_group_dict = {
        #     'L1_DAC': 'L1_I', 'L1_DLAC': 'L1_I', 'L1_HAC': 'L1_I', 'L1_NGC-DA': 'L1_I', 'L1_NGC-SA': 'L1_I',
        #     'L1_SLAC': 'L1_I',
        #     'L23_BP': 'L23_UM_I', 'L23_BTC': 'L23_UM_I', 'L23_ChC': 'L23_UM_I', 'L23_DBC': 'L23_UM_I', 'L23_LBC': 'L23_BC',
        #     'L23_MC': 'L23_MC', 'L23_NBC': 'L23_BC', 'L23_NGC': 'L23_UM_I', 'L23_PC': 'L23_PC', 'L23_SBC': 'L23_BC',
        #     'L4_BP': 'L4_UM_I', 'L4_BTC': 'L4_UM_I', 'L4_ChC': 'L4_UM_I', 'L4_DBC': 'L4_UM_I', 'L4_LBC': 'L4_BC',
        #     'L4_MC': 'L4_MC', 'L4_NBC': 'L4_BC', 'L4_NGC': 'L4_UM_I', 'L4_PC': 'L4_PC1', 'L4_SBC': 'L4_BC',
        #     'L4_SP': 'L4_PC2',
        #     'L4_SS': 'L4_SS', 'L5_BP': 'L5_UM_I', 'L5_BTC': 'L5_UM_I', 'L5_ChC': 'L5_UM_I', 'L5_DBC': 'L5_UM_I',
        #     'L5_LBC': 'L5_BC', 'L5_MC': 'L5_MC', 'L5_NBC': 'L5_BC', 'L5_NGC': 'L5_UM_I', 'L5_SBC': 'L5_BC',
        #     'L5_STPC': 'L5_PC', 'L5_TTPC1': 'L5_PC', 'L5_TTPC2': 'L5_PC', 'L5_UTPC': 'L5_PC', 'L6_BP': 'L6_UM_I',
        #     'L6_BPC': 'L6_PC1', 'L6_BTC': 'L6_UM_I', 'L6_ChC': 'L6_UM_I', 'L6_DBC': 'L6_UM_I', 'L6_IPC': 'L6_PC1',
        #     'L6_LBC': 'L6_BC', 'L6_MC': 'L6_MC', 'L6_NBC': 'L6_BC', 'L6_NGC': 'L6_UM_I', 'L6_SBC': 'L6_BC',
        #     'L6_TPC_L1': 'L6_PC2', 'L6_TPC_L4': 'L6_PC1', 'L6_UTPC': 'L6_PC1',
        # }
        _excitatory_markram_groups = ['L23_PC','L4_PC','L4_SP','L4_SS','L5_STPC','L5_TTPC1','L5_TTPC2','L5_UTPC','L6_IPC',
                                      'L6_BPC', 'L6_TPC_L1','L6_TPC_L4','L6_UTPC']

        _steep_post_inhibitory_groups = ['L23_DBC','L4_DBC','L5_DBC','L6_DBC','L23_BTC','L4_BTC','L5_BTC','L6_BTC','L23_MC',
                                         'L4_MC','L5_MC','L6_MC','L23_BP','L4_BP','L5_BP','L6_BP']

        _shallow_post_inhibitory_groups = ['L23_LBC','L4_LBC','L5_LBC','L6_LBC','L23_NBC','L4_NBC','L5_NBC','L6_NBC','L23_SBC',
                                         'L4_SBC','L5_SBC','L6_SBC','L23_ChC','L4_ChC','L5_ChC','L6_ChC']

        self._excitatory_markram_groups = _excitatory_markram_groups
        self._synaptic_efficiency_dict = {
            'steep_post' : _excitatory_markram_groups + _steep_post_inhibitory_groups,
            'shallow_post' : _shallow_post_inhibitory_groups }

    
        # self._own2markram_group_dict = self._InvertGroupDict(_cell_group_dict)

        file_pathways_anatomy_vannilized = 'pandas_playground/pathways_anatomy_vannilized.json'  # OUTPUT FILE

        self._data = pd.read_json(file_pathways_anatomy_vannilized, orient='index')

    def GetSynapseStrength(self,original_synapse_strength, own_connection,Ca=2.0):
        # The original synapse strength (with no units) is assumed to represent the value at [Ca] = 2 mM
        # First map from own connection to markram connections. Next select DataFrame with markram_pre column =
        # _excitatory_markram_groups and markram_post column = either steep_post, shallow_post or other.
        #  These selections map to K12. Calculate the mean of K12 values. Finally calculate final_synapse_strength
        # for own connection and original synapse strength.

        data=self._data # shorten

        # Select data matching own connection
        markram_connections = data[data['vanni_index'] == own_connection]

        assert not markram_connections.empty, 'No matching connections, a typo or missing matching Markram connection'
        markram_pres = markram_connections['markram_pre']
        markram_posts = markram_connections['markram_post']

        if all(markram_pres.isin(self._excitatory_markram_groups)) and all(markram_posts.isin(self._synaptic_efficiency_dict['steep_post'])):
            K12 = 2.79
        elif all(markram_pres.isin(self._excitatory_markram_groups)) and all(markram_posts.isin(self._synaptic_efficiency_dict['shallow_post'])):
            K12 = 1.09
        else:
            K12 = np.average([2.79, 1.09])

        Ca0=2.0
        # Calculate final synapse strength
        final_synapse_strength =  original_synapse_strength * (np.power(Ca,4)/(np.power(K12,4) + np.power(Ca,4)))
        final_synapse_strength_at_Ca2 = original_synapse_strength * (np.power(Ca0, 4) / (np.power(K12, 4) + np.power(Ca0, 4)))

        relative_final_synapse_strength = final_synapse_strength / final_synapse_strength_at_Ca2

        # Return
        return Ca, final_synapse_strength, relative_final_synapse_strength

    # def _InvertGroupDict(self,_cell_group_dict):
    #     # Inverts the cell group markram2own mapping to own2markram mapping
    #     own_cell_groups = set(_cell_group_dict.values())
    #
    #     # Map own cell groups to Markram cell groups
    #     markram_groups_tmp = []
    #     own2markram_group_dict = {}
    #     for own_cell_group in own_cell_groups:
    #         [markram_groups_tmp.append(name) for name, group in _cell_group_dict.items() if
    #          group == own_cell_group]  # search cell_group_dict by value
    #         own2markram_group_dict[own_cell_group] = markram_groups_tmp
    #         markram_groups_tmp = []
    #     return own2markram_group_dict


if __name__ == '__main__':
    Ca_obj= ChangeCalcium()
    Ca = np.arange(0.7, 5, 0.1)

    Ca, fss, rfss = Ca_obj.GetSynapseStrength(1,'L23_PC:L23_MC',Ca)
    # Units are nano Siemens (nS), and range is 0.11 to 1.5 nS (Markram 2015 Cell, Figure 10)
    # Total conductance about 1 microS, 3/4 excitatory, 1/4 inhibitory

    # Testing
    pyplot.plot(Ca,rfss, color='blue', lw=2)
    pyplot.xscale('log')
    pyplot.yscale('log')
    pyplot.xlim([0.7, 5])
    pyplot.ylim([0.03, 10])
    pyplot.show()