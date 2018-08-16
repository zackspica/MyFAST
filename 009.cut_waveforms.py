import numpy as np
from obspy import read, UTCDateTime
import glob, os
import matplotlib
matplotlib.use('Agg')


input_dir = 'data/network_detection/'
output_plot_dir = 'data/network_detection/plots'
output_eq_dir = 'data/network_detection/eqs'
nsta = 8
nstathresh = 2


if not os.path.exists(output_plot_dir):
    os.makedirs(output_plot_dir)
if not os.path.exists(output_eq_dir):
    os.makedirs(output_eq_dir)

network_bn = '%ssta_%sstathresh'%(nsta, nstathresh)
UTCDTfn = 'UTCDateTime_list_%s.txt'%(network_bn)


[fp_time, starttime, endtime, jd, dL, nevents, nsta, \
tot_ndets, max_ndets, tot_vol, max_vol, peaksum, \
num_sta, diff_ind] = np.loadtxt(input_dir+UTCDTfn, unpack=True)
# to avoid loading traces too many time
# we sort them by julday and load one 
# day at a time
a = np.argsort(jd)
# all used array must be sorted as well
juldays = jd[a]
starttime = starttime[a]
endtime = endtime[a]
num_sta = num_sta[a]
peaksum = peaksum[a]

i = 0
for k, jd in enumerate(juldays):
    if i != jd:
        g = glob.glob('data/waveforms*/*%03d.mseed'%jd)
        print '... Loading %s traces for julian day %03d'%(len(g), jd) 
        st = read('data/waveforms*/*%03d.mseed'%jd)
        i = jd
    else:
        print '... Traces already loaded'
    if a[k]>300:continue
    st_slice = st.slice(UTCDateTime(starttime[k]), UTCDateTime(endtime[k]))
    fn = 'rank_'+format(a[k],'04d')+'_nsta_'+str(int(num_sta[k]))+'_pks_'+str(int(peaksum[k]))\
    +'_'+UTCDateTime(starttime[k]).strftime('%Y-%m-%dT%H:%M:%S')

    st_slice.write(os.path.join(output_eq_dir, fn+'.mseed'), format='MSEED' )
#    st_slice.plot(equal_scale=False, outfile=os.path.join(output_plot_dir, fn+'.png'), show=False)
    print a[k] 








