#!/usr/bin/python3

import os, sys
import subprocess
import numpy
import glob
import time


def run():

    ## Edit HERE ##
    data_dir = '/home/pi/ad2/data/' # with the last slash
    sub_dir = '20200705'
    entries = 10000

    frequency = 10000000.0 # Hz For PMT test
    #frequency = 20000.0 # Hz For He-3
    trigger_level = -1.0 # V
    trigger_type = 'rise' # rise or fall
    trigger_position = 3.e-4 # s


    daq_cmd = '/home/pi/ad2/bin/daq'
    subrun_name = find_newrun(data_dir+sub_dir+'/')


    print_cmd(['Manual copy:','/home/pi/ad2/bin/autocopy.sh',
        data_dir+sub_dir])

    cmd = [daq_cmd
    ,str(frequency)
    ,str(trigger_level)
    ,trigger_type
    ,str(trigger_position)
    ,str(entries)
    ,data_dir+sub_dir + '/' + subrun_name 
    ]

    subprocess.run(['mkdir', '-p', data_dir+sub_dir ])

    print_cmd(cmd)
    subprocess.run(cmd)

    # Copy cmd
    print_cmd(['/Users/mzks/drs4/run_scripts/autocopy.sh',sub_dir])
    #subprocess.Popen(['/Users/mzks/drs4/run_scripts/autocopy.sh',sub_dir])


def print_cmd(cmd):
    for c in cmd:
        print(c, end=' ')
    print()


def find_newrun(dir_name):

    data_header = 'sub'

    files = glob.glob(dir_name+'*.txt')
    if len(files) == 0:
        return data_header+'0'.zfill(4)
    else:
        files.sort(reverse=True)
        num_pos = files[0].find('sub')
        return data_header+str(int(files[0][num_pos+3:num_pos+3+4])+1).zfill(4)


def auto_run():

    while(True):
        run()
        time.sleep(1)


if __name__ == '__main__':

    auto_run()
