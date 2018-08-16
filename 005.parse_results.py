import numpy as np
from params import basic_params
import subprocess, os



if __name__ == '__main__':
    
    p = basic_params()
    os.chdir('postprocessing/')
    comandLine = 'python parse_results.py \
        -d ../data/waveforms%s/fingerprints/\
        -p candidate_pairs_%s_%s \
        -i ../data/global_indices/%s_%s_idx_mapping.txt'
    i=0
    for sta in p['stalist']:
        for cha in p['chalist']:
            cmd = comandLine % (sta, sta, cha, sta, cha)
            print cmd
            i+=1
            if i==1:
                continue

            process = subprocess.Popen(cmd,
                    stdout=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            print output
        
