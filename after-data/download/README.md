# Documentation for s3_to_log.py

$ python s3_to_log.py bucket=com.mixafter.dev.logs prefix=cloudfront-video 2015-10-02 2015-11-02 folder=s3_pull

The default lines are above. You can not include them and it will default to that.

If the bucket name as a '-' in it then there will be a problem. prefix can have a '-' in it.

It expects the date to follow this format year-month-day with at most 2 digits.
Dates can be put in any order and it will sort that way. It will also work for one day.
The script automatically pulls an additional day of logs to allow for overflow.

The .gz files will temporarily be stored in a folder and then deleted when the unzipping is finished.
NEW: the .gz files will be concatenated to a single .gz file that will be stored in the same folder.
Only that file will be unzipped. 

The unzipped files will be recorded as .log files and will be stored in a given folder name or as the default 's3_pull'.

The request data will also be logged in a .txt file giving the inputed parameters (bucket, prefix, dates)
