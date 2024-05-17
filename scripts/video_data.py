import os, csv, sys, json
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter
import numpy as np
import collections

font = { 'size'   : 22 }

ALL_QOE_COMBINATION = False
matplotlib.rc('font', **font)


LOGS_FOLDER = "data/logFiles/"
JSON_FOLDER = "data/jsonFiles/"
GRAPHS_FOLDER = "data/graphs/"
CSV_FOLDER = "data/csvFiles/"

VIDEO_INFO_JSON_FILE = "video_info.json"

EXTRA_QOE_FOLDERS_REQUIRED = ["_qoe", "_qoe-ab-abv", "_qoe-ab-as", "_qoe-abv-as", "_qoe-abv", "_qoe-ab", "_qoe-as"]


def reset_main_folders():
	global LOGS_FOLDER, JSON_FOLDER, GRAPHS_FOLDER, CSV_FOLDER, VIDEO_INFO_JSON_FILE

	LOGS_FOLDER = "data/logFiles/"
	JSON_FOLDER = "data/jsonFiles/"
	# GRAPHS_FOLDER = "data/graphs/"
	CSV_FOLDER = "data/csvFiles/"

	VIDEO_INFO_JSON_FILE = "video_info.json"


def updateFolderLocations(video_list_folder, log_type):
	global LOGS_FOLDER, JSON_FOLDER, GRAPHS_FOLDER, CSV_FOLDER, VIDEO_INFO_JSON_FILE

	LOGS_FOLDER += (video_list_folder + "/")
	JSON_FOLDER += (video_list_folder + "/")
	CSV_FOLDER += (video_list_folder + "/")

	VIDEO_INFO_JSON_FILE = LOGS_FOLDER + VIDEO_INFO_JSON_FILE
	
	if (not os.path.isdir(JSON_FOLDER)):
		os.mkdir(JSON_FOLDER)
	
	if (not os.path.isdir(JSON_FOLDER + "/" + log_type)):
		os.mkdir(JSON_FOLDER + "/" + log_type)
		os.mkdir(JSON_FOLDER + "/" + log_type + "/quic")
		os.mkdir(JSON_FOLDER + "/" + log_type + "/tcp")

	if (not os.path.isdir(CSV_FOLDER)):
		os.mkdir(CSV_FOLDER)

	base_folder = CSV_FOLDER + "/" + log_type
	if (not os.path.isdir(base_folder)):
		os.mkdir(base_folder)

	folders_required = ["", "_wt", "_qoe"]
	
	if (ALL_QOE_COMBINATION):
		folders_required += EXTRA_QOE_FOLDERS_REQUIRED

	for folder in folders_required:
		if (not os.path.isdir(base_folder + "/quic" + folder)):
			os.mkdir(base_folder + "/quic" + folder)

		if (not os.path.isdir(base_folder + "/tcp" + folder)):
			os.mkdir(base_folder + "/tcp" + folder)

	
	if (not os.path.isdir(CSV_FOLDER + "/" + log_type + "/frame_length_quic")):
		os.mkdir(CSV_FOLDER + "/" + log_type + "/frame_length_quic")
		os.mkdir(CSV_FOLDER + "/" + log_type + "/frame_length_tcp")
		os.mkdir(CSV_FOLDER + "/" + log_type + "/buffer_health_quic")
		os.mkdir(CSV_FOLDER + "/" + log_type + "/buffer_health_tcp")


def getQuicFilesList(video_list_folder, log_type):
	video_files = {}

	folder = JSON_FOLDER + video_list_folder + "/" + log_type + "/" + "quic" +"/"
	print(folder)
	directory = os.fsencode(folder)
	for file in os.listdir(directory):
		file = file.decode("utf-8")
		vid = file.split("_")[2]
		if (vid not in video_files):
			video_files[vid] = []
		
		video_files[vid].append(folder + file)


	return video_files
	

