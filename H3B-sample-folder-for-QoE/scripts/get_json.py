import os, csv, sys, json
from video_data import updateFolderLocations
import sys
import collections
import video_data

def getVideoTags(input_string, req_id, tag, output):
	itag_idx = input_string.find("itag=")
	and_idx_1 = input_string.find("&", itag_idx)
	itag = int(input_string[itag_idx+5:and_idx_1])

	clen_idx = input_string.find("clen=")
	and_idx_4 = input_string.find("&", clen_idx)
	clen = int(input_string[clen_idx+5:and_idx_4])

	dur_idx = input_string.find("dur=")
	and_idx_4 = input_string.find("&", dur_idx)
	dur = float(input_string[dur_idx+4:and_idx_4])

	rn_idx = input_string.find("rn=")
	and_idx_3 = input_string.find("&", rn_idx)
	# print(input_string[rn_idx+3:and_idx_3])
	rn = 0
	rn = int(input_string[rn_idx+3:and_idx_3])

	range_idx = input_string.find("range=")
	if (range_idx == -1):
		print("Aha!")
		return
	and_idx_2 = input_string.find("&", range_idx)
	# print(input_string[range_idx+6:and_idx_2])
	ranges = list(map(int, input_string[range_idx+6:and_idx_2].split("-")))

	rbuf_idx = input_string.find("rbuf=")
	and_idx_2 = input_string.find("&", rbuf_idx)
	# print(input_string[rbuf_idx:])
	if (and_idx_2 == -1):
		rbuf = int(input_string[rbuf_idx+5:])
	else:
		rbuf = int(input_string[rbuf_idx+5:and_idx_2])

	output[req_id]["total_bytes"] = ranges[1] - ranges[0]
	output[req_id][tag+"_range"] = ranges
	output[req_id][tag+"_itag"] = itag
	output[req_id][tag+"_rbuf_sec"] = rbuf/clen * dur
	output[req_id][tag+"_rbuf"] = rbuf
	output[req_id][tag+"_rn"] = rn;
	output[req_id][tag+"_clen"] = clen;
	output[req_id][tag+"_dur"] = dur;


def getVideoTimes(input_string, req_id, output):
	st_idx = input_string.find("st=")
	
	percent_idx_1 = input_string.find("%", st_idx)
	if (percent_idx_1 == -1):
		and_idx_1 = input_string.find("&", st_idx)
		st = float(input_string[st_idx+3:and_idx_1])
	else:
		st = float(input_string[st_idx+3:percent_idx_1])

	et_idx = input_string.find("et=")
	percent_idx_2 = input_string.find("%", et_idx)
	if (percent_idx_2 == -1):
		and_idx_2 = input_string.find("&", et_idx)
		et = float(input_string[et_idx+3:and_idx_2])
	else:
		et = float(input_string[et_idx+3:percent_idx_2])

	rt_idx = input_string.find("rt=")
	and_idx_3 = input_string.find("&", rt_idx)
	rt = float(input_string[rt_idx+3:and_idx_3])
	
	fmt_idx = input_string.find("fmt=")
	and_idx_3 = input_string.find("&", fmt_idx)
	fmt = int(input_string[fmt_idx+4:and_idx_3])

	output[req_id]["st"] = st
	output[req_id]["et"] = et
	output[req_id]["rt"] = rt
	output[req_id]["fmt"] = fmt


def getStreamingStats(input_string, req_id, output):
	# print(req_id, "getStreamingStats")

	fmt_idx = input_string.find("fmt=")
	if (fmt_idx != -1):
		end_idx = input_string.find("&", fmt_idx)
		fmt = int(input_string[fmt_idx+4:end_idx])
		output[req_id]["itag"] = fmt

	bh_idx = input_string.find("bh=")
	if (bh_idx != -1):
		end_idx = input_string.find("&", bh_idx)
		if (end_idx == -1):
			end_idx = input_string.find("\"}", bh_idx)
		bh = input_string[bh_idx+3:end_idx]
		output[req_id]["buffer_health"] = bh

	cmt_idx = input_string.find("cmt=")
	if (cmt_idx != -1):
		end_idx = input_string.find("&", cmt_idx)
		cmt = input_string[cmt_idx+4:end_idx]
		output[req_id]["cmt"] = cmt

	bwm_idx = input_string.find("bwm=")
	if (bwm_idx != -1):
		end_idx = input_string.find("&", bwm_idx)
		bwm = input_string[bwm_idx+4:end_idx]
		output[req_id]["bwm"] = bwm

	bwe_idx = input_string.find("bwe=")
	if (bwe_idx != -1):
		end_idx = input_string.find("&", bwe_idx)
		bwe = input_string[bwe_idx+4:end_idx]
		output[req_id]["bwe"] = bwe

	vps_idx = input_string.find("vps=")
	if (vps_idx != -1):
		end_idx = input_string.find("&", vps_idx)
		vps = input_string[vps_idx+4:end_idx]
		output[req_id]["vps"] = vps


