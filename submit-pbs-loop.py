import commands
from popen2 import popen2
import time, glob, os, sys
import subprocess
from params import basic_params

def run(p):
  k=0
  for sta in p['stalist']:
     for cha in p['chalist']:
        comandLine = 'python postprocessing/parse_results.py \
                 -d data/waveforms%s/fingerprints/\
                 -p candidate_pairs_%s_%s \
                 -i data/global_indices/%s_%s_idx_mapping.txt'
        k+=1
        cmd = comandLine % (sta, sta, cha, sta, cha)
        print cmd
        if k !=10 : continue
        print cmd
        #print comps, sta.station, date
        # Open a pipe to the qsub command.
        output, input = popen2('qsub')
        # Customize your options here
        job_name = sta+'.'+cha
        nnodes = 16 
        processors = "nodes=1:ppn=%s"%nnodes
        command = cmd #"002.CorrelBinsSingleRotation.py -p %s -d %s -s %s -c %s -t %s -v" %(path, date, target, comps,  nthreads)
        node = 'beroza'
        print os.getcwd()
        job_string = """
        #!/bin/bash\n\
        #PBS -N %s\n\
        #PBS -q %s\n\
        #PBS -l %s\n\
        #PBS -o out/%s.out\n\
        #PBS -e out/%s.err\n\
        cd $PBS_O_WORKDIR\n\
        %s""" % (job_name, node, processors, job_name, job_name, command)
        
        # Send job_string to qsub
        input.write(job_string)
        input.close()
        
        # Print your job and the system response to the screen as it's submitted
        print job_string
        print output.read()
        time.sleep(1.0000)
        print os.getcwd()
        
#        os.system('echo "%s %s %s" >> o.txt'%(bin, target, k ))
        njob = int(commands.getoutput('qstat -u zspica | wc -l'))
        while njob >= 10:
            njob = int(commands.getoutput('qstat -u zspica | wc -l'))
            time.sleep(60)


if __name__=='__main__':
    try: os.makedirs('out/')
    except: pass
    # Loop over your jobs
    
    p = basic_params()
#    os.chdir('postprocessing/')
    
    
    run(p)
#    binfiles = dubble_check(binfiles)
#    print binfiles
    #run(binfiles,stations)
   # binfiles = error_check()
   # run(binfiles,stations)
    