def parseSysArgs(argv):
	to_save = "nop"

	log_type = argv[3]
	bw_list = []
	if (log_type in trace_files.keys()):
		bw_list = getBWInfo(log_type=log_type)
	else:
		[min_bw, max_bw, jump_bw, initial_bw_change] = log_type.split('-')
		min_bw = int(min_bw)
		max_bw = int(max_bw)
		jump_bw = int(jump_bw)
		
		bw_list = getBWInfo(min_bw, max_bw, jump_bw, initial_bw_change)
	
	video_list_id = argv[4]
	# vidoe_list_id = int(video_list_id.split("-")[-1]) - 1
	updateFolderLocations(video_list_id, log_type)

	if (len(argv) > 5):
		to_save = argv[5]
	

	return log_type, bw_list, to_save, video_list_id


def getVideoQualTicks(video_info_values):
	vid_qual=set()
	for k in video_info_values:
		vid_qual.add(k["qualityLabel"])

	all_qual=list(vid_qual)
	all_qual.sort(key=lambda x:(int(x.split('p')[0]),int(x.split('p')[1]) if len(x.split('p')[1])>0 else 0))
	y_ticks=[j for j in range(1,len(all_qual)+1)]
	mapping={}
	for i in range(len(all_qual)):
		mapping[all_qual[i]]=i+1

	return all_qual, y_ticks, mapping


def getFilesInfo(log_type, type_of_files, vid):

	quicmm_file = JSON_FOLDER + log_type + "/quic/chrome_debug_" + vid + "_" + log_type + "_quic.json"
	tcpmm_file = JSON_FOLDER + log_type + "/tcp/chrome_debug_" + vid + "_" + log_type + "_tcp.json"

	if (type_of_files == "all"):
		files = [tcp_file, quic_file, tcpmm_file, quicmm_file]
		prot_type=["tcp","quic","tcpmm","quicmm"]
		colors = ['g-', 'o-', 'b-', 'r-', 'k']
		marker_type = ['.', '*', '+', 'x']

	elif (type_of_files == "mm"):
		files = [tcpmm_file, quicmm_file]
		prot_type=["tcp","quic"]
		colors = ['b-', 'r-', 'k']
		# prot_type=["tcp1","quic1", "tcp2", "quic2", "tcp3", "quic3", "tcp4", "quic4"]
		# colors = ['b-', 'r-', 'b-.', 'r-.', 'b--', 'r--', 'b:', 'r:', 'k']
		marker_type = ['+', 'x']

	elif (type_of_files == "wmm"):
		files = [tcp_file, quic_file]
		prot_type=["tcp","quic"]
		colors = ['g-', 'o-', 'k']
		marker_type = ['.', '*']

	elif (type_of_files == "qm"):
		files = [quicmm_file]
		prot_type=["quic"]
		colors = ['r-', 'k']
		marker_type = ['x']

	elif (type_of_files == "tm"):
		files = [tcpmm_file]
		prot_type=["tcp"]
		colors = ['b-', 'k']
		marker_type = ['+']

	# print(log_type, vid)
	return files, prot_type, colors, marker_type


def getBWInfo(min_bw = 0, max_bw = 0, jump_bw = 0, initial_bw_change = "", log_type=""):
	
	bw_list = []
	if (log_type in trace_files.keys()):
		for elem in trace_files[log_type]:
			bw_list += [elem["bw"]]
	elif (log_type != ""):
		[min_bw, max_bw, jump_bw, initial_bw_change] = log_type.split('-')
		min_bw = int(min_bw)
		max_bw = int(max_bw)
		jump_bw = int(jump_bw)

	
	if (initial_bw_change == "inc"):
		for bw in range(min_bw, max_bw+jump_bw, jump_bw):
			bw_list += [bw]
		for bw in range(max_bw-jump_bw, min_bw, -1*jump_bw):
			bw_list += [bw]

	elif (initial_bw_change == "dec"):
		for bw in range(max_bw, min_bw+jump_bw-1, -1*jump_bw):
			bw_list += [bw]
		for bw in range(min_bw, max_bw, jump_bw):
			bw_list += [bw]

	# print(*bw_list)
	return bw_list


def plotBW(max_time, bw_list, log_type):
	limit = 240
	bx = []
	by = []

	if ( isinstance(log_type, str) and log_type in trace_files.keys()):
		# print("Sudden")
		bw_times = []
		cur_time = 0
		while (cur_time < max_time):
			for elem in trace_files[log_type]:
				cur_time += elem["time_limit"]
				# print(elem["bw"], elem["time_limit"], cur_time)
				by += [elem["bw"]]
				bx += [cur_time]

				if (cur_time > max_time):
					break

	else:
		# print("Normal")
		bw_len = len(bw_list)
		count = 0
		for time in range(limit, int(max_time)+limit, limit):
			bx += [time]
			by += [bw_list[count % bw_len]]
			count += 1

	
	return bx, by


