#!/usr/bin/python3
# ---------------------------------------#
#    daq.py
#    DAQ sample code to handle 
#    Analog discovery 2 for He-3
#
#    Provider:  Digilent, Inc.
#    Author  :  Keita Mizukoshi
#    Date    :  2020 Jun. 12
#
#    Usage:
#    python3 daq.py -h
# ---------------------------------------#

import os, sys
from ctypes import *
from dwfconstants import *
import math
import time
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description='AD2 DAQ in CUI', add_help=True)
parser.add_argument('-v', '--verbose', help='verbose level', default=0, type=int)
parser.add_argument('-d', '--dirname', help='Directory name', default='/home/pi/ad2/data/test1/', type=str)
parser.add_argument('-f', '--filename', help='File name', default='sub0000', type=str)
parser.add_argument('-t', '--trigger_level', help='Trigger Level (V)', default='0.1', type=str)
parser.add_argument('-n', '--negative_edge', help='Negative edge for trigger', action='store_true')
parser.add_argument('-p', '--time_position', help='Center of time position (sec.)', default='0.0', type=str)
parser.add_argument('-s', '--sampling', help='Sampling frequency (Hz)', default='10000000', type=str)
parser.add_argument('-e', '--entries', help='Number of events', default='10', type=int)

args = parser.parse_args()

verbose_level = args.verbose
dir_name = args.dirname
file_name = args.filename
trigger_level = c_double(float(args.trigger_level))
time_position = c_double(float(args.time_position))
sampling = c_double(float(args.sampling))
entries = args.entries
trigger_edge = args.negative_edge

if verbose_level > 1:
    print('Dir name    : ', dir_name)
    print('File name   : ', file_name)
    print('N events    : ', entries)
    print('Trigger (V) : ', trigger_level)
    print('Trig. Edge  : ', 'Negative' if trigger_edge else 'Positive')
    print('Sampling Hz : ', sampling)
    print('time pos.(s): ', time_position)

f = open(dir_name+file_name+'.txt', 'w')
f.write('Dir name    : '+ dir_name)
f.write('File name   : '+ file_name)
f.write('N events    : '+ str(entries))
f.write('Trigger (V) : '+ str(trigger_level))
f.write('Trig. Edge  : '+ 'Negative' if trigger_edge else 'Positive')
f.write('Sampling Hz : '+ str(sampling))
f.write('time pos.(s): '+ str(time_position))
f.close()


if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()
rgdSamples = (c_double*8192)()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# 2nd configuration for Analog Disocovery with 16k analog-in buffer
#dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(1), byref(hdwf)) 

if hdwf.value == hdwfNone.value:
    szError = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szError);
    print("failed to open device\n"+str(szError.value))
    quit()

#set up acquisition
dwf.FDwfAnalogInFrequencySet(hdwf, sampling) # Hz
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(8192)) 
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))

#set up trigger
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(0)) #disable auto trigger
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcDetectorAnalogIn) #one of the analog in channels
dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)
dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0)) # first channel
dwf.FDwfAnalogInTriggerLevelSet(hdwf, trigger_level) # 0.1V
if trigger_edge:
    dwf.FDwfAnalogInTriggerConditionSet(hdwf, trigcondFallingNegative) 
else :
    dwf.FDwfAnalogInTriggerConditionSet(hdwf, trigcondRisingPositive) 
dwf.FDwfAnalogInTriggerPositionSet(hdwf, time_position)

event_in_file = 10

# wait at least 2 seconds with Analog Discovery for the offset to stabilize, before the first reading after device open or offset/range change
time.sleep(2)

print('Start DAQ')
dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))
#trigger_timestamp = 0.
for iTrigger in range(entries):
    if iTrigger % event_in_file == 0:
        if iTrigger != 0:
            f.close()
        f = open(dir_name+file_name+'.'+str(int(iTrigger/event_in_file)).zfill(4)+'.dat', 'w')

    # new acquisition is started automatically after done state 

    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value :
            trigger_timestamp = datetime.now().timestamp()
            break
        time.sleep(0.001)
    
    dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, 8192) # get channel 1 data
    #dwf.FDwfAnalogInStatusData(hdwf, 1, rgdSamples, 8192) # get channel 2 data

    f.write('#. '+str(iTrigger)+'  '+str(trigger_timestamp)+'\n')
    for i in range(8192):
        f.write(str(rgdSamples[i]))
        f.write('\n')
    event_end_timestamp = datetime.now().timestamp()
    f.write(str(event_end_timestamp))
    f.write('\n')
    
f.close()
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(False))
dwf.FDwfDeviceCloseAll()

print('Stop DAQ')

