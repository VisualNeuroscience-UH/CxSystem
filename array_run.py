import cortical_system as CX
from brian2 import *
import multiprocessing
import time

class array_run(object):

    def __init__(self,anatomy_df,physiology_df):
        self.anatomy_df = anatomy_df
        self.physiology_df =physiology_df
        self.multidimension_array_run = 0
        # extract multidimension_array_run flag from anatomy config
        if 'multidimension_array_run' in str(self.anatomy_df.values):
            for col in self.anatomy_df.columns:
                if not math.isnan(any(self.anatomy_df[col].str.contains('multidimension_array_run'))):
                    if any(self.anatomy_df[col].str.contains('multidimension_array_run')):
                        multidim_flag_idx = self.anatomy_df[col][self.anatomy_df[col].str.contains('multidimension_array_run') == True].index[0]
                        if '#' not in self.anatomy_df[col][multidim_flag_idx] and '#' not in self.anatomy_df[col][multidim_flag_idx+1]:
                            self.multidimension_array_run = int(self.anatomy_df[col][multidim_flag_idx+1])
                            break
                        else:
                            return

        anatomy_array_search_result = anatomy_df[anatomy_df.applymap(lambda x: True if '|' in str(x) else False)]
        physio_array_search_result = physiology_df[physiology_df.applymap(lambda x: True if '|' in str(x) else False)]
        arrays_idx_anatomy = []
        arrays_idx_physio = []
        for col_idx in anatomy_array_search_result.columns:
            try:
                row_idx = anatomy_array_search_result[col_idx][anatomy_array_search_result[col_idx].str.contains('|') == True].index.tolist()
                for row in row_idx:
                    arrays_idx_anatomy.append((col_idx, row))
            except IndexError:
                pass
        for col_idx in physio_array_search_result.columns:
            try:
                row_idx = physio_array_search_result[col_idx][physio_array_search_result[col_idx].str.contains('|') == True].index.tolist()
                for row in row_idx:
                    arrays_idx_physio.append((col_idx, row))
            except IndexError:
                pass
        self.df_anat_final_array = []
        self.df_phys_final_array = []
        self.final_messages = []
        self.sum_of_array_runs = len(arrays_idx_anatomy) + len(arrays_idx_physio)
        if self.sum_of_array_runs > 1 and not self.multidimension_array_run:
            anatomy_default = self.df_default_finder(anatomy_df)
            physio_default = self.df_default_finder(physiology_df)
        else:
            anatomy_default = anatomy_df
            physio_default = physiology_df
        if self.multidimension_array_run:
            if arrays_idx_anatomy:
                anat_variations, anat_messages = self.df_builder_for_array_run( anatomy_df, arrays_idx_anatomy)
            if arrays_idx_physio:
                physio_variations, physio_messages = self.df_builder_for_array_run( physiology_df, arrays_idx_physio)

            for anat_idx, anat_df in enumerate(anat_variations):
                for physio_idx, physio_df in enumerate(physio_variations):
                    self.df_anat_final_array.append(anat_df)
                    self.df_phys_final_array.append(physio_df)
                    self.final_messages.append(anat_messages[anat_idx]+physio_messages[physio_idx])

        else:
            if arrays_idx_anatomy:
                df_anat_array, anat_messages = self.df_builder_for_array_run(anatomy_df, arrays_idx_anatomy)
                self.df_anat_final_array.extend(df_anat_array)
                self.df_phys_final_array.extend([physio_default for ii in range(len(self.df_anat_final_array))])
                self.final_messages.extend(anat_messages)
            if arrays_idx_physio:
                df_phys_array, physio_messages = self.df_builder_for_array_run(physiology_df, arrays_idx_physio)
                self.df_phys_final_array.extend(df_phys_array)
                self.df_anat_final_array.extend([anatomy_default for ii in range(len(self.df_phys_final_array))])
                self.final_messages.extend(physio_messages)

        print "Array of Dataframes for anatomical and physiological configuration are ready..."
        self.spawner()

    def arr_run(self,idx, working):
        working.value += 1
        np.random.seed(idx)
        print "################### Trial %d started running for %s ##########################" % (idx,self.final_messages[idx][1:])
        cm = CX.cortical_system(self.df_anat_final_array[idx],self.df_phys_final_array[idx],device='Python',output_file_suffix = self.final_messages[idx])
        cm.run()
        working.value -= 1

    def spawner(self):
        number_of_process = 0
        self.do_benchmark = 0
        if 'number_of_process' in str(self.anatomy_df.values):
            for col in self.anatomy_df.columns:
                if not math.isnan(any(self.anatomy_df[col].str.contains('number_of_process'))):
                    if any(self.anatomy_df[col].str.contains('number_of_process')):
                        multidim_flag_idx = self.anatomy_df[col][self.anatomy_df[col].str.contains('number_of_process') == True].index[0]
                        if '#' not in self.anatomy_df[col][multidim_flag_idx] and '#' not in self.anatomy_df[col][multidim_flag_idx+1]:
                            number_of_process = int(self.anatomy_df[col][multidim_flag_idx+1])
                            break
        if number_of_process == 0 :
            number_of_process = int(multiprocessing.cpu_count() * 3/4)
            print "Warning: number_of_process is not defined in the configuration file, the default number of processes are 3/4*number of CPU cores: %d processes" %number_of_process

        if 'do_benchmark' in str(self.anatomy_df.values):
            for col in self.anatomy_df.columns:
                if not math.isnan(any(self.anatomy_df[col].str.contains('number_of_process'))):
                    if any(self.anatomy_df[col].str.contains('number_of_process')):
                        multidim_flag_idx = self.anatomy_df[col][self.anatomy_df[col].str.contains('number_of_process') == True].index[0]
                        if '#' not in self.anatomy_df[col][multidim_flag_idx] and '#' not in self.anatomy_df[col][multidim_flag_idx+1]:
                            self.do_benchmark = int(self.anatomy_df[col][multidim_flag_idx+1])
                            break

        manager = multiprocessing.Manager()
        jobs = []
        working = manager.Value('i', 0)
        number_of_runs = len(self.final_messages)
        assert len(self.final_messages) < 1000 , 'The array run is trying to run more than 1000 simulations, this is not allowed unless you REALLY want it and if you REALLY want it you should konw what to do.'
        while len(jobs) < number_of_runs:
            time.sleep(0.3)
            if working.value < number_of_process:
                p = multiprocessing.Process(target=self.arr_run, args=(len(jobs), working,))
                jobs.append(p)
                p.start()
        for j in jobs:
            j.join()

    def df_builder_for_array_run(self, original_df, index_of_array_variable,message=''):
        array_of_dfs = []
        run_messages = []
        array_variable = original_df[index_of_array_variable[0][0]][index_of_array_variable[0][1]]
        opening_braket_idx = array_variable.index('{')
        if (not self.multidimension_array_run and self.sum_of_array_runs>1) or (self.sum_of_array_runs==1 and ':' in array_variable):
            colon_idx = array_variable.index(':')
            array_variable = array_variable.replace(array_variable[opening_braket_idx + 1:colon_idx + 1],'') # removing default value

        closing_braket_idx = array_variable.index('}')
        template_of_variable = array_variable[:opening_braket_idx] + '^^^' + array_variable[closing_braket_idx + 1:]
        changing_part = array_variable[opening_braket_idx + 1:closing_braket_idx].replace('|', ',')
        tmp_str = 'arange(' + changing_part + ')'
        variables_to_iterate = eval(tmp_str)
        variables_to_iterate = [template_of_variable.replace('^^^', str(vv)) for vv in variables_to_iterate]
        for var in variables_to_iterate:
            temp_df = original_df.copy()
            temp_df[index_of_array_variable[0][0]][index_of_array_variable[0][1]] = var
            if self.multidimension_array_run and len(index_of_array_variable)>1:
                tmp_message = self.message_finder(temp_df, index_of_array_variable)
                temp_df, messages = self.df_builder_for_array_run(temp_df, index_of_array_variable[1:],tmp_message)
            else:
                temp_df = [self.df_default_finder(temp_df)]
                messages = [message+self.message_finder(temp_df[0], index_of_array_variable)]
            array_of_dfs.extend(temp_df)
            run_messages.extend(messages)
        if not self.multidimension_array_run and len(index_of_array_variable)>1:
            temp_df, messages = self.df_builder_for_array_run(original_df, index_of_array_variable[1:])
            array_of_dfs.extend(temp_df)
            run_messages.extend(messages)
        return array_of_dfs, run_messages


    def df_default_finder(self,df_):
        df = df_.copy()
        df_search_result = df[df.applymap(lambda x: True if '|' in str(x) else False)]
        arrays_idx_ = []
        for col_ix in df_search_result.columns:
            row_ix = df_search_result[col_ix][df_search_result[col_ix].str.contains('|') == True].index.tolist()
            for row in row_ix:
                arrays_idx_.append((col_ix, row))
        for to_default_idx in arrays_idx_:
            value_to_default = df[to_default_idx[0]][to_default_idx[1]]
            assert ':' in value_to_default, "The default value should be defined for %s " % value_to_default
            default = value_to_default[value_to_default.index('{')+1:value_to_default.index(':')]
            df[to_default_idx[0]][to_default_idx[1]] = df[to_default_idx[0]][to_default_idx[1]].replace(value_to_default[value_to_default.index('{'):value_to_default.index('}')+1],default)
        return df

    def message_finder(self,df, idx):
        idx = idx[0]
        whitelist = set('abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        try:
            if any(df[0].str.contains('row_type')):
                definition_rows_indices = array(df[0][df[0].str.contains('row_type')].index.tolist())
                target_row = max(where(definition_rows_indices < idx[0])[0])
                title = str(df.loc[target_row][idx[1]])
                value = str(df.loc[idx[0]][idx[1]])
                message = '_' + title + ''.join(filter(whitelist.__contains__, value))
        except KeyError:
            if 'Variable' in df.columns:
                try:
                    if not math.isnan(df['Key'][idx[1]]):
                        title = str(df['Key'][idx[1]])
                        value = str(df[idx[0]][idx[1]])
                    else:
                        title = str(df['Variable'][idx[1]])
                        value = str(df[idx[0]][idx[1]])
                except TypeError:
                    title = str(df['Key'][idx[1]])
                    value = str(df[idx[0]][idx[1]])
                message = '_' + title + ''.join(filter(whitelist.__contains__, value))
        return message

