set LOG_TYPE="64-256-64-inc"
@REM set LOG_TYPE="640-1152-128-inc"
@REM set LOG_TYPE="dynamic-low-nys"
@REM set LOG_TYPE="128-2048-64-dec"
@REM set LOG_TYPE="dynamic-high"
@REM set LOG_TYPE="dynamic-low"
@REM set LOG_TYPE="dynamic-very-low"
set VIDEO_FOLDER="slot"

@REM python .\scripts\streamingstats.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_video_qoe_csv
@REM python .\scripts\streamingstats.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_cmt_csv
@REM python .\scripts\videoplayback.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_csv
@REM python .\scripts\bh_vs_realtime_graph.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_csv

@REM python .\scripts\streamingstats_slot.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_cmt_csv
python .\scripts\streamingstats_slot.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_video_qoe_csv
@REM python .\scripts\videoplayback_slot.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_csv
@REM python .\scripts\tcp_fallback_slot.py mm dynamic %LOG_TYPE% %VIDEO_FOLDER% create_csv