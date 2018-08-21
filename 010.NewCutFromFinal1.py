import numpy as np
from obspy import read, UTCDateTime, Stream
import glob, os, sys
import matplotlib.pyplot as plt
from params import get_first_time

input_dir = 'data/network_detection/'
output_plot_dir = 'data/network_detection/plots'
output_eq_dir = 'data/network_detection/eqs'
nsta = 18
nstathresh = 2
file = 'sorted_FinalNetDetTimes_%ssta_%sstathresh.txt'%(nsta, nstathresh)


if not os.path.exists(output_plot_dir):
    os.makedirs(output_plot_dir)
if not os.path.exists(output_eq_dir):
    os.makedirs(output_eq_dir)




if len(sys.argv) != 3:
   print "Usage: python PARTIALplot_detected_waveforms_Okmok.py <start_ind> <end_ind>"
   sys.exit(1)

IND_FIRST = int(sys.argv[1])
IND_LAST = int(sys.argv[2])
print "PROCESSING:", IND_FIRST, IND_LAST
         

# Inputs
times_dir = 'data/network_detection/'
[det_start_ind, det_end_ind, dL, nevents, nnsta, tot_ndets, max_ndets, tot_vol, max_vol, peaksum,\
num_sta, diff_ind] = np.loadtxt(times_dir+file,\
usecols=(0,1,2,3,4,5,6,7,8,9,10,11), unpack=True)

ss = np.loadtxt(times_dir+file, usecols=(np.arange(12,nsta+12)), unpack=True)
stations = np.loadtxt(times_dir+'station_order.txt', dtype='str')


# Times   
dt_fp = 1.2
det_times = dt_fp * det_start_ind
diff_times = dt_fp * diff_ind
dL_dt = dt_fp * dL
print len(det_times)

# Window length (seconds) for event plot
init_time = UTCDateTime('2016-10-10T08:55:06.840000') # global start time for all channels
wtime_before = 5 
wtime_after = 20

# Plot dimensions
out_width = 800
out_height = 2000

# Read in data and plot
ts_dir = 'raw/'


for kk in range(IND_FIRST, IND_LAST):
    ev_time = init_time + det_times[kk]
    start_time = ev_time - wtime_before
    end_time = ev_time + wtime_after
    print ev_time, start_time, end_time
    if (diff_times[kk] > wtime_after): # special case: unusually long delay between start and end times
        end_time = ev_time + diff_times[kk] + wtime_after
    jday_start = start_time.julday
    jday_end = end_time.julday
    if (jday_start != jday_end):
        print "Warning: start and end day not equal", kk, jday_start, jday_end

    stalist = []
    st =Stream()
    if int(peaksum[kk])<150:continue
    for s, sta in zip(ss[:,kk], stations):
        if np.isnan(s):continue
        else:st += read(ts_dir+'%03d/*%s*.mseed'%(jday_start, sta), format='MSEED')

    #st = read(ts_dir+'%03d/*.mseed'%jday_start, format='MSEED')
    print len(st)
    print st.__str__(extended=True)

    st_slice = st.slice(start_time, end_time)

    out_file = 'event_rank'+format(kk,'05d')+'_nsta'+str(int(num_sta[kk]))\
    +'_peaksum'+str(int(peaksum[kk]))+'_ind'+str(int(det_start_ind[kk]))+'_time'\
    +str(det_times[kk])+'_'+ev_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
    st_slice.write(os.path.join(output_eq_dir, out_file+'.mseed'), format='MSEED' )
    if plot:
        st_slice.plot(equal_scale=False, size=(out_width,out_height), outfile=out_file)
