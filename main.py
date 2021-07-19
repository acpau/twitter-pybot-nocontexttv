import tweepy
import os
import random
import operator
from pysubparser.cleaners import ascii, brackets, formatting, lower_case
from pysubparser import parser
import datetime
import time
import schedule
#import cv2

#Enable for console debugging. 
subtitleDebug = False

##########
# Setup Twitter API.

consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
key = 'key'
secret = 'secret'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

print("[", datetime.datetime.now().strftime("%H:%M:%S"), "] - ", "Bot initialized.")

api = tweepy.API(auth, wait_on_rate_limit=True)

##########

# "Schedule" works with callables.
class randCaption:
    # The main function.
    def __call__(self):
        #Choose a random SRT file from a location.
        # SRT files must be in './media/srt/' and H264 files in './media/h264/'.
        # SRT files must have the same name as corresponding H264 video.
        srtFile = random.choice(os.listdir("./media/srt"))
        srtDir = "./media/srt/" + srtFile

        indexMax = 0

        h264File = srtFile.split(".")
        h264Dir = "./media/mkv/" + h264File[0] + ".mkv"

        #cap=cv2.VideoCapture(mkvDir)
        #fps = cap.get(cv2.CAP_PROP_FPS)
        # FPS of the video file.
        fps=23.976023976023978

        # Parse and make a list from the choosen file.
        subtitles = list(formatting.clean(parser.parse(srtDir)))

        # Search for max index (indexMax). We will use this later to choose a random caption.
        for index in subtitles:
            indexMax+=1
            #Print all subtitles if debugging is enabled.
            if subtitleDebug:
                print(indexMax-1, " // ", index.start, " > ", index.end, index)
            else:
                pass

        print("\n")
        print("SRT File choice: ", srtDir)
        print("FPS: ", fps)

        # Choose a random caption.
        indexChoice = random.randint(0,indexMax)

        # SRT files start at index 1, but 'pysub-parser' starts at 0.
        # We are substracting 1 to 'indexMax' to make it coincide with the actual SRT index.
        print("Max index count: ", indexMax-1)
        print("Index start/end (milis): ", subtitles[indexChoice].start, " >>> ", subtitles[indexChoice].end)
        print("Index choice/content: ", subtitles[indexChoice-1])

        # SRT files indicates start/end times with a timestamp (HH:MM:SS:MMMMM). 
        # We need to turn this into frame count.
        # For this we will get total amount of seconds and multyply it to 'fps'.
        indexStartFrame = datetime.timedelta(hours=subtitles[indexChoice].start.hour,
            minutes=subtitles[indexChoice].start.minute,
            seconds=subtitles[indexChoice].start.second,
            microseconds=subtitles[indexChoice].start.microsecond).total_seconds() * fps
        indexEndFrame = datetime.timedelta(hours=subtitles[indexChoice].end.hour,
            minutes=subtitles[indexChoice].end.minute,
            seconds=subtitles[indexChoice].end.second,
            microseconds=subtitles[indexChoice].end.microsecond).total_seconds() * fps
        print("Index start frame: ", int(indexStartFrame))
        print("Index start frame: ", int(indexEndFrame))
        # We are choosing a random frame between choosen index's start and end.
        # If a previously printed index is choosen again, randomizing this will ensure the image output is not the same.
        indexRandomFrameChoice = (random.randint(int(indexStartFrame),int(indexEndFrame)))
        print("Index random frame choice: ", indexRandomFrameChoice)

        print("\n")

        # Here's where the magic happens. 
        # This line updates the account's status with the choosen index.
        api.update_status(subtitles[indexChoice-1].text)
        print("[", datetime.datetime.now().strftime("%H:%M:%S"), "] - ", "Status updated.")

        '''def main():
            while True:
                try:
                    pass
                except tweepy.TweepError as e:
                    raise e

        if __name__ == "__main__":
            main()'''

# This line tells 'Schedule' when to execute the 'randCaptions' class. Default is set once per hour.
print("[", datetime.datetime.now().strftime("%H:%M:%S"), "] - ", "Task scheduled.")
schedule.every().hour.do(randCaption())

# Schedule the task previously added.
while True:
    schedule.run_pending()
    time.sleep(1)