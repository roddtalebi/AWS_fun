## this script contains code chunks that can be used to compile contest reports

# imports
library(dplyr)
library(ggplot2)
library(lubridate)
library(plotly)
library(stringr)

# prior to this step create a data frame for the desired time period using the cdn log analysis preprocessing script

# read in data (csv)
file <- file.choose()
contest.data <- read.csv(file)

# rename columns using convention
colnames(contest.data) <- c('post.id', 'title', 'stats.likes', 'stats.shares', 'video.loops', 'user.id', 'user.name', 'date.created', 'date.published')

# fix dates
contest.data$date.created <- ymd_hms(contest.data$date.created)
contest.data$date.published <-ymd_hms(contest.data$date.published)

# create a edt date column
contest.data$edt.date.time <- with_tz(contest.data$date.published, "America/New_York")
contest.data$edt.date <- as.Date(contest.data$edt.date.time)
contest.data$edt.date <- ymd(contest.data$edt.date)

# remove unpublished videos
contest.data <- contest.data[complete.cases(contest.data$date.published),]

## create a subset of all activity for activity related to contest
# first make a list of unique contest videos
video.ids <- unique(contest.data$post.id)
#filter main activity log to only contain contest videos
contest.log <- filter(log, post.id %in% video.ids)
# subset log one before and after contest end 
begin.date <- "2016-04-18 12:00:00 EDT"
end.date <- "2016-06-01 23:59:59"
contest.log <- subset(contest.log, edt.time >= begin.date & edt.time <= end.date)

## counting statistics
# subset contest log to only hls-realted files
contest.hls <- contest.log %>% filter(str_detect(cs.uri.stem, c(".m3u8", ".ts")))
# subset logs related to main index calls
contest.i <- contest.log %>% filter(str_detect(cs.uri.stem, "index.m3u8"))

# count number of log entires per video
library(plyr)
post.count.all <- count(contest.hls, "post.id")
# count number of index calls per video
post.count.index <- count(contest.i, "post.id")

# attach names, video title, and user id to index count
i <- 1
for (id in post.count.index$post.id){
  name <- contest.data[which(contest.data$post.id == id), "user.name"]
  post.count.index[i, "user.name"] <- name
  title <- contest.data[which(contest.data$post.id == id), "title"]
  post.count.index[i, "title"] <- title
  user.id <- contest.data[which(contest.data$post.id == id), "user.id"]
  post.count.index[i, "user.id"] <- user.id
  pub <- as.character(contest.data[which(contest.data$post.id == id), "edt.date"])
  post.count.index[i, "date.published"] <- pub
  i <- i +1
}
# make column names more readable
colnames(post.count.index) <- c("Post ID", "Views", "User Name", "Video Title", "User ID", "Date Published")
# output results as a csv
output <- post.count.index[order(-post.count.index$Views),]
write.csv(output, "contest_results.csv", row.names = FALSE)


## contest overview video analysis

# this command can be used to get views related to contest overview videos
# if contest videos are still named using the convention of word titles, replace "deep" and "Deep" with a unique word from the contest

# subset data for stem ids that contain "Deep"
deep <- log %>% filter(str_detect(cs.uri.stem, "Deep"))
# get unique cs.uri.stem values
deep.u <- unique(deep$cs.uri.stem)
# subset all logs related to hls streaming
deep.v <- deep %>% filter(str_detect(cs.uri.stem, c(".m3u8", ".ts")))
# subset logs related to main index calls
deep.i <- deep.v %>% filter(str_detect(cs.uri.stem, "index.m3u8"))
#find number of unique ips in deep.v logs
length(unique(deep.v$c.ip))

## contest viz

# plot videos published by date
ggplot(contest.data, aes(edt.date)) + 
  geom_bar(colour = "darkblue", fill = "cadetblue1") + 
  labs(x = "Day", y = "", title = "Contest Videos by Date Published") + theme(axis.text.x  = element_text(vjust=-0.5, size=8))
ggplotly()

# plot index call activy by weekday
c <- ggplot(contest.i, aes(factor(weekday)))
# this line manually arranges day of the week
c + geom_bar(fill = "cadetblue1", colour = "steelblue") + scale_x_discrete(limits = c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"))
ggplotly()

# plot index call activity by hour of day
c <- ggplot(contest.i, aes(factor(hour)))
c + geom_bar(fill = "cadetblue1", colour = "steelblue") + labs(x = "Hour", y = "", title = "Index Calls by Hour")
ggplotly()

# plot edge location
library(scales)
c <- ggplot(contest.i, aes(factor(x.edge.location)))
c + geom_bar(fill = "plum2", colour = "khaki") + labs(x = "Edge Location", y = "", title = "Index Calls by Edge Location") + theme(
  axis.text.x = element_blank()) + scale_y_continuous(labels = comma) + scale_x_discrete(breaks=NULL)
ggplotly()

# plot index call activity
c <- ggplot(contest.i, aes(edt.date))
# this line manually arranges day of the week
c + geom_bar(fill = "gold", colour = "lightslateblue") + labs(x = "Date", y = "", title = "Index Calls by Date")
ggplotly()

# side by side video created and index calls
# not working yet
# better for counts that are closer in sum
index.counts <- count(contest.i, "edt.date")
create.counts <- count(contest.data, "edt.date")
create.counts$flag <- 1
index.counts$flag <- 0
growth.counts <- rbind(create.counts, index.counts)
ggplot(growth.counts, aes(x=edt.date, y=freq, fill=flag)) + geom_bar(position='dodge', stat='identity')
ggplotly()

# plot stacked bar of total traffic and contest traffic (trafic = log entries in this example)
# this requires making a contest flag column in time frame data
# custom legend labels don't yet work with ggplotly
time.frame$contest.flag <- 0
contest.indicies <- which(time.frame$post.id %in% video.ids)
time.frame[contest.indicies, "contest.flag"] <- 1
ggplot(time.frame, aes(edt.date)) + 
  geom_bar(colour="darkblue", aes(fill=factor(contest.flag))) +
  labs(x = "Date", y = "", title = "Total Log Entries During Lunazul Contest") + 
  scale_fill_manual(values=c("steelblue", "gold"), name="Traffic Type", labels=c("Non-contest", "Contest"))
ggplotly()

# plot ip counts in contest log
# NEED TO FINISH THIS
ip.counts <- count(contest.log, "c.ip")



# plot contest videos in three dimensions using gradient color fill
ggplot(data4, aes(x=edt.published, y=freq, colour=likes)) + geom_point() + scale_colour_gradient(low = "yellow", high = "red") + labs(x = "Date Published", y = "Views")
ggplotly()