def plotGraph(title, cur_graph_folder, output_path_1, video_folder, output_path_2):

	plt.title(title)
	plt.tight_layout()

	if (not os.path.isdir(cur_graph_folder)):
		os.mkdir(cur_graph_folder)

	# if (not os.path.isdir(video_folder)):
	# 	os.mkdir(video_folder)

	print("***************************", output_path_1)
	plt.savefig(output_path_1, dpi=200)
	if (output_path_2 != ""):
		plt.savefig(output_path_2, dpi=200)

	print("Graphs plotted!")


def plotMetricGraph(x, y_quic, y_tcp, title, ylabel, output_path, xlabel="Video ID"):
	plt.subplots(figsize=(16,9))
	# plt.figure()
	plt.plot(x, y_quic, "r-x", label="quic")
	plt.plot(x, y_tcp, "b-o", label="tcp")
	plt.legend(prop={ 'size': 7 }, bbox_to_anchor=(1.05, 1), loc='upper left')
	plt.grid()
	plt.xticks(x)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)

	plt.savefig(output_path, dpi=200)


def getBwTimeLimit(cur_time, cur_bw, log_type):
	# print("1:", cur_time, cur_bw, log_type)
	if ( isinstance(log_type, str) and log_type in trace_files.keys()):
		# print("Sudden")
		for elem in trace_files[log_type]:
			if (elem['bw'] == cur_bw):
				return elem['time_limit']

	else:
		# print("Normal")
		return 240


