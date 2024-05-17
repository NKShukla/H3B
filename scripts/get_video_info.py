import urllib
import urllib.parse
import urllib.request
from urllib.parse import urlparse
import sys
import json
import requests
from video_data import videos_list, LOGS_FOLDER, VIDEO_INFO_JSON_FILE

itagpriority = [397, 315, 313, 308, 266, 271, 299, 264, 303, 137, 298, 248, 138, 302, 136, 247, 135, 244, 134, 243, 133, 242, 140, 160, 251, 278, 171, 250, 249]
labels = {171: ["0p", "na", "0", "audio/webm"], 133: ["240p", "426x240", "24", "video/mp4"], 134: ["360p", "640x360", "24", "video/mp4"], \
          135: ["480s", "854x428", "30", "video/mp4"], 264: ["1080p", "1920x1200", "30", "video/mp4"], 137: ["1080s", "1920x960", "30", "video/mp4"], \
          266: ["2160s", "3840x1920", "30", "video/mp4"], 140: ["0p", "na", "0", "audio/mp4"], 271: ["1080p", "1920x1200", "30", "video/webm"], \
          278: ["144p", "256x144", "24", "video/webm"], 160: ["144p", "256x144", "24", "video/mp4"], 298: ["720s60", "1280x640", "60", "video/mp4"], \
          299: ["1080s60", "1920x960", "60", "video/mp4"], 302: ["720s60", "1280x640", "60", "video/webm"], 303: ["1080s60", "1920x960", "60", "video/webm"], \
          136: ["720p", "1280x720", "24", "video/mp4"], 308: ["1440s60", "2560x1280", "60", "video/webm"], 313: ["2160s", "3840x1920", "30", "video/webm"], \
          315: ["2160s60", "3840x1920", "60", "video/webm"], 138: ["1080p", "1920x1200", "30", "video/mp4"], 242: ["240p", "426x240", "24", "video/webm"], \
          243: ["360p", "640x360", "24", "video/webm"], 244: ["480s", "854x428", "30", "video/webm"], 247: ["720p", "1280x720", "24", "video/webm"], \
          248: ["1080s", "1920x960", "30", "video/webm"], 249: ["0p", "na", "0", "audio/webm"], 250: ["0p", "na", "0", "audio/webm"], \
          251: ["0p", "na", "0", "audio/webm"], 397: ["480p", "852×480", "30", "video/webm"]}

def getFormat(string):
    if string == None:
        return
    g = []
    streams = urlparse(string)[2].split(",")
    for p in streams:
        h = {}
        x = p.split("&")
        for y in x:
            y = y.split("=")
            if len(y) == 1:
                h[y[0]] = False
            else:
                h[y[0]] = urllib.parse.unquote(y[1])
        h["raw"] = p
        g.append(h)
    return g

def getData(youtubeId = "i_XE_3jMudA"):
    url = "https://www.youtube.com/get_video_info?video_id=%s&el=embedded&ps=default&eurl=&gl=US&hl=en&html5=1&c=TVHTML5&cver=6.20180913"%(youtubeId)
#     print url
    fp = urllib.request.urlopen(url)
    data = fp.read().decode("utf-8")
    fp.close()

    # print(type(data))
    arr = data.split("&")
    output = {}
    for a in arr:
        x = a.split("=")
        dt = urlparse(x[1])
        output[x[0]] = urllib.parse.unquote(x[1])
    if "status" not in output or output["status"] == "fail":
        print("Problem")
        exit(2)
    streams = output.get('url_encoded_fmt_stream_map', None)
    if streams != None:
        output['url_encoded_fmt_stream_map'] = getFormat(streams)

    streams = output.get('adaptive_fmts', None)
    if streams != None:
        output['adaptive_fmts'] = getFormat(streams)

    output['player_response'] = json.loads(output['player_response'])

    return output



if __name__ == "__main__":

    urls = []

    if sys.argv[1] == "video":
        urls = [sys.argv[2]]

    elif sys.argv[1] == "video-list":
        videos_list_folder = sys.argv[1]+"-"+sys.argv[2]
        urls = videos_list[videos_list_folder]

    elif sys.argv[1] in ["morning", "evening", "afternoon"]:
        videos_list_folder = sys.argv[1]
        urls = videos_list["video-list-8"]

    info={}
    count = 0
    for url in urls:
        x=json.dumps(getData(url),indent=2)
        if "streamingData" in x:
            count += 1
            print(url)
            info[url] = dict()
            y=json.loads(x)
            for obj in y["player_response"]["streamingData"]["formats"]:
                if "video" in obj["mimeType"]:
                    info[url][obj["itag"]]=dict()
                    info[url][obj["itag"]]["bitrate"] = obj["bitrate"]
                    info[url][obj["itag"]]["qualityLabel"] = obj["qualityLabel"]

            for obj in y["player_response"]["streamingData"]["adaptiveFormats"]:
                if "video" in obj["mimeType"] and obj["itag"] not in info:
                    info[url][obj["itag"]]=dict()
                    info[url][obj["itag"]]["bitrate"] = obj["bitrate"]
                    info[url][obj["itag"]]["qualityLabel"] = obj["qualityLabel"]
            
            print(json.dumps(info, indent=2))
        else:
            print("No video info for:", url)

    print("Total videos in the list: %d:", len(urls))
    print("Total videos in the video info file: %d:", count)

    if sys.argv[1] in ["video-list", "morning", "evening", "afternoon"]:
        output_file_name = LOGS_FOLDER + videos_list_folder + "/" + VIDEO_INFO_JSON_FILE
        with open(output_file_name, "w") as outfile:
            json.dump(info,outfile)