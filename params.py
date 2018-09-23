#!/usr/bin/env python
import glob, os, json
from obspy import read, UTCDateTime
import numpy as np
from parse_config import parse_json

"""
This is the main file with all the parameters existing 
in FAST. You only need to change this file and all other
functions used will be updated following the params here. 
All params are described here after but please refere to 
the user manual for more details. 

raw_path: str: where are the data sorted in SDS format
days: np.array: array of int(days) to compute
min_freq: int: min frequency
max_freq: int: max frequency
resample: bool: if True uses the resample function - else decimate 
                and div_factor
div_factor: int: used if decimate
sampling_rate: int: goal sampling rate of the traces
network: str: initial of the network 
stalist: list of str: list of station to compute
chalist: list of str: list of channel to compute. #this probably will be update int the future

"""





def basic_params():
    # Preprocessing params
    # ---------------------
    """
    Params for 001.preprocessing.py
    These params must be adjusted before playing 
    with any data set. Most important params for 
    the code to run well. 
    """
    p = {}
    ####basic config####
    p['raw_path'] = '/data/lawrence2/zspica/FAST_LOP/raw/'
    p['days'] = np.arange(284,330,1)
    p['min_freq'] = 3
    p['max_freq'] = 12
    p['resample'] = False #If False ==> decimate by div_factor else take sampling_rate
    p['div_factor'] = 5
    p['sampling_rate']= 25 #must be concordant wth div_factor and init samp rate
    p['network'] = 'TA'
    p['stalist'] = get_sta_from_txt()
    p['chalist'] = ['HHZ']
    return p 


def get_params_fp(net, sta, cha):
    #get configuration
    p = {}
    b = basic_params()
    ####fp files cofig####
    #fingerprint
    p['sampling_rate']= b['sampling_rate']# 
    p['min_freq']= b['min_freq']#
    p['max_freq']= b['max_freq']#
    p['spec_length']= 6.0
    p['spec_lag']= 0.12 
    p['fp_length']= 64 
    p['fp_lag']= 10
    p['k_coef']= 400
    p['nfreq']= 32
    p['mad_sampling_rate']=  0.1 
    p['mad_sample_interval']= 86400
    #performance
    p['num_fp_thread']= 12
    p['partition_len']= 86400 
    #data
    p['network']= net#
    p['station']= sta#
    p['channel']= cha#
    p['folder']= os.getcwd()+'/data/waveforms%s/'%sta# 
    p['starttime']= get_starttime(sta, cha, p['folder'])# 
    p['endtime']= get_endtime(sta, cha, p['folder'])#
    p['fp_files']= get_fp_files(sta, cha, p['folder'])#
    p['MAD_sample_files']= get_fp_files(sta, cha, p['folder'])#
    return p


def get_params_general_fp_config():
    #get config
    p = {}
    ####config.json - main fp params####
    #lsh_params
    p['ntbl']= 100
    p['nhash']= 4
    p['nvote']= 2
    p['nthread']= 12
    p['npart']= 1
    p['repeat']= 5
    p['noise_freq'] = 0.01
    #io
    p['base_dir']= 'data/'
    p['global_index_dir']= 'global_indices/'
    p['fp_param_dir']= 'parameters/fingerprint/'
    p['simsearch_param_dir']= 'parameters/simsearch/'
    p['fp_params']= fp_json_list()
    return p


def get_network_params():
    #get config
    b = basic_params()
    p = {}
    ####config.json####
    #network
    p['max_fp'] = get_max_fp()
    p['dt_fp'] = 1.2#fp_lag*spec_lag
    p['dgapL'] = 3
    p['dgapW'] = 3
    p['num_pass'] = 2
    p['min_dets'] = 4
    p['min_sum_multiplier'] = 1
    p['max_width'] = 8
    p['ivals_thresh'] = 6
    p['nsta_thresh'] = 2
    p['input_offset'] = 3
    #performace
    p['partition_size'] = 2147483648
    p['partition_gap'] = 5
    p['num_cores'] = 6
    #io
    p['channel_vars'] = b['stalist'] 
    p['fname_template'] = 'candidate_pairs_%s_combined.txt'
    p['base_dir'] = '../data/'
    p['data_folder']=  'inputs_network/'
    p['out_folder'] = 'network_detection/'
    return p