def printRequestId(req_id):
	print("********")
	print("Request ID:", req_id)
	print("time taken by request:", output[req_id]["total_time"])
	print("bytes/request:", output[req_id]["total_bytes"])
	
	print("\nOn Request Details: ")
	print("timestamp:", output[req_id]["request_ts"])
	print("itag:", output[req_id]["request_itag"])
	print("range:", output[req_id]["request_range"])
	print("rbuf:", output[req_id]["request_rbuf"])


def create_json(file_name, log_type, connType):
	output = {}
	# print("\nCreating JSON of file: ", file_name)
	log_file = open(file_name, "r", encoding="utf8")
	line = log_file.readline()

	allowed_requests = [
		"\"ABHIJIT_ON_RESPONSE_STARTED", 
		"\"ON_RESPONSE_STARTED", 
		"\"RESPONSE_STARTED", 
		"RESPONSE_STARTED", 
		"ON_SEND_HEADERS", 
		"SEND_HEADERS", 
		"\"SEND_HEADERS", 
		"\"ABHIJIT_ON_SEND_HEADERS", 
		"\"ON_SEND_HEADERS", 
		"\"ABHIJIT_ON_COMPLETE", 
		"\"ON_COMPLETE", 
		"\"COMPLETE", 
		"COMPLETE"
	]
	extra_allowed_requests = [
		"\"ABHIJIT_ON_RESPONSE_STARTED", 
		"\"ON_RESPONSE_STARTED", 
		"\"RESPONSE_STARTED", 
		"RESPONSE_STARTED", 
		"ON_SEND_HEADERS", 
		"SEND_HEADERS", 
		"\"SEND_HEADERS", 
		"\"ABHIJIT_ON_SEND_HEADERS", 
		"\"ON_SEND_HEADERS", 
		"\"ABHIJIT_ON_COMPLETE", 
		"\"ON_COMPLETE", 
		"\"COMPLETE", 
		"COMPLETE"
		"ON_RESPONSE_STARTED", 
		"ON_COMPLETE", 
		"COMPLETE", 
		"\"ABHIJIT_ON_RESPONSE_STARTED", 
		"\"ABHIJIT_ON_COMPLETE", 
		"\"ON_RESPONSE_STARTED", 
		"\"ON_COMPLETE", 
		"\"RESPONSE_STARTED", 
		"\"COMPLETE", 
		]

	start_time = -1

	while (line != ""):
		tmp = line.find(" ")
		space_idx_1 = line.find(" ", tmp+1);
		request_tag = line[tmp+1:space_idx_1]

		if (request_tag not in extra_allowed_requests):
			line = log_file.readline()
			continue

		space_idx_2 = line.find(" ", space_idx_1+1)
		timestamp = line[space_idx_1+1:space_idx_2]
		if (start_time == -1):
			start_time = float(timestamp)
		end_of_json = line.find("\", source")
		# print(line[space_idx_2+1:end_of_json] + "\n")
		tags = json.loads(line[space_idx_2+1:end_of_json])
		# Checkpoint 1
		# print()
		# print(line)

		# if request is for videoplayback
		req_id = int(tags["requestId"])

		if (tags["url"].find("mime=video") != -1 and tags["url"].find("range=") != -1):
			if (request_tag in allowed_requests):
				if (req_id in output.keys()):
					print(request_tag, req_id)
					if ("COMPLETE" in request_tag):
						if ({"name":"client-protocol","value":"quic"} in tags["responseHeaders"]):
							output[req_id]["quic_protocol"] = True
						else:
							output[req_id]["quic_protocol"] = False
					else:
						output[req_id]["complete_ts"] = (float(tags["timeStamp"]) - start_time) / 1000
						output[req_id]["total_time"] = float(output[req_id]["complete_ts"] - output[req_id]["request_ts"])
						getVideoTags(tags["url"], req_id, "complete", output)
						output[req_id]["kbytes/second"] = (output[req_id]["total_bytes"]/output[req_id]["total_time"])  * 1000 / 1024;
					
				else:
					print(request_tag, req_id)
					output[req_id] = dict()
					output[req_id]["type"] = "videoplayback"
					output[req_id]["request_ts"] = (float(tags["timeStamp"]) - start_time) / 1000

		# if request is for watchtime
		# elif (tags["url"].find("watchtime?") != -1):
		# 	if (req_id not in output.keys()):
		# 		output[req_id] = dict()
		# 		output[req_id]["type"] = "watchtime"
		# 		output[req_id]["request_ts"] = (float(tags["timeStamp"]) - start_time) / 1000
		# 		getVideoTimes(tags["url"], req_id, output)

		# if request is for streamingstats
		elif (tags["url"].find("streamingstats") != -1):
			if (req_id not in output.keys() and (request_tag in ["\"RESPONSE_STARTED", "\"ABHIJIT_ON_RESPONSE_STARTED", "\"ON_RESPONSE_STARTED" ])):
				output[req_id] = dict()
				output[req_id]["type"] = "streamingstats"
				output[req_id]["request_ts"] = (float(tags["timeStamp"]) - start_time) / 1000
				getStreamingStats(tags["url"], req_id, output)


		line = log_file.readline()

	#########################################################################################
	output = collections.OrderedDict(sorted(output.items()))
	json_obj = json.dumps(output, indent=4)

	if (not os.path.isdir(video_data.JSON_FOLDER)):
		os.mkdir(video_data.JSON_FOLDER)

	if (not os.path.isdir(video_data.JSON_FOLDER + "/" + log_type)):
		os.mkdir(video_data.JSON_FOLDER + "/" + log_type)

	if (not os.path.isdir(video_data.JSON_FOLDER + "/" + log_type + "/" + connType)):
		os.mkdir(video_data.JSON_FOLDER + "/" + log_type + "/" + connType)

	file_name = file_name.replace("logFiles", "jsonFiles")
	output_file_name = file_name.split(".log")[0] + ".json"
	with open(output_file_name, "w") as outfile:
		outfile.write(json_obj)


