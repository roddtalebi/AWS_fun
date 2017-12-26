# Given a bucket and a date range, this program should download, unzip, and save all the respective
#  log files to a folder named 'data' or to another specified name

# read in formate:
# $ python s3_to_log.py bucket=com.mixafter.dev.logs prefix=cloudfront-video 2015-10-02 2015-11-02 folder=data


#_________________________________________________________________________________________
# first read in the values to prep for download stage

from sys import argv
from string import find
import time
import os
import shutil
import re
from os import listdir


# set defaults:
dates = "0"

ori_last_day = str(time.strftime("%Y-%m-%d"))

month = str(int(time.strftime("%m"))-1).zfill(2)
if month == '00':
	month='12'
first_day = str(time.strftime("%Y-"))+month+str(time.strftime("-%d"))

myBucket = 'com.mixafter.prod.logs'

prefix = 'cloudfront-video'

folder = 's3_pull'

# extract values
for input in range (0, len(argv)):
	
	# get the buckets
	# bucket name shouldn't have '-' in it
	check = find(argv[input], 'bucket=')
	if check != -1:
		myBucket = argv[input][7:]
	
	check = find(argv[input], 'prefix=')
	if check != -1:
		prefix = argv[input][7:]
	else: #prefix may have '-' so we want to make sure we don't load prefix into dates
		check2 = find(argv[input], '-')
		if check2 != -1:
			if dates == "0":
				dates = []
			dates.append(argv[input])
			# sort the dates later
	
	# find folder name
	check = find(argv[input], 'folder=')
	if check != -1:
		folder = argv[input][7:]

# now sort the dates to get first + last
if dates != "0": #not using default dates
	if len(dates)==2: #2 days given
		dates.sort()
		first_day = dates[0]
		ori_last_day = dates[1]
	else: #only 1 day given
		first_day = dates[0]
		ori_last_day = dates[0]

#but now I have to add a day to the last day just in case there was an overflow of logs
year = int(ori_last_day[:4])
month = int(ori_last_day[5:7])
day = int(ori_last_day[8:])

if day == 31:
	if month==1 or month==3 or month==5 or month==7 or month==8 or month==10:
		new_month = str(month + 1).zfill(2)
		new_day = '01'
		last_day = str(year) +'-'+ new_month +'-'+ new_day
	elif month==12:
		new_month = '01'
		new_day = '01'
		new_year = str(year + 1).zfill(2)
		last_day = new_year +'-'+ new_month +'-'+ new_day
	else:
		new_day = str(day+1).zfill(2)
		last_day = ori_last_day[:8] + new_day
elif day == 30:
	if month==4 or month==6 or month==9 or month==11:
		new_month = str(month + 1).zfill(2)
		new_day = '01'
		last_day = str(year) +'-'+ new_month +'-'+ new_day
	else:
		new_day = str(day+1).zfill(2)
		last_day = ori_last_day[:8] + new_day
elif day == 28:
	if month==2:
		new_month = '03'
		new_day = '01'
		last_day = str(year) +'-'+ new_month +'-'+ new_day
	else:
		new_day = str(day+1).zfill(2)
		last_day = ori_last_day[:8] + new_day
else:
	new_day = str(day+1).zfill(2)
	last_day = ori_last_day[:8] + new_day
# now there is an ori_last_day for the real last day, and last_day for the safety barrier



# create folder if it doesn't exist
directory = '../data/'+folder
if os.path.exists(directory): #directory already exist so delete it
	shutil.rmtree(directory)
os.makedirs(directory) #now make new directory


content1 = myBucket +'\n'+ prefix +'\n'+ first_day +'\n'+ ori_last_day +'\n'+ last_day +'\n'

# display meta data to the user for correctness
print '\n'
print content1
print "Save to", directory
print '\n'



#_________________________________________________________________________________________
# now let's start the download stage!

import boto3

s3 = boto3.resource('s3') # point to s3 aws service
bucket = s3.Bucket(myBucket) # open up the right bucket

# create a temporary folder for storing the .gz files
temp = 'dontnameanotherfilethisname'
temp_directory = '../data/' + temp
if os.path.exists(temp_directory): #directory already exist so delete it
	shutil.rmtree(temp_directory)
os.makedirs(temp_directory) #now make new directory


keyList = []
content2 = [] #for writing file names to .txt file
for item in bucket.objects.all():
	item = str(item.key)
	if prefix in item: #it's of the right folder
		
		# THIS PART NEEDS TO BE FASTER FOR WHEN WE DOWNLOAD MORE LOGS!
		
		name = str([(item[m.start():]) for m in re.finditer(r'/',item)][-1]) #only keep the file name and remove directory junk
	
		day1 = re.findall(r'[0-9]{4}'+'-'+r'[0-9]{2}'+'-'+r'[0-9]{2}',name) #year-month-day
		day2 = re.findall(r'_[0-9]{8}',name) #yearmonthday
		if day1 != []: #then it found a file name with the day
			day = day1[0]
		elif day2 != []:
			day = str(day2[0][1:5]) +'-'+ str(day2[0][5:7]) +'-'+ str(day2[0][7:])
		else:
			day="0"
	
		if first_day <= day <= last_day: #check if that day falls in our range
			file_name = temp_directory + name
			bucket.download_file(item, file_name)
			content2.append(name[1:]) #add file name except for leading /

print "Download Done\n"



#_________________________________________________________________________________________
# create a .txt file to save all the meta data to (just for reference)

# save and print the pull requested data
text_file = "meta_s3pull.txt"
meta = "Bucket\nPrefix\nFirst Day\nLastDay\nLast Day with Buffer\nFile Names\n############\n"

file = open(directory +'/'+ text_file, 'w')
file.write(meta + content1)
for name in content2:
  file.write("%s\n" % name)
file.close()

print "Meta File Written\n"

#_________________________________________________________________________________________
# concatenate the .gz files to one

mergedFile = 'merged_file.gz'

with open(temp_directory +'/'+ mergedFile, 'wb') as destFile:
	for name in listdir(temp_directory):
		if name == mergedFile:
			continue
		with open(temp_directory +'/'+ name, 'rb') as sourceFile:
			shutil.copyfileobj(sourceFile, destFile)

print "Merge Done\n"

 



#_________________________________________________________________________________________
# now the unzipping stage

import gzip

# for unzipping multiple files:
#for name in listdir(temp_directory):
#	log_file = directory +'/'+ name[:-3] + '.log'
#	gz_file = temp_directory +'/'+ name
#	
#	inF = gzip.open(gz_file, 'rb')
#	outF = open(log_file, 'wb')
#	outF.write( inF.read() )
#	inF.close()
#	outF.close()


# for unzipping the single merged file:
gz_file = temp_directory + '/' + mergedFile
log_file = directory + '/' + mergedFile[:-3] + '.log'

inF = gzip.open(gz_file, 'rb')
outF = open(log_file, 'wb')
print "opened"
outF.write( inF.read() )
print "written"
inF.close()
outF.close()


# now delete the temporary file
shutil.rmtree(temp_directory)

print "Unzip Done\n"















	