####Fill params functions####
def get_fp_files(sta, cha, folder, basename_only=True):
    g = glob.glob(folder+'*%s*%s*'%(sta, cha))
    for f in g: 
        if f.endswith('.json'): 
            g.remove(f)
    if basename_only:
        files = []
        for f in sorted(g): # attention a ce que l ordre soit bon!
            files.append(os.path.basename(f))
    else:
        files = sorted(g)
    return files        


def get_starttime(sta, cha, folder):
    files = get_fp_files(sta, cha, folder, basename_only=False)
    starttime = read(files[0],headonly=True)[0].stats.starttime
    return str(starttime)[:-5]


def get_endtime(sta, cha, folder):
    files = get_fp_files(sta, cha, folder, basename_only=False)
    endtime = read(files[-1],headonly=True)[0].stats.endtime
    return str(endtime)[:-5]


def fp_json_list():
    g = sorted(glob.glob('parameters/fingerprint/fp_input*.json'))
    files = []
    for f in g: 
        files.append(os.path.basename(f))
    return files
   

def get_max_fp():
    g = glob.glob('../data/global_indices/*mapping.txt')
    fps = []
    for f in g:
        fps.append(int(open(f,'r').readlines()[-1]))
    return np.max(fps)

def get_first_time():
    #get global starttime for all channels
    fl = open('data/global_indices/global_idx_stats.txt').readlines()[0]
    init_time = UTCDateTime(fl)
    return init_time

def get_sta_from_txt():
    m = np.loadtxt('stations.txt',dtype={'names': ('a', 'b', 'c', 'd', 'e'),
                    'formats': ('|S15', np.float, np.float, np.float, np.float)})
    stations = m['a']
    stalist = [] 
    for sta in stations:
        s = sta.split('.')[1]
        stalist.append(s)
    return stalist
    


def get_all_sta():
    g = glob.glob('data/wave*')
    n = []
    for f in g:
        bn = os.path.basename(f)
        n.append(bn.split('waveforms')[1])
    return n

###Make json params functions####
def remove_old_json():
    os.system('rm -rf parameters/fingerprint/*.json')
    os.system('rm -rf config.json')
    os.system('rm -rf simsearch/simsearch_param.json') 


def create_json_fp(net, sta, cha):

    p = get_params_fp(net, sta, cha)
    f = {'fingerprint':
            {'sampling_rate': int('%s'%p['sampling_rate']),
            'min_freq': float('%s'%p['min_freq']),
            'max_freq': float('%s'%p['max_freq']), 
            'spec_length': float('%s'%p['spec_length']),
            'spec_lag': float('%s'%p['spec_lag']),
            'fp_length': int('%s'%p['fp_length']),
            'fp_lag': int('%s'%p['fp_lag']),
            'k_coef': int('%s'%p['k_coef']),
            'nfreq': int('%s'%p['nfreq']),
            'mad_sampling_rate': float('%s'%p['mad_sampling_rate']),
            'mad_sample_interval': float('%s'%p['mad_sample_interval'])
            },
        'performance':
            {'num_fp_thread': int('%s'%p['num_fp_thread']),
            'partition_len': int('%s'%p['partition_len'])
            },
        'data': 
            {'station': p['station'],
            'channel': p['channel'],
            'start_time': p['starttime'],
            'end_time': p['endtime'],
            'folder': p['folder'],
            'fingerprint_files': p['fp_files'],
            'MAD_sample_files': p['MAD_sample_files']
            }
        }
    try: os.makedirs('parameters/fingerprint/')
    except:pass
    with open('parameters/fingerprint/fp_input_%s_%s_%s.json'%(p['network'], p['station'],\
            p['channel']), 'w') as outfile:  
        json.dump(f, outfile, sort_keys=True, indent=4)
    print "... json file for: %s.%s.%s"%(net, sta, cha)


