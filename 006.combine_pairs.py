import numpy as np
from params import basic_params 
import subprocess, os
from params import *#create_json_network_params


"""/!\ Want to weight each station equally, 
so multiply similarity in each 1-component 
station by nvote.
Check example in postprocesing/combine_HecotrMine.sh
"""


if __name__ == '__main__':
    
    p = basic_params()
    subprocess.call(['rm', '-rf', 'data/inputs_network/'])
    subprocess.call(['mkdir', 'data/inputs_network/'])
    print '... copying candidate_pairs*merged.txt to data/inputs_network/\
            because they are going to be deleted.'
    subprocess.call(['cp -r data/waveforms*/fingerprints/candidate_pairs*merged.txt\
            data/inputs_network/'], shell=True)
    os.chdir('postprocessing/')
    comandLine = 'python parse_results.py \
        -d ../data/inputs_network/ \
        -p candidate_pairs_%s \
        --sort true --parse false -c true -t 6'
    
    for sta in p['stalist']:
        cmd = comandLine % (sta)
        print cmd
        process = subprocess.Popen(cmd, 
                stdout=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        print output
        print  ">>> Network detection inputs ready for station %s"% sta
    print  ">>> Network detection inputs ready at ../data/inputs_network/"
    print
    create_json_network_params()
    print  ">>> Network params json ready"



