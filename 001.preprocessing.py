# -*- coding: utf-8 -*-
from obspy import read
import glob, os
import numpy as np
from params import * 
from statsmodels import robust

"""
Simple script to take data in folder RAW/yr/
and convert it to special format useful for FAST
Apply preprocessing to the data. It includes:
demean
detrend
resample -or- decimate by div_factor
/!\ files have to be named as follow:
{julday}/{network}.{stations}*{channel}*
In a second step, json files with fp parameters 
will be created. 
"""


def detect_time_gaps(st, min_samples=10, epsilon=1e-20, thresh_disc=100):
    """Script to detect time gaps filled with 0's"""
    # Read data
    tdata = st[0].data
    indz = np.where(abs(tdata) < epsilon)[0] # indices where we have 0
    diff_indz = indz[min_samples:] - indz[0:-min_samples] # Need min_samples consecutive samples with 0's to identify as time gap
    ind_des = np.where(diff_indz == min_samples)[0] # desired indices: value is equal to min_samples in the time gap
    ind_gap = indz[ind_des] # indices of the time gaps
    gap_start_ind = []
    gap_end_ind = []
    if (0 == len(ind_gap)): 
        num_gaps = 0
    else:
        print "Warning: %s time gap(s) with zeros found"%len(ind_gap)
        # May have more than 1 time gap
        ind_diff = np.diff(ind_gap) # discontinuities in indices of the time gaps, if there is more than 1 time gap
        ind_disc = np.where(ind_diff > thresh_disc)[0]
        # N-1 time gaps
        curr_ind_start = ind_gap[0]
        for igap in range(len(ind_disc)): # do not enter this loop if ind_disc is empty
            gap_start_ind.append(curr_ind_start)
            last_index = ind_gap[ind_disc[igap]] + min_samples
            gap_end_ind.append(last_index)
            curr_ind_start = ind_gap[ind_disc[igap]+1] # update for next iteration
        # Last time gap
        gap_start_ind.append(curr_ind_start)
        gap_end_ind.append(ind_gap[-1] + min_samples)
        num_gaps = len(gap_start_ind)

    return [num_gaps, gap_start_ind, gap_end_ind]


def fill_zero_gaps(st, num_gaps, gap_start_ind, gap_end_ind):
    print 'Number of zeros filled time gaps: ', num_gaps
    print 'Starting index of each time gap: ', gap_start_ind
    print 'Ending index of each time gap: ', gap_end_ind
    ntest = 2000 # Number of test samples in data - assume they are noise
    for igap in range(num_gaps):
        ngap = gap_end_ind[igap] - gap_start_ind[igap] + 1
        print 'Number of samples in gap: ', ngap

      # Bounds check
        if (gap_start_ind[igap]-ntest < 0): # not enough data on left side
            median_gap_right = np.median(st[0].data[gap_end_ind[igap]+1:gap_end_ind[igap]+ntest]) # median of ntest noise values on right side of gap
            median_gap = median_gap_right
            mad_gap_right = robust.mad(st[0].data[gap_end_ind[igap]+1:gap_end_ind[igap]+ntest]) # MAD of ntest noise values on right side of gap
            mad_gap = mad_gap_right
        elif (gap_end_ind[igap]+ntest >= len(st[0].data)): # not enough data on left side
            median_gap_left = np.median(st[0].data[gap_start_ind[igap]-ntest:gap_start_ind[igap]-1]) # median of ntest noise values on left side of gap
            median_gap = median_gap_left
            mad_gap_left = robust.mad(st[0].data[gap_start_ind[igap]-ntest:gap_start_ind[igap]-1]) # MAD of ntest noise values on left side of gap
            mad_gap = mad_gap_left
        else:
            median_gap_left = np.median(st[0].data[gap_start_ind[igap]-ntest:gap_start_ind[igap]-1]) # median of ntest noise values on left side of gap
            median_gap_right = np.median(st[0].data[gap_end_ind[igap]+1:gap_end_ind[igap]+ntest]) # median of ntest noise values on right side of gap
            median_gap = 0.5*(median_gap_left + median_gap_right)
            mad_gap_left = robust.mad(st[0].data[gap_start_ind[igap]-ntest:gap_start_ind[igap]-1]) # MAD of ntest noise values on left side of gap
            mad_gap_right = robust.mad(st[0].data[gap_end_ind[igap]+1:gap_end_ind[igap]+ntest]) # MAD of ntest noise values on right side of gap
            mad_gap = 0.5*(mad_gap_left + mad_gap_right)
        # Fill in gap with uncorrelated white Gaussian noise
        gap_x = mad_gap*np.random.randn(ngap) + median_gap
        st[0].data[gap_start_ind[igap]:gap_end_ind[igap]+1] = gap_x


def preprocessing(p):
    nanfile=0
    """preprocessing"""
    #os.system('rm -rf data/waveforms*')
    for day in p['days']:
        for sta in p['stalist']:
            try:os.makedirs('data/waveforms%s/'%sta)
            except:pass
            for cha in p['chalist']:
                g = glob.glob(p['raw_path']+'%03d/*TA.%s.%s.mseed'%(day, sta,day))
                for f in g:
                    st = read(f)
                    if len(st) > 1:
                        print "Warning: More than one file in Stream"
                        print "... Merging"
                        st.merge(method=0, fill_value=0)
                    if np.isnan(st[0].data).any():
                        print "Warning: Data contains NaN values, skip this file - %s"%st
                        nanfile +=1
                        bad_file.append(os.path.basename(f))
                        continue
                    # ------- CHECK IF 0-LIKE GAPS AND FILL WITH UNCORRELATED NOISE -------
                    [num_gaps, gap_start_ind, gap_end_ind] = detect_time_gaps(st)
                    if num_gaps != 0: 
                        fill_zero_gaps(st, num_gaps, gap_start_ind, gap_end_ind)
                        
                    st.detrend(type='demean')
                    st.detrend(type='linear')
                    st.filter('bandpass', freqmin=p['min_freq'], freqmax=p['max_freq'], zerophase=True)
                    if st[0].stats.sampling_rate > p['sampling_rate']:
                        if p['resample']:
                            st.resample(p['sampling_rate'], no_filter=True, strict_length=False)
                        else:
                            st.decimate(p['div_factor'], no_filter=True, strict_length=False)
                    print st 
                    print
                    st.write('data/waveforms%s/%s'%(sta,os.path.basename(f)),format='MSEED')
    print nanfile, 'files were rejected because of NaN'

if __name__=='__main__':
    p = basic_params()
    print '>>> Running Preprocessing'
    print '>>> Downsampling to %s'%p['sampling_rate']
    if p['resample'] == True:
        m = 'resampling'
    else: m = 'decimating'
    print '>>> Downsample method: %s'%m
    print '>>> looking for stations: %s'%p['stalist']
    print '>>> looking for channels: %s'%p['chalist']
    print '>>> looking for days: %s'%p['days']
    print
    preprocessing(p)
