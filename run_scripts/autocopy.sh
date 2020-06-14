#!/bin/bash

# to copy and remove local raw data

if [ $# -ne 1 ]; then
	echo 'Usage ./autocopy "dir_name"'
	ls /home/pi/ad2/data
	exit 1
fi

if [ -e /home/pi/ad2/run_scripts/lock ]; then
	echo 'Other Process running'
	exit 2

fi
mkdir /home/pi/ad2/run_scripts/lock

data_dir=$1
echo $data_dir

rsync -avr --checksum --progress -e 'ssh' /home/pi/ad2/data/${data_dir} data_server:ad2/data

rm -rf /home/pi/ad2/run_scripts/lock
