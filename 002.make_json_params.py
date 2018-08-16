import json
import os, glob
from params import *




if __name__=='__main__':
    print
    p = basic_params()
    print '>>> Running jason_params'
    stalist = p['stalist']
    chalist = p['chalist']
    net = p['network']
    remove_old_json()
    for sta in stalist:
        for cha in chalist:
            create_json_fp(net, sta, cha)
    create_json_global_index()
    create_json_general_fp_config()
    create_json_simsearch_config()