def getQoeFlowGaps(cmt_val, video_info, vid):
	real_time = 0
	video_seeker = 0
	realtime_seeker = 0
	playback_time = 0
	
	avg_bitrate = 0
	avg_bitrate_variation = 0
	avg_stall = 0

	qoe_flow = []
	
	qoe_abv_as_flow = []
	qoe_ab_as_flow = []
	qoe_ab_abv_flow = []
	
	qoe_ab_flow = []
	qoe_abv_flow = []
	qoe_as_flow = []

	metric_flow = []

	x = []
	y = []
	markers = []
	list_bitrate = []
	list_bitrate_variation = []
	list_stall = []
	playback_starttime = cmt_val[0][0]
	real_time = 0
	video_starttime = 0
	
	i = 0
	total_windows = 0
	while i < len(cmt_val): 
		total_windows += 1
		sigma_bitrate = 0
		sigma_bitrate_variation = 0
		sigma_video_segment_length = 0
		avg_video_segment_length = 0
		segment_count = 1
		temp_realtime_seeker = 0

		while (i < len(cmt_val)):
			print("cur video seeker:", cmt_val[i][1], "next vt:", real_time + 50)
			x.append(cmt_val[i][0])
			y.append(cmt_val[i][1])

			# calculating avg bitrate
			bitrate = video_info[vid][str(cmt_val[i][3])]["bitrate"]
			# bitrate = int(cmt_val[i][3].split("p")[0])
			cur_seg_length = y[-1] - video_seeker;
			sigma_bitrate += (cur_seg_length * bitrate)
			sigma_video_segment_length += cur_seg_length
			
			list_bitrate.append(bitrate)

			if (i+1 < len(cmt_val)):
				next_bitrate = video_info[vid][str(cmt_val[i+1][3])]["bitrate"]
				sigma_bitrate_variation += abs(bitrate - next_bitrate)
				if (y[-1] > 0):
					list_bitrate_variation.append((sigma_bitrate_variation / y[-1]) * avg_video_segment_length)

			if (y[-1] > 0):
				list_stall.append(((x[-1] - playback_starttime - y[-1]) / y[-1]) * avg_video_segment_length)
		
			markers.append(marker_map[cmt_val[i][2]])
			
			segment_count += 1
			temp_realtime_seeker = x[-1]
			video_seeker = y[-1]
			
			if (temp_realtime_seeker < real_time + 50):
				realtime_seeker = x[-1]
				i += 1
			else:
				y.pop()
				x.pop()
				break

		real_time += 50
		playback_time = video_seeker - video_starttime
		print("PT:", playback_time)
		video_starttime = video_seeker

		# calculating avg stall


		if (playback_time > 0):
			avg_video_segment_length = sigma_video_segment_length / segment_count
			# print("avg sl:", avg_video_segment_length, "sigma:", sigma_video_segment_length, "count:", segment_count)
			# calculating avg bitrate
			avg_bitrate = sigma_bitrate / playback_time

			# calculating avg bitrate variation
			avg_bitrate_variation = (sigma_bitrate_variation / playback_time) * avg_video_segment_length
			
			playback_endtime = temp_realtime_seeker

			print("PST:", playback_starttime, "PET:", playback_endtime)
			avg_stall = ((playback_endtime - playback_starttime - playback_time) / playback_time) * avg_video_segment_length
			
			if (avg_stall < 0):
				avg_stall = 0

			playback_starttime = realtime_seeker
			# print("AS:", avg_stall, "PE:", playback_endtime, "PS:", playback_starttime, "PT:", playback_time, "AVG SL:", avg_video_segment_length)

		qoe = (avg_bitrate - avg_bitrate_variation) / 1000 - 4.3 * avg_stall
		metric_flow.append([total_windows, avg_bitrate, avg_bitrate_variation, avg_stall])
		qoe_flow.append([total_windows, qoe, avg_bitrate, avg_bitrate_variation, avg_stall])
		
		if ALL_QOE_COMBINATION:
			qoe_ab_abv = (avg_bitrate - avg_bitrate_variation) / 1000
			qoe_ab_as = (avg_bitrate) / 1000 - 4.3 * avg_stall
			qoe_abv_as = (0 - avg_bitrate_variation) / 1000 - 4.3 * avg_stall
			qoe_ab = (avg_bitrate) / 1000
			qoe_abv = (0 - avg_bitrate_variation) / 1000
			qoe_as = 0 - 4.3 * avg_stall

			qoe_abv_as_flow.append([total_windows, qoe_abv_as, avg_bitrate, avg_bitrate_variation, avg_stall])
			qoe_ab_as_flow.append([total_windows, qoe_ab_as, avg_bitrate, avg_bitrate_variation, avg_stall])
			qoe_ab_abv_flow.append([total_windows, qoe_ab_abv, avg_bitrate, avg_bitrate_variation, avg_stall])
			qoe_ab_flow.append([total_windows, qoe_ab, avg_bitrate, avg_bitrate_variation, avg_stall])
			qoe_abv_flow.append([total_windows, qoe_abv, avg_bitrate, avg_bitrate_variation, avg_stall])
			qoe_as_flow.append([total_windows, qoe_as, avg_bitrate, avg_bitrate_variation, avg_stall])

	return metric_flow, qoe_flow, qoe_abv_as_flow, qoe_ab_as_flow, qoe_ab_abv_flow, qoe_ab_flow, qoe_abv_flow, qoe_as_flow

