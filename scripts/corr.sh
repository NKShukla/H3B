#!/bin/sh

set -e

mkdir -p data/phase1
mkdir -p data/phase2
mkdir -p data/mahimahi

cd data/input || exit
for FILE in *.pcap
do
    # tshark -r "$FILE" -Y "tcp" -T fields -e frame.time_relative -e tcp.len  >> "../phase1/$FILE.csv"
    sed -i -e 1i'real_time,tcp_bytes' "../phase1/$FILE".csv
    # tshark -r $FILE -Y "quic or tcp" -T fields -e ip.proto -e tcp.len -e udp.length -e frame.time_relative >> ../phase1/$FILE.csv
    # sed -i -e 1i'\protocol,tcp_bytes,quic_bytes,real_time' "../phase1/$FILE".csv
    
done

echo "Phase 1 done"
cd ../..
python3 automate1.py

echo "Phase 2 done"
python3 mahimahiTraceGen.py

echo "All done"