def checkCompleteVideos():
	LOGS_FOLDER = "data/logFiles/"
	LOG_TYPES = ['128-1152-256-dec', 'sudden-6']	
	video_types = ['morning', 'afternoon', 'evening']


def getFilename(video_list_folder, log_type, connType):
	if (video_list_folder == "slot"):
		pass
	elif (video_list_folder in ["morning", "afternoon", "evening"]):
		if (log_type == "dynamic-high"):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type + "_" + connType + "_highbw.log"
		elif ("dynamic-high-v" in log_type):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type[:-3] + "_" + connType + ".log"
		elif (log_type == "dynamic-low"):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type + "_" + connType + "_lowbw.log"
		elif ("dynamic-low-mr" in log_type):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + "dynamic-low" + "_" + connType + "_lowbw.log"
		elif (log_type == "dynamic-low-gs"):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type[:-3] + "_" + connType + "_lowbw-gs.log"
		elif (log_type == "dynamic-low-nys"):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type[:-4] + "_" + connType + "_lowbw-nys.log"
		elif (log_type == "dynamic-low-ss"):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type[:-3] + "_" + connType + "_lowbw-ss.log"
		elif ("dynamic-low-v" in log_type):
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type[:-3] + "_" + connType + "_lowbw.log"
		else:
			filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type + "_" + connType + "_" + video_list_folder + ".log"
	else:
		filename = video_data.LOGS_FOLDER + log_type + "/" + connType + "/chrome_debug_" + vid + "_" + log_type + "_" + connType + ".log"

	return filename


if __name__ == '__main__':

	if (sys.argv[1] == "video"):
		create_json(sys.argv[2])
	
	elif sys.argv[1] == "video-list":
		log_type = sys.argv[3]
		video_list_folder = sys.argv[1] + '-' + sys.argv[2];

	elif sys.argv[1] in ["no-slot", "slot"]:
		log_type = sys.argv[2]
		video_list_folder = sys.argv[1]

	updateFolderLocations(video_list_folder, log_type)

	connType = [ "quic", "tcp" ]

	for conn in connType:
		folder = video_data.LOGS_FOLDER + log_type + "/" + conn +"/"
		directory = os.fsencode(folder)
		for file in os.listdir(directory):
			file = file.decode("utf-8") 
			print(folder + file)
			create_json(folder + file, log_type, conn)