def getQoeFlow(cmt_val, video_info, vid):
	playback_time = 0
	sigma_bitrate = 0
	sigma_bitrate_variation = 0

	qoe_flow = []

	qoe_abv_as_flow = []
	qoe_ab_as_flow = []
	qoe_ab_abv_flow = []

	qoe_ab_flow = []
	qoe_abv_flow = []
	qoe_as_flow = []

	metric_flow = []

	x = []
	y = []
	markers = []
	list_bitrate = []
	list_bitrate_variation = []
	list_stall = []
	sigma_video_segment_length = 0
	playback_starttime = cmt_val[0][0]

	for i in range(len(cmt_val)):
		x.append(cmt_val[i][0])
		y.append(cmt_val[i][1])

		# calculating avg bitrate
		bitrate = video_info[vid][str(cmt_val[i][3])]["bitrate"]
		sigma_bitrate += ((y[-1] - playback_time) * bitrate)
		sigma_video_segment_length += (y[-1] - playback_time)
		inst_avg_video_segment_length = sigma_video_segment_length / (i+1) 

		list_bitrate.append(bitrate)

		# calculating avg bitrate variation
		if (i+1 < len(cmt_val)):
			next_bitrate = video_info[vid][str(cmt_val[i+1][3])]["bitrate"]
			sigma_bitrate_variation += abs(bitrate - next_bitrate)
			print("b:", bitrate, "nb:", next_bitrate, "v:", sigma_bitrate_variation)

			if (y[-1] > 0):
				list_bitrate_variation.append((sigma_bitrate_variation / y[-1]) * inst_avg_video_segment_length)

		if (y[-1] > 0):
			list_stall.append(((x[-1] - playback_starttime - y[-1]) / y[-1]) * inst_avg_video_segment_length)
		playback_time = y[-1]
		markers.append(marker_map[cmt_val[i][2]])

		if (playback_time > 0):
			# calculating avg bitrate
			avg_bitrate = sigma_bitrate / playback_time

			# calculating avg bitrate variation
			avg_bitrate_variation = (sigma_bitrate_variation / playback_time) * inst_avg_video_segment_length
			print(sigma_bitrate_variation, ":", avg_bitrate_variation)

			# calculating avg stall
			playback_endtime = x[-1]
			avg_stall = ((playback_endtime - playback_starttime - playback_time) / playback_time) * inst_avg_video_segment_length
			if (avg_stall < 0):
				avg_stall = 0


			qoe = (avg_bitrate - avg_bitrate_variation) / 1000 - 4.3 * avg_stall
			metric_flow.append([cmt_val[i][1], avg_bitrate,  avg_bitrate_variation, avg_stall])
			qoe_flow.append([cmt_val[i][1], qoe, bitrate, avg_bitrate, avg_bitrate_variation, avg_stall])

			if ALL_QOE_COMBINATION:
				qoe_ab_abv = (avg_bitrate - avg_bitrate_variation) / 1000
				qoe_ab_as = (avg_bitrate) / 1000 - 4.3 * avg_stall
				qoe_abv_as = (0 - avg_bitrate_variation) / 1000 - 4.3 * avg_stall
				qoe_ab = (avg_bitrate) / 1000
				qoe_abv = (0 - avg_bitrate_variation) / 1000
				qoe_as = 0 - 4.3 * avg_stall

				qoe_abv_as_flow.append([cmt_val[i][1], qoe_abv_as, avg_bitrate, avg_bitrate_variation, avg_stall])
				qoe_ab_as_flow.append([cmt_val[i][1], qoe_ab_as, avg_bitrate, avg_bitrate_variation, avg_stall])
				qoe_ab_abv_flow.append([cmt_val[i][1], qoe_ab_abv, avg_bitrate, avg_bitrate_variation, avg_stall])
				qoe_ab_flow.append([cmt_val[i][1], qoe_ab, avg_bitrate, avg_bitrate_variation, avg_stall])
				qoe_abv_flow.append([cmt_val[i][1], qoe_abv, avg_bitrate, avg_bitrate_variation, avg_stall])
				qoe_as_flow.append([cmt_val[i][1], qoe_as, avg_bitrate, avg_bitrate_variation, avg_stall])
	
	return metric_flow, qoe_flow, qoe_abv_as_flow, qoe_ab_as_flow, qoe_ab_abv_flow, qoe_ab_flow, qoe_abv_flow, qoe_as_flow, list_bitrate, list_bitrate_variation, list_stall, avg_bitrate, avg_bitrate_variation, avg_stall, x[-1]

base_trace_files = {
	# bw in kbps
	# time_limit in seconds
	"dynamic-very-low": [
		{
			"bw": 64,
			"time_limit": 60 
		},
		{
			"bw": 128,
			"time_limit": 60
		},
		{
			"bw": 192,
			"time_limit": 60
		},
		{
			"bw": 256,
			"time_limit": 60
		},
		{
			"bw": 192,
			"time_limit": 60
		},
		{
			"bw": 128,
			"time_limit": 60
		},
	],
	"dynamic-low": [
		{
			"bw": 640,
			"time_limit": 240
		},
		{
			"bw": 384,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 240
		},
		{
			"bw": 384,
			"time_limit": 240
		},
	],
	"dynamic-high": [
		{
			"bw": 1152,
			"time_limit": 240
		},
		{
			"bw": 896,
			"time_limit": 240
		}
	],
	"sudden-2": [
		{
			"bw": 2048,
			"time_limit": 120
		},
		{
			"bw": 512,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 480
		},
		{
			"bw": 1024,
			"time_limit": 240
		},
	],
	"sudden-3": [
		{
			"bw": 2048,
			"time_limit": 240
		},
		{
			"bw": 1024,
			"time_limit": 240
		},
		{
			"bw": 512,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 240
		},
	],
	"sudden-4": [
		{
			"bw": 2048,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 120
		},
	],
	"sudden-6": [
		{
			"bw": 2048,
			"time_limit": 20
		},
		{
			"bw": 512,
			"time_limit": 60
		},
		{
			"bw": 128,
			"time_limit": 120
		}
	],
}


