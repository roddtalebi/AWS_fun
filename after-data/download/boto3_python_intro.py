
# stole knowledge from here:
# https://boto3.readthedocs.io/en/latest/guide/quickstart.html#using-boto-3


import boto3
import botocore

myBucket = 'com.mixafter.dev.logs'
# NOTE: that I can later make this a more customizeable variable by asking the user which bucket they want to look at


#__________________________
# INTRO
# I'm gonna try two methods: boto3.resource and boto3.client to show how to get the files in a bucket

#_________________________
# First let's use boto3.resource

# Let's use Amazon S3
s3 = boto3.resource('s3')

# Print out all bucket names
for bucket in s3.buckets.all():
    print(bucket.name)
# cool


# let's see what happens when we try to open one bucket
bucket = s3.Bucket(myBucket)

for item in bucket.objects.all():
    print(item.key) #will print the .gz file name
    print(item.bucket_name) #should be the same as myBucket

# each object in bucket.objects.all() will have a key attribute and bucket_name attribute

# if I want all key names or .gz file name,s I can do this:
keyList = []
for item in bucket.objects.all():
    keyList.append(item.key)

len(keyList) #to see how many .gz files are in the bucket

#________________________ 
# Now I'm gonna take a look at boto3.client('s3')

# trying another way to access buckets...with 'client'
client = boto3.client('s3')
#http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketGET.html
bucketDict = client.list_objects(Bucket=myBucket) # can also have Bucket, Delimiter, EncodingType, Marker, MaxKeys, Prefix
# the above is a dictionary with the following:
#    'Name': just returns myBucket value
#    'ResponseMetadata': is another dictionary with:
#         'HTTPStatusCode' : would give 200 or something
#         'HostId': long string of junk
#         'RequestId': string of junk
#    'MaxKeys':1000 ...only allows 1000 
#    'Prefix': ''
#    'Marker': u''
#    'EncodingType': 'url'
#    'IsTruncated': True
#    'Contents': list of values ... limited to at most 1000 values. must run again with Markers='last key value' to get next 1000
#       ^so each element in the list of Contents is a dictionary with the following keys:
#          'LastModified': datetime.datetime(2015, 9, 10, 20, 59, 20, tzinfo=tzutc())
#          'ETag':"fec849f4388c5800ae4c8946a337444d" <- string
#          'StorageClass':'STANDARD'
#          'Key': u'cloudfront-video/E8IEISA9J2WM6.2015-09-10-20.c6663ef4.gz'
#          'Owner': dictionary with keys: 'DisplayName':awsdatafeeds and 'ID':long string
#          'Size': number of bytes

# for example: our myBucket has 11058 .gz files. so I'd have to run this like 11 times to get all .gz files
marker = bucketDict['Contents'][bucketDict['MaxKeys']-1]['Key']
bucketDict = client.list_objects(Bucket=myBucket, Marker=marker)
print(bucketDict['IsTruncated'])
print(len(bucketDict['Contents']))

# So that client stuff is far more complicated but it could be helpful to have that extra information later...but doubt it since the individual buckets aren't important but the actual .gz logs are.



#_______________________
# aight let's try to download .gz files
# use boto3.resource('s3')

s3 = boto3.resource('s3')
bucket = s3.Bucket(myBucket)

keyList = []
for i,item in enumerate(bucket.objects.all()):
    file_name = str(i)+'.gz'
    bucket.download_file(item.key, file_name)

# that should download them all but still need to open them


#_____________________
# let's try to open them straight from s3 bucket instead of downloading them to computer then reading in

# try giving dates and read in those files to then read in the dates for that.







