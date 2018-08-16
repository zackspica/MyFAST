import subprocess, os

os.chdir('postprocessing/')
subprocess.call(['cp -r ../parameters/network/* .'], shell=True)
cmd = 'python scr_run_network_det.py network_params.json'
print 
print cmd
process = subprocess.Popen(cmd,
        stdout=subprocess.PIPE, shell=True)
output, error = process.communicate()
print output
print
print '>>> Clean up results from network detection'