trace_files = {
	"no-throttler": [
		{
			"bw": 1,
			"time_limit": 240
		}
	],
	"dynamic-low": base_trace_files["dynamic-low"],
	"dynamic-low-v2": base_trace_files["dynamic-low"],
	"dynamic-low-v3": base_trace_files["dynamic-low"],
	"dynamic-low-parallel-v4": base_trace_files["dynamic-low"],
	"dynamic-low-gs": base_trace_files["dynamic-low"],
	"dynamic-low-nys": base_trace_files["dynamic-low"],
	"dynamic-low-ss": base_trace_files["dynamic-low"],
	"dynamic-low-mr1": base_trace_files["dynamic-low"],
	"dynamic-low-mr2": base_trace_files["dynamic-low"],
	"dynamic-low-mr3": base_trace_files["dynamic-low"],
	"dynamic-high": [
		{
			"bw": 1152,
			"time_limit": 240
		},
		{
			"bw": 896,
			"time_limit": 240
		}
	],
	"dynamic-high-v2": [
		{
			"bw": 1152,
			"time_limit": 240
		},
		{
			"bw": 896,
			"time_limit": 240
		}
	],
	"sudden-2": [
		{
			"bw": 2048,
			"time_limit": 120
		},
		{
			"bw": 512,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 480
		},
		{
			"bw": 1024,
			"time_limit": 240
		},
	],
	"sudden-3": [
		{
			"bw": 2048,
			"time_limit": 240
		},
		{
			"bw": 1024,
			"time_limit": 240
		},
		{
			"bw": 512,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 240
		},
	],
	"sudden-4": [
		{
			"bw": 2048,
			"time_limit": 240
		},
		{
			"bw": 128,
			"time_limit": 120
		},
	],
	"sudden-6": [
		{
			"bw": 2048,
			"time_limit": 20
		},
		{
			"bw": 512,
			"time_limit": 60
		},
		{
			"bw": 128,
			"time_limit": 120
		}
	],
}


