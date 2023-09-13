#Arthur Hakobyan
#13 May 2023
#Project 3 The Crucible
#Chaja

import pymongo 
import pandas as pd
import argparse
import subprocess
import math
from datetime import timedelta
import xlsxwriter
import os


#1. #2 Argparse and Video arguments with python main.py -f twitch_nft_demo.mp4 -v

# MongoClient
client = pymongo.MongoClient("mongodb://localhost:27017/")



parser = argparse.ArgumentParser()
parser.add_argument('-f', '--files', dest='work_files', help='Baselight/Flames Text files') 
parser.add_argument('-v', '--verbose', action='store_true', help='Console')

arg_parse = parser.parse_args()
input_file = arg_parse.work_files

#3. Using ffmpeg or 3rd party tool of your choice, to extract timecode from video and write your own timecode method to convert marks to timecode

if arg_parse.work_files:
    #Get totalframes
    ffmpegcommand = ["ffprobe", "-v", "0" ,"-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", input_file]
    runffmpeg = subprocess.run(ffmpegcommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    frames = int(runffmpeg.stdout.decode("utf-8").strip().replace("/1", ""))
print(frames)

gettime = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", input_file]
gettime_h = subprocess.run(gettime, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
totalframe = int(gettime_h.stdout.decode("utf-8").strip())
h = int(totalframe / ((frames*60)*60)) 
m = int(totalframe / (frames*60)) % 60 
s = int((totalframe % (frames*60))/frames) 
f = totalframe % (frames*60) % frames
totaltimecode = ( "%02d:%02d:%02d:%02d" % ( h, m, s, f))

print(totaltimecode)


#4. From (2) Call the populated database from proj2, find all ranges only that fall in the length of video from (1)


# Parse the command-line arguments
args = parser.parse_args()

# Databases
project_db = client["Project_2"]
works_col = project_db["works"]
frames_col = project_db["data"]

x = frames_col.find({}, {"Location": 1})

location_ranges = []
for line in x:
    for location_frame in line["Location"]:
        ranges = []
        if "-" in location_frame:  # Check if the range is present
            location, frame_range = location_frame.split(" ", 1)
            start_frame, end_frame = frame_range.split("-")
            ranges.extend([location, start_frame, end_frame])
        if ranges:
            location_ranges.append(ranges)


filteredframes = []
new_list = []
avg_frames = []

#print(location_ranges)



counter = 0
while counter < len(location_ranges):
    h = int(int(location_ranges[counter][1]) / ((frames*60)*60)) 
    m = int(int(location_ranges[counter][1]) / (frames*60)) % 60 
    s = int((int(location_ranges[counter][1]) % (frames*60))/frames) 
    f = int(location_ranges[counter][1]) % (frames*60) % frames
    timecode = ( "%02d:%02d:%02d:%02d" % ( h, m, s, f))
    
    if(timecode < totaltimecode):
        h = int(int(location_ranges[counter][2]) / ((frames*60)*60)) 
        m = int(int(location_ranges[counter][2]) / (frames*60)) % 60 
        s = int((int(location_ranges[counter][2]) % (frames*60))/frames) 
        f = int(location_ranges[counter][2]) % (frames*60) % frames
        timecodevar = ( "%02d:%02d:%02d:%02d" % ( h, m, s, f))
        if(timecodevar < totaltimecode):
            filteredframes.append(location_ranges[counter])
            new_list.append("%s-%s"%(timecode, timecodevar))
            mathvar = math.ceil((int(location_ranges[counter][2])+int(location_ranges[counter][1]))/2)
            #avg_frames.append(math.ceil((int(location_ranges[counter][2])+int(location_ranges[counter][1]))/2))
            delta = timedelta(seconds=(mathvar / frames))
            avg_frames.append(str(delta))
            
    counter += 1
#5. 5. New argparse output parameter for XLS with flag from (2) should export same CSV export, but in XLS with new column from files found from (3) and export their timecode ranges as well

"""
countingframe = 0
while countingframe < len(avg_frames):
        commandpicture = ["ffmpeg", "-i", input_file, "-ss", avg_frames[countingframe], "-vf", "scale=96:74", "-frames:v","1","-q:v","2","%s.jpg"%(countingframe)] 
        countingframe+=1
        subprocess.run(commandpicture)
"""


workbook = xlsxwriter.Workbook('project3.xlsx')
worksheet = workbook.add_worksheet()
row = 0 
col = 0

#6. #6. Create Thumbnail (96x74) from each entry in (2), but middle most frame or closest to. Add to XLS file to it's corresponding range in new column
"""
excelcounting = 0
while excelcounting < len(filteredframes):
        worksheet.write(row, col, filteredframes[excelcounting][0])
        worksheet.write(row, col + 1, "%s-%s"%(filteredframes[excelcounting][1], filteredframes[excelcounting][2]))
        worksheet.write(row, col + 2, new_list[excelcounting])
        worksheet.insert_image(row, col + 3, "%s.jpg"%(excelcounting))
        row += 1
        excelcounting += 1
workbook.close()
"""


from frameioclient import FrameioClient

# Initialize Frame.io client
client = FrameioClient("fio-u-sEqg08xog0JOOkZWfaGpXFiQH4oVgUqyvnd4lvMCYdmJtxoGzF66mBQY7tDzSefH")
parent_asset_id = 'a50d31b9-fe06-4e4b-970a-9f58fe8646c9'
directory = './'

# Iterate through the JPEG files 
for filename in os.listdir(directory):
    if filename.endswith(".jpg"):
        file_path = os.path.join(directory, filename)
        filesize = os.path.getsize(file_path)
        
        # Create the asset on Frame.io
        asset = client.assets.create(
            parent_asset_id=parent_asset_id,
            name=filename,
            type="file",
            filetype="image/jpeg",
            filesize=filesize
        )
        # Upload asset
        client.assets.upload(asset["parent_id"], file_path)

