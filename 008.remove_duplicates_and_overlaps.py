import subprocess, os
import numpy as np
from parse_config import parse_json
from params import get_first_time
""" 
this script arrange the results over readable table
remove duplicated events and overlaping events
"""



"""configure these params"""
input_dir = 'data/network_detection/'
nsta = 18
nstathresh = 2
wtime_before = 10 #time in s for UTCDateTime list 
wtime_after = 15 
flag_each_station = True
#less important
network_bn = '%ssta_%sstathresh'%(nsta, nstathresh)
netfile = '%s_detlist_rank_by_peaksum.txt'%(network_bn)
netdetfile = 'NetDetTimes_%s.txt'%(network_bn)
uniqueEvent_fn = 'Uniquestart_%s.txt'%(network_bn)
finalfilename = 'FinalNetDetTimes_%s.txt'%(network_bn)
sortedfile = 'sorted_%s'%(finalfilename)
UTCDTfn = 'UTCDateTime_list_%s.txt'%(network_bn)
network_config = parse_json('postprocessing/network_params.json')
dt_fp = network_config['network']['dt_fp']
init_time = get_first_time()# global start time for all channels
firstline =  '#start_fp_id\t  end_fp_ind\t    dL\t    nevent\t        nsta\t   tot_ndets\t max_ndets\t  tot_vol\t  max_vol\t   max_peaksum\t   nsta_detect\t  diff_ind\n'
firstline_utc =  '#fp_time\t       starttime\t       endtime\t     julday\t      dL\t    nevent\t        nsta\t   tot_ndets\t max_ndets\t  tot_vol\t  max_vol\t   max_peaksum\t   nsta_detect\t  diff_ind\n'


"""
Create stations_order.txt
"""
os.chdir(input_dir)
fl = open('%s'%netfile).readlines()[0]
sorder = filter(None,fl.split(' '))[1:nsta+1]
open('station_order.txt','w+').close()
f = open('station_order.txt', 'a')
for s in sorder:
    f.write("%s\t" % str(s))

"""
Arrange network detection results
Save only start and end fingerprint indices for each event
first num_sta columns -> 2 columns
output 2 more columns at end
    num_sta: number of stations that detected event
    diff_ind: difference between first and last fingerprint index
"""
# Read in network detections
data = np.genfromtxt(netfile, dtype=str, skip_header=1)
print ("Number of detection: %s"%len(data))
# Get min and max index (time) for each event over all stations without NaNs
ind_time_min = []
ind_time_max = []
ind_time_diff = []
count_not_nan = []
for iev in range(len(data)):
    cur_event = data[iev]
    ind_event_time = []
    for ista in range(nsta):
        if ('nan' != str.lower(cur_event[ista])):
            ind_event_time.append(int(cur_event[ista]))
    print 'event:', iev, ', times: ', ind_event_time
    ind_time_min.append(str(min(ind_event_time)))
    ind_time_max.append(str(max(ind_event_time)))
    ind_time_diff.append(str(max(ind_event_time)-min(ind_event_time)))
    count_not_nan.append(str(len(ind_event_time)))
# Output network detections with min index and max index to file
open(netdetfile, 'w+').close()
fout = open(netdetfile, 'a+')
fout.write(firstline)
for iev in range(len(data)):
    fout.write('%12s %12s %12s %12s %12s %12s %12s %12s %12s %12s %12s %12s' \
    % (ind_time_min[iev], ind_time_max[iev], data[iev][nsta], data[iev][nsta+1], data[iev][nsta+2], \
    data[iev][nsta+3], data[iev][nsta+4], data[iev][nsta+5], data[iev][nsta+6], data[iev][nsta+7], \
    count_not_nan[iev], ind_time_diff[iev]))
    if (flag_each_station):
        for ista in range(nsta):
             fout.write('%12s' % data[iev][ista])
    fout.write('\n')
fout.close()
print "... Number of network detections: ", len(data)
print ">>> Network detection results arranged"
print


"""
Remove duplicated events
Remove events with duplicate start fp index
and keep event with highest end num_sta then peaksum
"""
#
cmd1 = "awk '!seen[$1, $2]++' %s > tmp_no_duplicates.txt" %(netdetfile)
# Sort by start times (first column), then number of stations, then descending order of peaksum similarity - should not have duplicate start-end pairs
cmd2 = "sort -k1,1n -nrk11,11 -nrk10,10 tmp_no_duplicates.txt > tmp_sorted_no_duplicates.txt"
# Sort by start times, removing duplicate start times
cmd3 = "sort -u -nk1,1 tmp_sorted_no_duplicates.txt > %s"%(uniqueEvent_fn)
cmd4 = "rm tmp_*.txt"
print ">>> Remove duplicated events"
print '... '+cmd1
print '... '+cmd2
print '... '+cmd3
print '... '+cmd4
subprocess.call([cmd1], shell=True)
subprocess.call([cmd2], shell=True)
subprocess.call([cmd3], shell=True)
subprocess.call([cmd4], shell=True)
print ">>> Duplicated events removed"
print 

"""
Remove overlaping events
Remove events with overlaping times
i.e. when starttime of one event is 
before endtime of another event
"""
print ">>> Remove overlaping events"
# Read all event lines into dictionary with start index as key
# Later, we will delete overlapping events from this dictionary
event_dict = {}
with open(uniqueEvent_fn, 'r') as fin:
    for il, line in enumerate(fin):
        if il==0:continue
        evline = line.split()
        key = int(evline[0]) # key is start index
        val = []
        iq = 0
        for vv in evline[1:]:
            if (iq >= 11):
                val.append(vv) # val: end_index, dL, nevents, nsta, tot_ndets, max_ndets, tot_vol, max_vol, peaksum
            else: 
                val.append(int(vv))
            iq += 1
        event_dict[key] = val