videos_list = {
	"video-list-1" : [
		"4b4MUYve_U8",
		"05FBD6wFi7E",
		"7_R5M56QALM",
		"8IavDw9Uhwg",
		"Ac4f0ha2l1g",
		"AnlCPdB4OA4",
		"DYZ5Ef_HQE4",
		"HcrgwwVj8Xk",
		"jEUaZEul13c",
		"JzS8rv2i0QA",
		"m-5dG8-kveA",
		"nhFL_mg-fF0", # RM
		"nqwjGaxqDMA",
		"O6Iiy_YOe4Y",
		"PvLauGfc_ys",
		"q6UVlhEBhpk",
		"Unzc731iCUY",
		"UtHbm8xqpjE"
	],

	"video-list-2" : [
		"9-24INx2w7A",
		"1vhJrQ6jjfI",
		"69mLWKom4JA",
		"ebsAyKkXas0",
		"fsCoFYI6GLk",
		"HOgzSrAhkGc",
		"HsJupanmVJU",
		"hvxGYK2Oqto",
		"LjhVENuPptc",
		"oZei5FnBsLI",
		"qz9BzXeTr4M",
		"xEUoeAHQiwc",
		"zi6JrVdN4dE",
	],

	"video-list-3" : [
		"8hqzTX9NGLw", # 
		"yBi0LTmkbN8",
		"1WQCBJRVYcE",
		"Au7p14uPI8w",
		"a6oTJlXyLL4",
		"ng5Qg3XDnFs",
		"bPiofmZGb8o",
		"wW1lY5jFNcQ",
		"Lc1__3Qcy2M",
		"dmDbesougG0",
	],

	"video-list-4" : [
		"bijS0H7bSSk",
		"OBmP_7k2h_4",
		"o57MPQLdnxY",
		"eaCxMqulz3k",
		"OYZMdAivLqc",
		"5-elZ34LAo8",
		"IzRYraztZVA",
		"PYjf8g4kGyE",
		"ZGKaamC4FnE",
		"zbEnOYtsXHA",
	],


	"video-list-5" : [
		"1vhJrQ6jjfI", # scheduled #1
		"4b4MUYve_U8", # scheduled
		"8hqzTX9NGLw", # done #2
		"HOgzSrAhkGc", # done
		"JzS8rv2i0QA", # done #3
		"O6Iiy_YOe4Y", # scheduled
		"o57MPQLdnxY", # scheduled
		"PvLauGfc_ys", # scheduled
		"Unzc731iCUY", # scheduled
		"xEUoeAHQiwc", # done
		"a6oTJlXyLL4",
		"Au7p14uPI8w",
		"1WQCBJRVYcE",
		"q6UVlhEBhpk",
		"bijS0H7bSSk",
		"yBi0LTmkbN8",
	],

	"video-list-sudden": [
		"Ac4f0ha2l1g",
		"HsJupanmVJU",
		"JzS8rv2i0QA",
		"O6Iiy_YOe4Y",
		"PvLauGfc_ys",
		"Unzc731iCUY"
	],

	"video-list-7" : [
		"3UAH3sqKLGo",
		"4QcHHal-pt4",
		"7hnUYWkMZ70",
		"8fbw41hT2fY",
		"44U8AY7iXwM",
		"aXwCrtAo4Wc",
		"b_0At3AI5vI",
		"C6jJg9Zan7w",
		"d3UCW_AV93M",
		"fSbINA1WWRs",
		"g1dJQAs65O8",
		"iyBbXFKEmUs",
		"jSJ6uLkf35g",
		"KfugZksSp5g",
		"kKgoHp4M1Qg",
		"lsJBGvyiAHI",
		"N_pNS1wF6gA",
		"SqQIvR0N3lk",
		"SxItzffU9ww",
		"TjmzoBIsKd0",
		"URyi3m2CFmc",
		"UyZPBocGiR8",
		"VbpF3vuPGYw",
		"Vjw7wAZqSM4",
		"VQEgFZCLScw",
		"WaRVCWuhQxM",
		"x7GvOM4zULI",
		"yESbHdkSU1M",
		"yMg5DokVZJw",
		"YWHxE0F2IoI",
	],

	"video-list-7-temp" : [
		"WaRVCWuhQxM",
		"SxItzffU9ww",
		"YWHxE0F2IoI",
		# "TjmzoBIsKd0",
		"d3UCW_AV93M",
		"kKgoHp4M1Qg",
		"URyi3m2CFmc",
		"OMUEmWGxoVg",
		"lsJBGvyiAHI",
		"yESbHdkSU1M",
		"VQEgFZCLScw",
		"iyBbXFKEmUs",
		"yMg5DokVZJw",
		"7hnUYWkMZ70",
		"UyZPBocGiR8",
	],

	"video-list-7-temp2" : [
		"WaRVCWuhQxM",
		"SxItzffU9ww",
		"YWHxE0F2IoI",
		"d3UCW_AV93M",
		"kKgoHp4M1Qg",
		"URyi3m2CFmc",
		"OMUEmWGxoVg",
		"lsJBGvyiAHI",
		"yESbHdkSU1M",
		"yMg5DokVZJw",
		"UyZPBocGiR8",
		"PvLauGfc_ys",
		"Ac4f0ha2l1g"
	],

	# new videos with 3 slots
	"video-list-8": [
		"-SI0HKTfHN4",
		"3UAH3sqKLGo",
		"4QcHHal-pt4",
		"8fbw41hT2fY",
		"Ac4f0ha2l1g",
		"aXwCrtAo4Wc",
		"b_0At3AI5vI",
		"C6jJg9Zan7w",
		"fSbINA1WWRs",
		"g1dJQAs65O8",
		"iqnSO7azw9A",
		"jSJ6uLkf35g",
		"KfugZksSp5g",
		"LEJVf5S8mF8",
		"N_pNS1wF6gA",
		"PJVtsVpsAWo",
		"SqQIvR0N3lk",
		"VbpF3vuPGYw",
		"Vjw7wAZqSM4",
		"x7GvOM4zULI",
		"ZAWKCE2DX5s",
		"ziruq8L5RBk",
		"O6Iiy_YOe4Y",
		"PvLauGfc_ys",
		"Unzc731iCUY",
		"44U8AY7iXwM",
		"1vhJrQ6jjfI",
		"4b4MUYve_U8",
		"9-24INx2w7A",
		"AnlCPdB4OA4",

		
		# removed
		# "bijS0H7bSSk",
		
		"HsJupanmVJU",
		"jEUaZEul13c",
		"JzS8rv2i0QA",
		"NisfIUglozc",
		"nqwjGaxqDMA",
		
		# removed
		# "q6UVlhEBhpk",
		
		"QLJzjp1n5X4",
		"d_SHgEul5DY",
		"fsCoFYI6GLk",
		"hvxGYK2Oqto",
		"iPgYplU2u6Q",
		"LjhVENuPptc",
		"oIaIejhTRy0",
		"oZei5FnBsLI",
		"zi6JrVdN4dE",

		# more videos
		"SegxEqthbbk",
		"HIQ1kDKiBgs"
	]
}

