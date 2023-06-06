import video_data
from video_data import *
from collections import Counter
import pdb

if __name__ == '__main__':

	video_list_folder = sys.argv[4]
	log_type = sys.argv[3]
	to_save = ""
	
	quic_video_files = getQuicFilesList(video_list_folder, log_type)

	total_videos = 0
	y_ab_tcp = []
	y_ab_quic = []
	y_abv_quic = []
	y_abv_tcp = []
	y_s_tcp = []
	y_s_quic = []

	count = 0
	metrics = []
	final_qoe = []
	packet_counts = []
	packet_bytes = []
	startup_delay = []

	response_latency_csv = []

	log_type, bw_list, to_save, video_list_id = parseSysArgs(sys.argv)
	bw_len = len(bw_list)
	
	video_count = 0
	for vid in videos[log_type][video_list_id]:
		# loop over each file
		count += 1

		video_count += 1

		if (vid not in quic_video_files.keys()):
			continue
		
		with open(video_data.VIDEO_INFO_JSON_FILE, "r") as tmp:
			video_info = json.load(tmp)

		all_qual, y_ticks, mapping = getVideoQualTicks(video_info[vid].values())
		
		files, prot_type, colors, _ = getFilesInfo(log_type, sys.argv[1], vid)
		quic_files = quic_video_files[vid]

		for quic_file in quic_files:

			# loop over different network protocol configuration for each video
			cur = 0
			max_time = 0
			tcp_file = quic_file.replace("quic", "tcp")

			if (not os.path.isfile(tcp_file)):
				continue

			if (to_save == "draw_graphs"):
				fig, p1 = plt.subplots(figsize=(16,9))
				p2 = p1.twinx()
				p1.set_xlabel("Real Time (s)")
				p1.set_ylabel("PlaybackTime (s)")
				p2.set_ylabel("Bandwidth (kbps)")

			elif ("stats" in to_save):
				fig, p3 = plt.subplots(figsize=(16,9))
				if (to_save == "save_bitrate_stats"):
					p3.set_xlabel("Bitrate (Kbps)")
					p3.set_ylabel("CDF ")

				elif (to_save == "save_bitrate_variation_stats"):
					p3.set_xlabel("Bitrate Variations(Kbps)")
					p3.set_ylabel("CDF ")

				elif (to_save == "save_stall_stats"):
					p3.set_xlabel("Stall (s)")
					p3.set_ylabel("CDF ")
			
			elif ("draw_combined_metrics" in to_save):
				fig, p6 = plt.subplots(figsize=(16,9))
				p7 = p6.twinx()
				p6.set_xlabel("Real Time (s)")
				p6.set_ylabel("Stall Time (s)")
				p7.set_ylabel("Bitrate/Bitrate Variation (Mbps)")
				
			elif (to_save == "draw_qoe_flow"):
				fig, p4 = plt.subplots(figsize=(16,9))
				p4.set_xlabel("Real Time")
				p4.set_ylabel("QOE")
			
			elif (to_save == "draw_tput_flow"):
				fig, p4 = plt.subplots(figsize=(16,9))
				p8 = p4.twinx()
				p4.set_xlabel("Real Time")
				p4.set_ylabel("Throughput (kbytes/sec)")
				p8.set_ylabel("Bandwidth (kbps)")

			elif (to_save == "draw_response_flow"):
				fig, p4 = plt.subplots(figsize=(16,9))
				p8 = p4.twinx()
				p4.set_xlabel("Real Time")
				p4.set_ylabel("Response Latency (sec)")
				p8.set_ylabel("Bandwidth (kbps)")

			elif (to_save == "draw_ab_flow"):
				fig, p5 = plt.subplots(figsize=(16,9))
				p5.set_xlabel("Real Time")
				p5.set_ylabel("Average Bitrate (kbps)")
			
			elif (to_save == "draw_abv_flow"):
				fig, p5 = plt.subplots(figsize=(16,9))
				p5.set_xlabel("Real Time")
				p5.set_ylabel("Average Bitrate Variation (kbps)")
			
			elif (to_save == "draw_s_flow"):
				fig, p5 = plt.subplots(figsize=(16,9))
				p5.set_xlabel("Real Time")
				p5.set_ylabel("Average Stall (s)")
			
			video_id = "v" + str(video_count)
			print("\n", video_id, vid)

			if (video_list_folder == "slot"):
				slot = quic_file.split(".json")[0].split("_")[-1]
				video_id += "_" + slot

			files = [tcp_file, quic_file]
			for file in files:
				print(file)
				keyerror_flag = False

				if ("quic" in file):
					# metric_key = vid + "_quic"
					metric_key = video_id + "_quic"

				else:
					# metric_key = vid + "_tcp"
					metric_key = video_id + "_tcp"

				cmt_val = []
				throughput_flow = []
				response_latency = []
				
				with open(file, "r") as tmp:
					json_obj = json.load(tmp)

				total_segments_requested = 0
				video_segment_length_sum = 0
				dur = -1
				time_taken = 0
				packet_size = 0
				check_startup_delay = True
				stall_till_last_segment = 0

				cur_bw_index = 0
				cur_bw = bw_list[cur_bw_index]
				cur_time = 0
				cur_bw_time_limit = getBwTimeLimit(cur_time, cur_bw, log_type)

				for req_id in json_obj:
					print("yaha tak theek h", json_obj[req_id])
					if (json_obj[req_id]["type"] == "videoplayback" and "complete_ts" in json_obj[req_id]):
						
						if (dur == -1):
							dur = json_obj[req_id]["complete_dur"]
						total_segments_requested += 1

						# calculating video segment length in time units
						clen = json_obj[req_id]["complete_clen"]
						video_range_bytes = json_obj[req_id]["complete_range"]
						video_range_dur = ((video_range_bytes[1] - video_range_bytes[0]) / clen) * dur

						packet_size += video_range_bytes[1] - video_range_bytes[0]
						diff = (float(json_obj[req_id]["complete_ts"]) - float(json_obj[req_id]["request_ts"]))
						time_taken += diff

						response_latency.append([json_obj[req_id]["complete_ts"], time_taken / total_segments_requested])

						# throughput_flow.append(packet_size / time_taken)
						throughput_flow.append([json_obj[req_id]["complete_ts"], (packet_size / time_taken)])
						
						# adding the segment's length
						video_segment_length_sum += video_range_dur



					if (json_obj[req_id]["type"] == "streamingstats" and "itag" in json_obj[req_id].keys()):
						print("yaha kya haal h")
						itag = json_obj[req_id]["itag"]
						
						# try:
						# 	vid_qual = video_info[vid][str(itag)]["qualityLabel"].split("p")[0] + "p"
						# except Exception as e:
						# 	keyerror_flag = True
						# 	print("yaha kya haal h-3",e)
						# 	break
						vid_qual = video_info[vid][str(itag)]["qualityLabel"].split("p")[0] + "p"

						if ("cmt" in json_obj[req_id].keys()):
							cmt = json_obj[req_id]["cmt"].split(',')
							for c in cmt:
								c = c.split(":")
								stall_till_current_segment = max(float(c[0]) - float(c[1]), 0)
								current_stall = max(stall_till_current_segment - stall_till_last_segment, 0)
								stall_till_last_segment = stall_till_current_segment
								request_ts = float(c[0])
								if (request_ts >= cur_bw_time_limit):
								  cur_bw_index = (cur_bw_index + 1) % bw_len
								  cur_bw = bw_list[cur_bw_index]
								  time_limit = getBwTimeLimit(request_ts, cur_bw, log_type)
								  cur_bw_time_limit += time_limit
								cmt_val.append([float(c[0]), float(c[1]), vid_qual, itag, current_stall, cur_bw])

							if ("buffer_health" in json_obj[req_id].keys()):
								bh = (json_obj[req_id]["buffer_health"].split(',')[-1]).split(":")
								if (bh[1] == str(dur)):
									bh[0] = str(float(bh[0]) + (dur - cmt_val[-1][1]))
									cmt_val.append([float(bh[0]), float(bh[1]), vid_qual, itag, 0, cur_bw])
									break

						if (check_startup_delay and "vps" in json_obj[req_id].keys()):
							vps = json_obj[req_id]["vps"].split(',')
							for v in vps:
								v = v.split(":")
								if (v[1] == "PL"):
									print(metric_key, v)
									startup_delay.append([metric_key, float(v[0])])
									check_startup_delay = False
									break

				if (keyerror_flag):
					continue

				packet_counts.append([metric_key, total_segments_requested, packet_size])
				cmt_val.sort()

				if (to_save == "create_cmt_csv"):
					fields = ["real_time (s)", "video_playback_time (s)", "video_quality", "bitrate (kbps)", "stall_in_this_segment (s)", "bandwidth"]

					csvfolder = video_data.CSV_FOLDER + log_type + "/" + prot_type[cur] + "_cmt"

					if (not os.path.isdir(csvfolder)):
						os.mkdir(csvfolder)
					
					csvfilename = csvfolder + "/" + video_id + "_" + prot_type[cur] + ".csv"
					with open(csvfilename, 'w', newline='') as csvfile:
						csvwriter = csv.writer(csvfile)
						# writing the fields  
						csvwriter.writerow(fields)
						# writing the data rows  
						csvwriter.writerows(cmt_val)
					cur += 1
					continue

				avg_video_segment_length = video_segment_length_sum / total_segments_requested; # time units (s)
				
				metric_flow, qoe_flow, qoe_abv_as_flow, qoe_ab_as_flow, qoe_ab_abv_flow, qoe_ab_flow, qoe_abv_flow, qoe_as_flow, list_bitrate, list_bitrate_variation, list_stall, avg_bitrate, avg_bitrate_variation, avg_stall, time = video_data.getQoeFlow(cmt_val, video_info, vid)

				max_time = max(max_time, time)
				
				if (to_save == "draw_tput_flow"):
					x_tput = []
					y_tput = []
					for throughput in throughput_flow:
						x_tput += [throughput[0]]
						y_tput += [throughput[1]]
					
					# print(y_tput)
					p4.plot(x_tput[15:], y_tput[15:], colors[cur], label=prot_type[cur])
				
				elif (to_save == "draw_response_flow"):

					response_latency_csv.append([metric_key, response_latency[-1][1]])
					
					x_response_latency = []
					y_response_latency = []
					for response in response_latency:
						x_response_latency += [response[0]]
						y_response_latency += [response[1]]
					
					# print(y_response_latency)
					p4.plot(x_response_latency[15:], y_response_latency[15:], colors[cur], label=prot_type[cur])

				elif (to_save == "draw_qoe_flow"):
					x_qoe = []
					y_qoe = []
					for qoe in qoe_flow:
						x_qoe += [qoe[0]]
						y_qoe += [qoe[1]]

					p4.plot(x_qoe, y_qoe, colors[cur], label=prot_type[cur])
				
				if (to_save == "draw_ab_flow" or to_save == "draw_combined_metrics"):
					x_metric = []
					y_metric = []
					for metric in metric_flow:
						x_metric += [metric[0]]
						y_metric += [metric[1] / 1000]
					
					if (to_save == "draw_combined_metrics"):
						if (cur == 0): # tcp
							p7.plot(x_metric, y_metric, color="lime", linestyle="-", label=prot_type[cur] + ":ab")
						else:
							p7.plot(x_metric, y_metric, color="darkgreen", linestyle="-", label=prot_type[cur] + ":ab")

					else:
						p5.plot(x_metric, y_metric, colors[cur], label=prot_type[cur])

				if (to_save == "draw_abv_flow" or to_save == "draw_combined_metrics"):
					x_metric = []
					y_metric = []
					for metric in metric_flow:
						x_metric += [metric[0]]
						y_metric += [metric[2] / 1000]
					
					if (to_save == "draw_combined_metrics"):
						if (cur == 0):
							p7.plot(x_metric, y_metric, color="lightcoral", linestyle="--", label=prot_type[cur] + ":abv")
						else:
							p7.plot(x_metric, y_metric, color="red", linestyle="--", label=prot_type[cur] + ":abv")
					else:
						p5.plot(x_metric, y_metric, colors[cur], label=prot_type[cur])

				if (to_save == "draw_s_flow" or to_save == "draw_combined_metrics"):
					x_metric = []
					y_metric = []
					for metric in metric_flow:
						x_metric += [metric[0]]
						y_metric += [metric[3]]
					
					if (to_save == "draw_combined_metrics"):
						if (cur == 0):
							p6.plot(x_metric, y_metric, color="violet", linestyle="-.", label=prot_type[cur] + ":as")
						else:
							p6.plot(x_metric, y_metric, color="indigo", linestyle="-.", label=prot_type[cur] + ":as")

					else:
						p5.plot(x_metric, y_metric, colors[cur], label=prot_type[cur])
				
				elif (to_save == "create_video_qoe_csv"):
					fields = ["real_time", "qoe", "bitrate", "avg_bitrate", "avg_bitrate_variation", "avg_stall"]

					basecsvfolder = video_data.CSV_FOLDER + log_type + "/" + prot_type[cur]
					folders_required = ["_qoe"]
					if (ALL_QOE_COMBINATION):
						folders_required += EXTRA_QOE_FOLDERS_REQUIRED
						
					for folder in folders_required:
						csvfolder = basecsvfolder + folder
						if (not os.path.isdir(csvfolder)):
							os.mkdir(csvfolder)

						csvfilename = csvfolder + "/" + video_id + "_" + prot_type[cur] + ".csv"
						with open(csvfilename, 'w', newline='') as csvfile:
							csvwriter = csv.writer(csvfile)
							# writing the fields  
							csvwriter.writerow(fields)
							# writing the data rows  
							if (folder == "_qoe"):
								csvwriter.writerows(qoe_flow)
							elif (folder == "_qoe-ab-abv"):
								csvwriter.writerows(qoe_ab_abv_flow)
							elif (folder == "_qoe-ab-as"):
								csvwriter.writerows(qoe_ab_as_flow)
							elif (folder == "_qoe-abv-as"):
								csvwriter.writerows(qoe_abv_as_flow)
							elif (folder == "_qoe-ab"):
								csvwriter.writerows(qoe_ab_flow)
							elif (folder == "_qoe-abv"):
								csvwriter.writerows(qoe_abv_flow)
							elif (folder == "_qoe-as"):
								csvwriter.writerows(qoe_as_flow)
						
				
				elif (to_save == "create_response_latency_csv"):
					fields = ["real_time", "response_latency"]
					csvfolder = video_data.CSV_FOLDER + log_type + "/rl_" + prot_type[cur]

					if (not os.path.isdir(csvfolder)):
						os.mkdir(csvfolder)

					csvfilename = csvfolder + "/" + video_id + "_" + prot_type[cur] + ".csv"
					with open(csvfilename, 'w', newline='') as csvfile:
						csvwriter = csv.writer(csvfile)
						# writing the fields  
						csvwriter.writerow(fields)
						# writing the data rows  
						csvwriter.writerows(response_latency)
				
				list_bitrate.sort()
				list_bitrate_variation.sort()
				list_stall.sort()

				frequency_bitrate = Counter(list_bitrate)
				frequency_bitrate_variation = Counter(list_bitrate_variation)
				frequency_stall = Counter(list_stall)

				pdf_bitrate=[]
				sum_frequency_bitrate=sum(frequency_bitrate.values())

				pdf_bitrate_variation=[]
				sum_frequency_bitrate_variation=sum(frequency_bitrate_variation.values())

				pdf_stall=[]
				sum_frequency_stall=sum(frequency_stall.values())

				for i in frequency_bitrate.keys():
					pdf_bitrate.append(frequency_bitrate[i] / sum_frequency_bitrate)
				
				for i in frequency_bitrate_variation.keys():
					pdf_bitrate_variation.append(frequency_bitrate_variation[i] / sum_frequency_bitrate_variation)
				
				for i in frequency_stall.keys():
					pdf_stall.append(frequency_stall[i] / sum_frequency_stall)

				cdf_bitrate = np.cumsum(pdf_bitrate) # plt.plot(list_bitrate,cdf_bitrate)  1 graph for each video
				cdf_bitrate_variation = np.cumsum(pdf_bitrate_variation)
				cdf_stall = np.cumsum(pdf_stall)

				metrics.append([metric_key, avg_bitrate, avg_bitrate_variation, avg_stall])
				final_qoe.append([metric_key, (avg_bitrate-avg_bitrate_variation) * 1024 - 4.3 * avg_stall]) #single graph for all videos

				if (to_save =="draw_graphs"):
					p1.plot(x, y, colors[cur], label=prot_type[cur])

				elif (to_save =="save_bitrate_stats"):
					p3.plot([0] + list(frequency_bitrate.keys()), [0] + list(cdf_bitrate), colors[cur], label=prot_type[cur])
				
				elif (to_save =="save_bitrate_variation_stats"):
					p3.plot([0] + list(frequency_bitrate_variation.keys()), [0] + list(cdf_bitrate_variation), colors[cur], label=prot_type[cur])
				
				elif (to_save =="save_stall_stats"):
					p3.plot([0] + list(frequency_stall.keys()), [0] + list(cdf_stall), colors[cur], label=prot_type[cur])

				cur += 1

			if (to_save == "draw_tput_flow"):
				bx, by = plotBW(max_time, bw_list, log_type)
				p8.step(bx, by, colors[-1], label="bandwidth")

				p4.grid(True)
				
				handles, labels = p4.get_legend_handles_labels()
				handle = []
				label = []
				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])
				p4.legend(handles, label, bbox_to_anchor=(1.40, 1), loc='upper right')

				handles, labels = p8.get_legend_handles_labels()
				p8.legend(handles, labels, bbox_to_anchor=(1.40, 1.10), loc='upper right')

				plt.xticks(np.arange(0, max_time, 200.0))
				p4.tick_params(axis='x', labelsize=8)

				title = "Tput vs RealTime (" + vid + "_" + video_id + ")"

				cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/tput_flow" 
				output_path_1 = cur_graph_folder + "/" + video_id + "_" + vid + "_" + "_tput_flow.png"

				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + "_tput_flow.png"

				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")
			
			elif (to_save == "draw_response_flow"):
				bx, by = plotBW(max_time, bw_list, log_type)
				p8.step(bx, by, colors[-1], label="bandwidth")

				p4.grid(True)
				
				handles, labels = p4.get_legend_handles_labels()
				handle = []
				label = []
				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])
				p4.legend(handles, label, bbox_to_anchor=(1.40, 1), loc='upper right')

				handles, labels = p8.get_legend_handles_labels()
				p8.legend(handles, labels, bbox_to_anchor=(1.40, 1.10), loc='upper right')

				plt.xticks(np.arange(0, max_time, 200.0))
				p4.tick_params(axis='x', labelsize=8)

				title = "Response Latency vs RealTime (" + vid + "_" + video_id + ")"

				cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/response_latency_flow/" 
				output_path_1 = cur_graph_folder + video_id + "_" + vid + "_" + "_response_flow.png"

				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + "_response_flow.png"

				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")

			elif (to_save == "draw_qoe_flow"):
				p4.grid(True)
				
				handles, labels = p4.get_legend_handles_labels()
				handle = []
				label = []
				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])
				p4.legend(handles, label, bbox_to_anchor=(1.40, 1), loc='upper right')

				plt.xticks(np.arange(0, max_time, 200.0))
				p4.tick_params(axis='x', labelsize=8)

				title = "QOE vs RealTime (" + vid + "_" + video_id + ")"

				cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/qoe_flow/" 
				output_path_1 = cur_graph_folder + video_id + "_" + vid + "_" + "_qoe_flow.png"

				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + "_qoe_flow.png"
				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")
			
			elif (to_save == "draw_ab_flow" or to_save == "draw_abv_flow" or to_save == "draw_s_flow"):
				p5.grid(True)
				
				handles, labels = p5.get_legend_handles_labels()
				handle = []
				label = []
				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])
				p5.legend(handles, label, bbox_to_anchor=(1.40, 1), loc='upper right')

				plt.xticks(np.arange(0, max_time, 200.0))
				p5.tick_params(axis='x', labelsize=7)

				if (to_save == "draw_ab_flow"):
					title = "Average Bitrate vs RealTime (" + vid + "_" + video_id + ")"
					folder_name = "ab_flow"
				elif (to_save == "draw_abv_flow"):
					title = "Average Bitrate Variation vs RealTime (" + vid + "_" + video_id + ")"
					folder_name = "abv_flow"
				elif (to_save == "draw_s_flow"):
					title = "Average Stall vs RealTime (" + vid + "_" + video_id + ")"
					folder_name = "s_flow"

				cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/" + folder_name + "/" 
				output_path_1 = cur_graph_folder + video_id + "_" + vid + "_" + "_" + folder_name + ".png"

				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + "_" + folder_name + ".png"
				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")

			elif ("stats" in to_save):
				p3.grid(True)
				
				handles, labels = p3.get_legend_handles_labels()
				handle = []
				label = []

				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])

				p3.legend(handle, label, loc = "upper right", bbox_to_anchor=(1.40, 1))

				filename = ""
				title = ""
				cur_graph_folder = ""
				if (to_save == "save_bitrate_stats"):
					title = "CDF of Bitrate (" + vid + ")"
					cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/cdfs_bitrate"
					filename = "cdfs_bitrate.png"
				elif (to_save == "save_bitrate_variation_stats"):
					title = "CDF of Bitrate Variation (" + vid + ")"
					cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/cdfs_bitrate_variations" 
					filename = "cdfs_bitrate_variation.png"
				elif (to_save == "save_stall_stats"):
					title = "CDF of Stall (" + vid + ")"
					cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/cdfs_stall" 
					filename = "cdfs_stall.png"

				output_path_1 = cur_graph_folder + video_id + "_" + vid + "_" + "_" + filename
				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + "_" + filename
				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")

			elif (to_save == "draw_combined_metrics"):
				# bx, by = plotBW(max_time, bw_list, log_type)
				# p7.step(bx, by, colors[-1], label="bandwidth")

				p6.grid(True)
				
				handles, labels = p6.get_legend_handles_labels()
				handle = []
				label = []

				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])

				p6.legend(handle, label, loc = "upper right", bbox_to_anchor=(1.40, 1))
				
				handles, labels = p7.get_legend_handles_labels()
				p7.legend(handles, labels, bbox_to_anchor=(1.40, 0.8), loc='upper right')
				
				filename = "combined_metrics.png"
				
				if ("high" in log_type):
					title = "Combined Metrics: high bw ( " + video_id + ":" + vid + " )"
				else:
					title = "Combined Metrics: low bw ( " + video_id + ":" + vid + " )"

				cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/combined_metrics/"

				output_path_1 = cur_graph_folder + video_id + "_" + vid + "_" + filename
				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + filename
				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")

			elif (to_save =="draw_graphs"):
				bx, by = plotBW(max_time, bw_list, log_type)
				p2.step(bx, by, colors[-1], label="bandwidth")

				p1.grid(True)
				
				handles, labels = p1.get_legend_handles_labels()
				handle = []
				label = []
				for i in range(len(handles)):
					if (labels[i] not in label):
						handle.append(handles[i])
						label.append(labels[i])
				p1.legend(handles, label, bbox_to_anchor=(1.40, 1), loc='upper right')
				handles, labels = p2.get_legend_handles_labels()
				p2.legend(handles, labels, bbox_to_anchor=(1.40, 1.10), loc='upper right')

				plt.xticks(np.arange(0, max_time, 50.0))
				p1.tick_params(axis='x', labelsize=4)

				title = "PlaybackTime vs RealTime (" + vid + ")"

				cur_graph_folder = video_data.GRAPHS_FOLDER + log_type + "/real_vs_watchtime/" 
				output_path_1 = cur_graph_folder + video_id + "_" + vid + "_" + "_real_vs_watchtime.png"

				video_folder = video_data.GRAPHS_FOLDER + log_type + "/all/" + vid
				output_path_2 = video_folder + "/" + vid + "_" + "_real_vs_watchtime.png"
				plotGraph(title, cur_graph_folder, output_path_1, video_folder="", output_path_2="")

			total_videos += len(videos[log_type][video_list_id])
		
	
	if (to_save == "check_startup_delay"):
		fields = ["video_id", "startup_delay over QUIC (s)", "startup_delay over TCP (s)"]
		csvfilename = video_data.CSV_FOLDER + log_type + "/startup_delay.csv"
		
		x = []
		for i in range(0, len(startup_delay), 2):
			x.append([startup_delay[i][0].split("_")[0], startup_delay[i+1][1], startup_delay[i][1]])

		with open(csvfilename, 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			# writing the fields  
			csvwriter.writerow(fields)
			# writing the data rows  
			csvwriter.writerows(x)

	elif (to_save == "cdf_qoe"):
		font = { 'size'   : 13 }
		matplotlib.rc('font', **font)

		final_qoe_tcp = []
		final_qoe_quic = []
		for i in range(0, len(final_qoe), 2):
			final_qoe_quic += [final_qoe[i+1][1]]
			final_qoe_tcp += [final_qoe[i][1]]

		final_qoe_quic.sort()
		frequency_qoe_quic = Counter(final_qoe_quic)
		pdf_qoe_quic = []
		sum_frequency_qoe_quic = sum(frequency_qoe_quic.values())
		for i in frequency_qoe_quic.keys():
			pdf_qoe_quic.append(frequency_qoe_quic[i]/sum_frequency_qoe_quic)
		cdf_qoe_quic = np.cumsum(pdf_qoe_quic)

		final_qoe_tcp.sort()
		frequency_qoe_tcp = Counter(final_qoe_tcp)
		pdf_qoe_tcp = []
		sum_frequency_qoe_tcp = sum(frequency_qoe_tcp.values())
		for i in frequency_qoe_tcp.keys():
			pdf_qoe_tcp.append(frequency_qoe_tcp[i]/sum_frequency_qoe_tcp)
		cdf_qoe_tcp = np.cumsum(pdf_qoe_tcp)

		# plt.plot(list_qoe_quic, cdf_qoe_quic)

		print("Total videos:", count)

		x = np.linspace(0, max(final_qoe_quic[-1], final_qoe_tcp[-1]), 40)	
		plt.subplots(figsize=(16,9))
		# plt.figure()
		# print([0] + list(frequency_qoe_quic.keys()), "\n", [0] + list(cdf_qoe_quic))

		plt.plot([0] + list(frequency_qoe_quic.keys()), [0] + list(cdf_qoe_quic), "r-x", label="quic")
		plt.plot([0] + list(frequency_qoe_tcp.keys()), [0] + list(cdf_qoe_tcp), "b-o", label="tcp")
		
		title="CDF of QOE of Video ID (" + log_type + ")",
		xlabel="QOE (Mbps)",
		ylabel="CDF QOE(Mbps)",

		plt.legend(prop={ 'size': 7 }, loc = "upper left", bbox_to_anchor=(1.40, 1))
		plt.grid()
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.title(title)

		output_path_cdf_qoe = video_data.GRAPHS_FOLDER + log_type + "/cdf_qoe_graph_" + log_type + "_" + sys.argv[4] + ".png"
		plt.savefig(output_path_cdf_qoe, dpi=200)

	elif (to_save =="save_qoe"):
		font = { 'size'   : 13 }
		matplotlib.rc('font', **font)

		print("Total videos:", count)
		x = range(1, total_videos+1)
		y_quic = []
		y_tcp = []

		final_qoe_comparison = [0, 0, 0];

		for i in range(0, len(final_qoe), 2):

			if (int(final_qoe[i+1][1]) > int(final_qoe[i][1])):
				final_qoe_comparison[0] += 1
			elif (int(final_qoe[i+1][1]) == int(final_qoe[i][1])):
				final_qoe_comparison[1] += 1
			elif (int(final_qoe[i+1][1]) < int(final_qoe[i][1])):
				final_qoe_comparison[2] += 1

			y_tcp += [final_qoe[i][1]]
			y_quic += [final_qoe[i+1][1]]

		fields = ["vid_transportLayerProtocol", "qoe"]
		# csvfilename = video_data.CSV_FOLDER + log_type + "/qoe_data_" + sys.argv[1] + ".csv"
		csvfilename = video_data.CSV_FOLDER + log_type + "/qoe_data_" + sys.argv[1] + ".csv"
		
		with open(csvfilename, 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			# writing the fields  
			csvwriter.writerow(fields)
			# writing the data rows  
			csvwriter.writerows(final_qoe)

		print("Total Complete Videos", len(final_qoe)//2)

		print("QOE of:")
		print("1. DASH/QUIC is greater than DASH/TCP in :", final_qoe_comparison[0], "videos")
		print("2. DASH/QUIC is equal to DASH/TCP in :", final_qoe_comparison[1], "videos")
		print("3. DASH/QUIC is less than DASH/TCP in :", final_qoe_comparison[2], "videos")
		output_path_qoe = video_data.GRAPHS_FOLDER + log_type + "/qoe_graph_" + log_type + "_" + sys.argv[4] + ".png"

		plotMetricGraph(
			x,
			y_quic,
			y_tcp,
			title="QOE vs Video ID (" + log_type + ")",
			ylabel="QOE(kbps)",
			output_path=output_path_qoe
		)

	elif (to_save == "create_csv"):
		print("Total videos:", count)

		metrics_comparison_stats = {
			# quic greater, quic equal to, quic less than
			"qoe": [0, 0, 0],
			"average_bitrate": [0, 0, 0],
			"average_bitrate_variation": [0, 0, 0],
			"stall": [0, 0, 0]
		}

		x = range(1, total_videos+1)

		font = { 'size'   : 11 }
		matplotlib.rc('font', **font)


		fields = ["vid_transportLayerProtocol", "averageBitrate (kbps)", "averageBitrateVariations (#)", "averageStall (s)"]
		csvfilename = video_data.CSV_FOLDER + log_type + "/metrics_data_" + sys.argv[1] + ".csv"

		with open(csvfilename, 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			# writing the fields  
			csvwriter.writerow(fields)
			# writing the data rows  
			csvwriter.writerows(metrics)
	
		for i in range(0, len(metrics), 2):
			# metrics[i+1] is for quic data
			# average bitrate graph
			# print("AB: Q:", int(metrics[i+1][1]), " T:",  int(metrics[i][1]))
			if (int(metrics[i+1][1]) > int(metrics[i][1])):
				metrics_comparison_stats["average_bitrate"][0] += 1
			elif (int(metrics[i+1][1]) == int(metrics[i][1])):
				metrics_comparison_stats["average_bitrate"][1] += 1
			elif (int(metrics[i+1][1]) < int(metrics[i][1])):
				metrics_comparison_stats["average_bitrate"][2] += 1

			# print("ABV: Q:", int(metrics[i+1][2]), " T:",  int(metrics[i][2]))
			if (int(metrics[i+1][2]) > int(metrics[i][2])):
				metrics_comparison_stats["average_bitrate_variation"][0] += 1
			elif (int(metrics[i+1][2]) == int(metrics[i][2])):
				metrics_comparison_stats["average_bitrate_variation"][1] += 1
			elif (int(metrics[i+1][2]) < int(metrics[i][2])):
				metrics_comparison_stats["average_bitrate_variation"][2] += 1

			# print("S: Q:", int(metrics[i+1][3]), " T:",  int(metrics[i][3]))
			if (int(metrics[i+1][3]) > int(metrics[i][3])):
				metrics_comparison_stats["stall"][0] += 1
			elif (int(metrics[i+1][3]) == int(metrics[i][3])):
				metrics_comparison_stats["stall"][1] += 1
			elif (int(metrics[i+1][3]) < int(metrics[i][3])):
				metrics_comparison_stats["stall"][2] += 1

			y_ab_tcp += [metrics[i][1]]
			y_ab_quic += [metrics[i+1][1]]
			
			# average bitrate variation graph
			y_abv_tcp += [metrics[i][2]]
			y_abv_quic += [metrics[i+1][2]]
			
			# average stall graph
			y_s_tcp += [metrics[i][3]]
			y_s_quic += [metrics[i+1][3]]

		print("Total Complete Videos", len(metrics)//2)

		print("Average Bitrate of:")
		print("1. DASH/QUIC is greater than DASH/TCP in :", metrics_comparison_stats["average_bitrate"][0], "videos")
		print("2. DASH/QUIC is equal to DASH/TCP in :", metrics_comparison_stats["average_bitrate"][1], "videos")
		print("3. DASH/QUIC is less than DASH/TCP in :", metrics_comparison_stats["average_bitrate"][2], "videos")
		
		print("Average Bitrate Variation of:")
		print("1. DASH/QUIC is greater than DASH/TCP in :", metrics_comparison_stats["average_bitrate_variation"][0], "videos")
		print("2. DASH/QUIC is equal to DASH/TCP in :", metrics_comparison_stats["average_bitrate_variation"][1], "videos")
		print("3. DASH/QUIC is less than DASH/TCP in :", metrics_comparison_stats["average_bitrate_variation"][2], "videos")

		print("Average Stall (Rebuffering) of:")
		print("1. DASH/QUIC is greater than DASH/TCP in :", metrics_comparison_stats["stall"][0], "videos")
		print("2. DASH/QUIC is equal to DASH/TCP in :", metrics_comparison_stats["stall"][1], "videos")
		print("3. DASH/QUIC is less than DASH/TCP in :", metrics_comparison_stats["stall"][2], "videos")

		plotMetricGraph(x, 
						y_ab_quic, 
						y_ab_tcp,
						title="Average Bitrate (kbps) vs Video ID (" + log_type + ")",
						ylabel="Average Bitrate(kbps)",
						output_path=video_data.CSV_FOLDER + log_type + "/average_bitrate_metric.png")

		plotMetricGraph(x, 
						y_abv_quic, 
						y_abv_tcp,
						title="Average Bitrate Variations (kbps) vs Video ID (" + log_type + ")",
						ylabel="Average Bitrate Variations(kbps)",
						output_path=video_data.CSV_FOLDER + log_type + "/average_bitrate_variations_metric.png")

		plotMetricGraph(x, 
						y_s_quic, 
						y_s_tcp,
						title="Average Stall (s) vs Video ID (" + log_type + ")",
						ylabel="Average Stall(s)",
						output_path=video_data.CSV_FOLDER + log_type + "/average_stall_metric.png")

	elif (to_save == "save_packet_count"):
		fields = ["video_id", "packet_count_ratio", "packet_bytes_ratio"]
		csvfilename = video_data.CSV_FOLDER + log_type + "/pacekt_count.csv"
		
		x = []
		for i in range(0, len(packet_counts), 2):
			packet_count_ratio = packet_counts[i][1] / packet_counts[i+1][1] # tcp / quic
			packet_bytes_ratio = packet_counts[i][2] / packet_counts[i+1][2] # tcp / quic
			x.append([packet_counts[i][0], packet_count_ratio, packet_bytes_ratio])

		with open(csvfilename, 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			# writing the fields  
			csvwriter.writerow(fields)
			# writing the data rows  
			csvwriter.writerows(x)