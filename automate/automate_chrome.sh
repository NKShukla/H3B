#!/usr/bin/env bash

set -x

if [ $# -lt 3 ]
then
    echo use $0 "<tracefile> <video_id_file> <slot>"
    exit 1
fi

tracefile=$1; shift
video_id_file=$1; shift
slot=$1;shift

cat $video_id_file

quicExeFile=$(mktemp)
tcpExeFile=$(mktemp)

function runScript() 
{
    exeFile=$1; shift
    vid=$1; shift
    disQuic=$1; shift
    protocol=$1; shift

    cat > $exeFile << EOF
    #!/usr/bin/env bash

    set -x

    google-chrome-stable --user-data-dir=$udir "https://www.youtube.com/embed/$vid?rel=0&autoplay=1" --load-extension=../DASH/adblock,../DASH/NetworkLogExtension $disQuic --no-proxy-server --autoplay-policy=no-user-gesture-required --no-first-run --enable-logging --log-level=0 --start-maximized --no-default-browser-check

    cpid=\$!
    kill -INT cpid
EOF
}

chmod +x $tcpExeFile $quicExeFile

log_type="$(cut -d'.' -f1 <<<"$(cut -d'/' -f2 <<<"$tracefile")")"

for vid in `cat $video_id_file`
do
    # quic-enabled stream
    echo $vid
    
    udir=$(mktemp -d)
    runScript $quicExeFile $vid " " "quic"
    chmod +x $quicExeFile

    sudo bash tcpdump_start.sh pcaps/${vid}_"${log_type}"_quic_slot-${slot}
    
    mm-link $tracefile $tracefile $quicExeFile
    # $quicExeFile

    sudo bash tcpdump_stop.sh

    cp ${udir}/chrome_debug.log logs-collected/chrome_debug_${vid}_"${log_type}"_quic_slot-${slot}.log
    
    rm -rf $udir
    rm $quicExeFile
    echo $vid + "quic complete"
    sleep 30

    # quic-disabled stream
    udir=$(mktemp -d)
    runScript $tcpExeFile $vid "--disable-quic" "tcp"
    chmod +x $tcpExeFile

    sudo bash tcpdump_start.sh pcaps/${vid}_"${log_type}"_tcp_slot-${slot}       
    mm-link $tracefile $tracefile $tcpExeFile
    # $tcpExeFile

    sudo bash tcpdump_stop.sh

    cp ${udir}/chrome_debug.log logs-collected/chrome_debug_${vid}_"${log_type}"_tcp_slot-${slot}.log
    
    rm -rf $udir
    rm $tcpExeFile
    echo $vid + "tcp complete"
    sleep 30
done