videos = {
	# TRACEFILE : 128-1152-256-dec
		"128-1152-256-dec": {
			"video-list-1" : videos_list["video-list-1"],
			"video-list-2" : videos_list["video-list-2"],
			"video-list-3" : videos_list["video-list-3"],
			"video-list-4" : videos_list["video-list-4"],
			"no-slot": videos_list["video-list-8"],
			"afternoon": videos_list["video-list-8"],
			"evening": videos_list["video-list-8"],
		},

		"128-2048-64-dec": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
			# "video-list-5": videos_list["video-list-5"][:10],
			# "video-list-6" : videos_list["video-list-6"]
		},

		"128-2048-64-inc": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
			# "video-list-5" : videos_list["video-list-5"],
			# "video-list-6": videos_list["video-list-6"]
		},

		"256-256-256-inc": {
			"video-list-7" : videos_list["video-list-7"]
		},

		"768-768-768-inc": {
			"video-list-7" : videos_list["video-list-7"]
		},

		"sudden-6": {
			"video-list-7" : videos_list["video-list-7-temp2"],
			"no-slot": videos_list["video-list-8"],
			"afternoon": videos_list["video-list-8"],
			"evening": videos_list["video-list-8"],
		},

		"dynamic-high": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
		},

		"dynamic-low": {
			"no-slot": videos_list["video-list-8"],
			"slot": videos_list["video-list-8"],
		},
		
		"dynamic-low-gs": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
		},

		"dynamic-low-nys": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
		},

		"dynamic-low-ss": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
		},
		"no-throttler": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
		},
		"64-256-64-inc": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],
		},
		"640-1152-128-inc": {
			"slot": videos_list["video-list-8"],
			"no-slot": videos_list["video-list-8"],

		}
	}


marker_map = {
	"144p" : ".", # point
	"240p" : "s", # square
	"360p" : "^", # triangle
	"480p" : "d", # diamond
	"720p" : "*", # star
	"1080p" : "+", # plus
}


marker_color_map = {
	"144p" : "b", # point
	"240p" : "g", # square
	"360p" : "c", # triangle
	"480p" : "y", # diamond
	"720p" : "m", # star
	"1080p" : "#cc4bc1", # plus		
}


color_map_quicmm = {
	"144p" : '#72BDF3', # blue
	"240p" : '#FF9D9D', # red
	"360p" : '#00F9FF', # green
	"480p" : '#FFFB00', # yellow
	"720p" : '#E100FF', # magenta
	"1080p" : '#C13A00', # brown
}


color_map_tcpmm = {
	"144p" : '#0094FF',
	"240p" : '#FF0000',
	"360p" : '#02ADA6',
	"480p" : '#D3BD08',
	"720p" : '#760379',
	"1080p" : '#691F00',
}