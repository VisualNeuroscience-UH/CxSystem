__author__ = 'V_AD'
import numpy as np
import pandas as pd
import os

vanni_data = pd.read_json(os.path.abspath('./pathways_anatomy_vannilized.json'),  orient='index')
henry_data = pd.read_json(os.path.abspath('./pathways_anatomy_vanni.json'), orient='index')
with open('./generated_config_file.csv', 'w') as config_file:
    config_file.write('row_type,sys_mode,do_optimize\n')
    config_file.write('params,local,0\n')
    config_file.write('row_type,idx,path,freq,monitors\n')
    config_file.write('IN,0, ./V1_input_layer_2015_10_30_11_7_31.mat ,190*Hz ,[Sp]\n')
    config_file.write('row_type,idx, number_of_neurons, neuron_type, layer_idx, net_center, monitors\n')
    group_index=1
    NG_options = {
        'L1_I': 'L1i',
        '_BC': 'BC',
        '_MC': 'MC',
        '_PC': 'PC',
        '_SS': 'SS',
        '_UM_I': 'UMi',
    }
    layer_options = {
        '1': '1',
        '23': '2',
        '4': '4',
        '5': '5',
        '6': '6',
    }
    PC_layer_options = {
        '2' : '1',
        '41': '2',
        '42': '1',
        '5': '1',
        '61': '4',
        '62' : '1',
    }
    default_center = '5+0j'
    default_NG_monitor = ',N/A'
    group_items = []
    for item in vanni_data['vanni_pre'].unique():
        layer_str = item[0:item.index('_')]
        layer_idx = [layer_options[lay] for lay in layer_options.keys() if lay in layer_str][0]
        N_type = [NG_options[opt] for opt in NG_options.keys() if opt in item][0]
        if N_type == 'PC':
            if len(item[item.index('_')+1:])>2:
                layer_idx = '[' + layer_idx + '->' + PC_layer_options[layer_idx+item[item.index('_')+1:][2]] + ']'
            else:
                layer_idx = '[' + layer_idx + '->1]'
        NN = sum(np.unique(vanni_data.ix[np.where(vanni_data['vanni_pre'] == item)[0]]['neuron_number_pre']))
        line = 'G,%d,%d,%s,%s,%s%s\n' %(group_index,NN,N_type,layer_idx,default_center, default_NG_monitor )
        group_index+=1
        config_file.write(line)
        group_items.append(item)
    config_file.write('row_type,receptor,pre_syn_idx,post_syn_idx,syn_type,p,n,monitors,percentage\n')
    syn_num = len(henry_data[:])
    receptor_options={
        '_I' : 'gi',
        '_BC' : 'gi',
        '_MC' : 'gi',
        '_SS' : 'ge',
        '_PC' : 'ge',
    }
    default_syn_type = 'Fixed'
    default_syn_monitor = 'N/A'
    for syn_index in range(0,syn_num):
        line = 'S,ge,0,1,Fixed,0.043,N/A,[St]wght[rec](0-20),0.60'
        line = 'S,'
        syn_name = henry_data.ix[syn_index].name
        syn_name_pre = syn_name[0:syn_name.index(':')]
        syn_name_post = syn_name[syn_name.index(':')+1:]
        receptor =  [receptor_options[NG_type] for NG_type in receptor_options.keys() if NG_type in syn_name_pre][0]
        line += receptor + ','
        pre_group_item = [it for it in group_items if syn_name_pre == it][0]
        pre_group_idx = group_items.index(pre_group_item)
        post_group_item = [it for it in group_items if syn_name_post == it][0]
        post_group_idx = group_items.index(post_group_item)
        line+= '%d'%pre_group_idx + ','
        line+= '%d'%post_group_idx + ','
        line+= default_syn_type+ ','
        line+= '%f'%henry_data.ix[syn_index]['connection_probability']+ ','
        line += '%d' % henry_data.ix[syn_index]['mean_number_of_synapses_per_connection'] + ','
        line += default_syn_monitor + '\n'
        config_file.write(line)


        # _mapping = {
#     u'L1_I': 'L1i',
#     u'L23_UM_I': 'UMi',
#     u'L23_BC' : 'BC',
#     u'L23_MC':'MC',
#     u'L23_PC':'PC',
#     u'L4_UM_I':'UMi',
#     u'L4_BC':'BC',
#     u'L4_MC':'MC',
#     u'L4_PC1':'PC',
#     u'L4_PC2':'PC',
#     u'L4_SS':'SS',
#     u'L5_UM_I':'UMi',
#     u'L5_BC':'BC',
#     u'L5_MC':'MC',
#     u'L5_PC':'PC',
#     u'L6_UM_I':'UMi',
#     u'L6_PC1':'PC1',
#     u'L6_BC':'BC',
#     u'L6_MC':'MC',
#     u'L6_PC2':'PC,'
# }