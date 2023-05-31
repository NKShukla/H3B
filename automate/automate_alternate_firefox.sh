#!/usr/bin/env bash

set -x

if [ $# -lt 4 ]
then
    echo use $0 "<tracefile> <video_id_file> <day_timing> <loop_required>"
    exit 1
fi

tracefile=$1; shift
video_id_file=$1; shift
day_timing=$1;shift
loop_required=$1;shifts

cat $video_id_file

quicExeFile=$(mktemp)
tcpExeFile=$(mktemp)

function runScript() 
{
    exeFile=$1; shift
    vid=$1; shift
    disQuic=$1; shift
    timing=$1; shift
    protocol=$1; shift
    pref=$1; shift
    
    cat > $exeFile << EOF
    #!/usr/bin/env bash

    set -x
  
    web-ext run --source-dir=/home/vagrant/Sapna/BTP/DASH/NetworkLogExtensionFirefox \
    --pref devtools.console.stdout.chrome=true --pref devtools.console.stdout.content=true \
    --pref media.autoplay.default=0 --pref network.http.http3.enable=$pref \
    --pref network.http.http3.enable_0rtt=$pref --pref network.http.http3.priority=$pref \
    --pref network.http.http3.support_version1=$pref --pref network.http.http3.enabled=$pref \
    --pref network.http.http3.backup_timer_delay=100 \
    --verbose --args="-private-window-url=https://www.youtube.com/embed/$vid?rel=0&autoplay=1" | tee firefox_debug.log
    
    cpid=\$!
    kill -INT cpid
EOF
}

chmod +x $tcpExeFile $quicExeFile


log_type="$(cut -d'.' -f1 <<<"$(cut -d'/' -f2 <<<"$tracefile")")"

for vid in `cat $video_id_file`
do
    currenttime=$(date +%H:%M)
    flag=0
    timing=${day_timing}

    if [[ "$day_timing" == "morning" ]]; then
        while :
        do
            if [[ "$currenttime" > "08:00" ]] && [[ "$currenttime" < "16:00" ]]; then
                flag=1
                break
            fi
            
            if [[ "$loop_required" == "false" ]]; then
                break
            fi

            currenttime=$(date +%H:%M)
        done

        echo $currenttime
    fi

    if [[ "$day_timing" == "afternoon" ]]; then
        while :
        do
            if [[ "$currenttime" > "16:00" ]] && [[ "$currenttime" < "23:59" ]]; then
                flag=1
                break
            fi

            if [[ "$loop_required" == "false" ]]; then
                break
            fi

            currenttime=$(date +%H:%M)
        done
        echo $currenttime
    fi

    if [[ "$day_timing" == "evening" ]]; then
        while :
        do
            if [[ "$currenttime" > "00:00" ]] && [[ "$currenttime" < "08:00" ]]; then
                flag=1
                break
            fi

            if [[ "$loop_required" == "false" ]]; then
                break
            fi

            currenttime=$(date +%H:%M)
        done
        echo $currenttime
    fi

    if [[ "$day_timing" == "lowbw" ]] || [[ "$day_timing" == "highbw" ]]; then
        flag=1
    fi

    if [[ "$day_timing" == "slot" ]]; then
        flag=1
        timing=${day_timing}-${loop_required}
    fi

    if [[ "$flag" == "1" ]]; then
        echo $vid
        
        udir=$(mktemp -d)
        runScript $quicExeFile $vid " " $timing "quic" "true"
        chmod +x $quicExeFile

        sudo bash tcpdump_start.sh pcaps/${vid}_"${log_type}"_quic_${timing}
        
        mm-link $tracefile $tracefile $quicExeFile
        # $quicExeFile

        sudo bash tcpdump_stop.sh

        mv firefox_debug.log logs/firefox_debug_${vid}_"${log_type}"_quic_${timing}.log
        cp logs/firefox_debug_${vid}_"${log_type}"_quic_${timing}.log logs-collected/firefox_debug_${vid}_"${log_type}"_quic_${timing}.log

        rm -rf $udir
        rm $quicExeFile
        echo $vid + "quic complete"
        sleep 30
    fi

    if [[ "$flag" == "1" ]]; then
        udir=$(mktemp -d)
        runScript $tcpExeFile $vid "--disable-quic" $timing "tcp" "false"
        chmod +x $tcpExeFile

        sudo bash tcpdump_start.sh pcaps/${vid}_"${log_type}"_tcp_${timing}       
        mm-link $tracefile $tracefile $tcpExeFile
        # $tcpExeFile

        sudo bash tcpdump_stop.sh


        mv firefox_debug.log logs/firefox_debug_${vid}_"${log_type}"_tcp_${timing}.log
        cp logs/firefox_debug_${vid}_"${log_type}"_tcp_${timing}.log logs-collected/firefox_debug_${vid}_"${log_type}"_tcp_${timing}.log
        
        rm -rf $udir
        rm $tcpExeFile
        echo $vid + "tcp complete"

        # sed '1d' $video_id_file > temp
        # rm $video_id_file
        # cp temp $video_id_file
        # rm temp

        sleep 30
    fi
done

#--log-net-log=/home/nsl5/Sapna/BTP/automate/net-export/$vid-$protocol-$timing.json