print "Initial number of event lines:", len(event_dict)
# Traverse events in dictionary in order of start time
keylist = sorted(event_dict.keys())
ik = 0
while (ik < len(keylist)):
    vv = event_dict[keylist[ik]]
    tmp_dict = {}
    tmp_dict[keylist[ik]] = vv
    # If start time of next event is before or at end time of current event, or for all events in the tmp_dict: add to temp dictionary since it overlaps
    ii = 1
    end_time = vv[0]
    if (ik+ii) < len(keylist):
        while(keylist[ik+ii] <= end_time):
           tmp_dict[keylist[ik+ii]] = event_dict[keylist[ik+ii]]
           end_time = max(end_time, event_dict[keylist[ik+ii]][0])
           print ik, ii, ik+ii, keylist[ik+ii], end_time
           ii += 1
           if ((ik+ii) >= len(keylist)):
               break

    # Events with overlap have more than 1 event in temp dictionary
    # Keep the event with highest peaksum; remove all other overlap events in temp dictionary from the event_dict
    if (len(tmp_dict) > 1):
        tmp_eventlist = sorted(tmp_dict.iteritems(), key=lambda(k,v): v[8], reverse=True) # sort by descending order of peaksum
        keep_event = tmp_eventlist[0]
        orig_end_time = keep_event[1][0]
        event_dict[keep_event[0]][0] = end_time # Replace with latest end time over all overlapping events
        print "Event with maximum peaksum: start time:", keep_event[0], ", end time:", event_dict[keep_event[0]][0],\
        ", peaksum:", event_dict[keep_event[0]][8], ", original end time:", orig_end_time
        for iev in tmp_eventlist[1:]:
            print "    Removing overlap event, start time:", iev[0], ", end time:", iev[1][0], ", peaksum:", iev[1][8]
            event_dict.pop(iev[0])
        print "Current number of event lines:", len(event_dict)
    ik += ii
print "Final number of event lines:", len(event_dict)
# Output event list (without overlap events) to file
out_key_list = sorted(event_dict.keys())
open(finalfilename,'w+').close()
with open(finalfilename, 'w') as fout:
    fout.write(firstline)
    for kkey in out_key_list:
        value = event_dict[kkey]
        fout.write(('%12d %12d %12d %12d %12d %12d %12d %12d %12d %12d %12d %12d') \
        %(kkey, value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7], value[8], value[9], value[10]))
        if (flag_each_station):
            for ista in range(nsta):
               fout.write('%12s' % value[11+ista])
        fout.write('\n')

fout.close()
print '>>> Overlaping event removed'
print


"""
Sort events in descending order of num_sta 
(number of stations that detected event), then peaksum 
(maximum similarity for this event)
"""

print '>> Sorting file: %s'%(finalfilename)
# Sort in descending order of number of stations (column 11), then descending order of peaksum (column 10)
cmd = "sort -nrk11,11 -nrk10,10 %s  > %s"%(finalfilename, sortedfile)
subprocess.call([cmd], shell=True)
with open('%s'%sortedfile, 'r+') as f:
    file_data = f.read(); f.seek(0,0); f.write(firstline + file_data)
f.close()
print 
print '>>> All result are cleaned and sorted in file %s'%(sortedfile)

'''have to werk on this'''
#"""
#Convert fp indice to UTCDateTime and put it on file
#"""
#[det_start_ind, det_end_ind, dL, nevents, nsta, \
#tot_ndets, max_ndets, tot_vol, max_vol, peaksum, \
#num_sta, diff_ind] = np.loadtxt(sortedfile, \
#usecols=(0,1,2,3,4,5,6,7,8,9,10,11), unpack=True)
#det_times = dt_fp * det_start_ind
#det_end_times = dt_fp * det_end_ind
#diff_times = dt_fp * diff_ind
##values = np.loadtxt(sortedfile, unpack=True)[12:]
#
#open(UTCDTfn,'w+').close()
#with open(UTCDTfn, 'w') as fout:
#    fout.write(firstline_utc)
#    for kk in range(len(det_times)):
#        ev_time = init_time + det_times[kk]
#        start_time = ev_time - wtime_before
#        end_time = ev_time + wtime_after
#        if (diff_times[kk] > wtime_after): # special case: unusually long delay between start and end times
#            end_time = ev_time + diff_times[kk] + wtime_after
#        print kk, ev_time, start_time, end_time.timestamp
#        fout.write(('%15s %15s %15s %5s %12d %12d %12d %12d %12d %12d %12d %12d %12d %12d\n') \
#            %(ev_time.timestamp, start_time.timestamp, end_time.timestamp, '%03d'%ev_time.julday, dL[kk], nevents[kk], nsta[kk], \
#            tot_ndets[kk], max_ndets[kk], tot_vol[kk], max_vol[kk], peaksum[kk], \
#            num_sta[kk], diff_ind[kk]))
#        #if (flag_each_station):
#        #    for ista in range(nsta):
#        #        fout.write('%12s' % value[ista])
#        #fout.write('\n')
#fout.close()
#
#os.system('rm %s'%uniqueEvent_fn)
#os.system('rm %s'%netdetfile)
#print
#print ">>> the following files have been created:"
#print '... ', finalfilename, '(the list of all fp with no overlap and repeated events)' 
#print '... ', sortedfile, '(same but sorted with respec to numper of station detection)'
#print '... ', UTCDTfn, '(contains UTCDateTimes of each events)'
#