def create_json_general_fp_config():

    p = get_params_general_fp_config()
    f = {'lsh_param':
            {'ntbl': int('%s'%p['ntbl']),
            'nhash': int('%s'%p['nhash']),
            'nvote': int('%s'%p['nvote']),
            'nthread': int('%s'%p['nthread']),
            'npart': int('%s'%p['npart']),
            'noise_freq': float('%s'%p['noise_freq']),
            'repeat': int('%s'%p['repeat'])
            },
        'io':
            {'base_dir': p['base_dir'],
            'global_index_dir': p['global_index_dir'],
            'fp_param_dir': p['fp_param_dir'],
            'simsearch_param_dir': p['simsearch_param_dir'],
            'fp_params': p['fp_params']
            }
        }
    with open('config.json', 'w') as outfile:  
        json.dump(f, outfile, sort_keys=True, indent=4)
    print "... json file fp | done"


def create_json_simsearch_config():

    p = get_params_general_fp_config()
    print "... json file for simsearch | done"
    f = {'fp_param_dir': "../"+p['fp_param_dir'],
        'fp_params': p['fp_params'],
        'lsh_param':
            {'ntbl': int('%s'%p['ntbl']),
            'nhash': int('%s'%p['nhash']),
            'nvote': int('%s'%p['nvote']),
            'nthread': int('%s'%p['nthread']),
            'npart': int('%s'%p['npart']),
            'noise_freq': float('%s'%p['noise_freq'])
            }
        }
    try: os.makedirs('simsearch/')
    except:pass
    with open('simsearch/simsearch_param.json', 'w') as outfile:  
        json.dump(f, outfile, sort_keys=True, indent=4)


def create_json_network_params():
    p = get_network_params() 
    f = {'network':
            {'max_fp': p['max_fp'],
            'dt_fp': float('%s'%p['dt_fp']),
            'dgapL': int('%s'%p['dgapL']),
            'dgapW': int('%s'%p['dgapW']),
            'num_pass': int('%s'%p['num_pass']),
            'min_dets': int('%s'%p['min_dets']),
            'min_sum_multiplier': int('%s'%p['min_sum_multiplier']),
            'max_width': int('%s'%p['max_width']),
            'ivals_thresh': int('%s'%p['ivals_thresh']),
            'nsta_thresh': int('%s'%p['nsta_thresh']),
            'input_offset': int('%s'%p['input_offset'])
            },
        'performance':
            {'partition_size': int('%s'%p['partition_size']),
            'partition_gap': int('%s'%p['partition_gap']),
            'num_cores': int('%s'%p['num_cores'])
            },
        'io':
            {'channel_vars': p['channel_vars'],
            'fname_template': p['fname_template'],
            'base_dir': p['base_dir'],
            'data_folder': p['data_folder'],
            'out_folder': p['out_folder']
            }
        }
    print "... json file for network params | done"
    with open('network_params.json', 'w') as outfile:  
        json.dump(f, outfile, sort_keys=True, indent=4)


def create_json_global_index():
    p = get_params_general_fp_config()
    f = {'fp_param_dir': "../"+p['fp_param_dir'],
            'fp_params': p['fp_params'],
            'index_folder': '../data/global_indices/'
            }
    print "... json file for global_index | done"
    with open('parameters/fingerprint/global_indices.json', 'w') as outfile:  
        json.dump(f, outfile, sort_keys=True, indent=4)



if __name__=='__main__':
    net = 'NL'
    sta = 'G144'
    cha = 'HHZ'
    #get_all_sta()
    get_sta_from_txt()
    #get_network_params()
    #get_first_time()
    #Pget_max_fp()
    #p = get_params_fp(net, sta, cha)
    #print p
    #t0 = get_starttime('G144', 'HHZ', os.getcwd()+'/data/waveforms%s/'%sta)
    #t1 = get_endtime('G144', 'HHZ',   os.getcwd()+'/data/waveforms%s/'%sta)
    #print t1, t0, type(t0)
    #tdelta = UTCDateTime(t1)-UTCDateTime(t0)
    #print tdelta/5
    #print params
    #print filters

#EDF
