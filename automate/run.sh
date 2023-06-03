#!/usr/bin/env bash
set -x
set -e
sudo sysctl -w net.ipv4.ip_forward=1

for i in {1..100}
do
	bash automate_chrome.sh dynamic-high.com- "video-groups/video-ids" $i
	bash automate_chromium.sh dynamic-low.com- "video-groups/video-ids" $i
	bash automate_firefox.sh 64-256-64-inc.com- "video-groups/video-ids" $i
	bash automate_chrome.sh pakistan.com- "video-groups/video-ids" $i	
done

