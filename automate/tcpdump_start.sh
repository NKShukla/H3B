#!/bin/sh
set -x

rm -f nohup.out

pcapfile=$1; shift
nohup /usr/sbin/tcpdump -ni enp0s3 -s 65535 -w "$pcapfile".pcap &

# Write tcpdump's PID to a file
echo $! > /var/run/tcpdump.pid
