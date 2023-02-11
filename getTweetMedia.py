
import requests
import os
import re
import sqlite3
from config import *
import pyexiv2
from datetime import datetime
from twython import Twython
# import tweepy


class TFAP:

    def __init__(self):
        pass

    def save_image(self, image_url, i):
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接

        # Download the image
        response = s.get(image_url)
        image_data = response.content

        # Write the image to disk
        image_extension = image_url.split(".")[-1]
        image_extension = image_extension.split("?")[0]
        filename = os.path.join(
            self.year_month_dir, f"{self.tweet_id}_{i}.{image_extension}")
        with open(filename, "wb") as f:
            f.write(image_data)

        if image_extension in ["jpg", 'png']:

            # https://github.com/LeoHsiao1/pyexiv2/blob/master/docs/Tutorial-cn.md
            img = pyexiv2.Image(filename)

            exif = {
                'Exif.Image.Artist': self.user_name,
                'Exif.Photo.DateTimeOriginal': self.created_at,
                'Exif.Image.ImageDescription': self.full_text
            }
            img.modify_exif(exif)

            iptc = {
                # https://github.com/LeoHsiao1/pyexiv2/issues/107#issuecomment-1426647658
                # 指定编码格式，避免乱码：マリンのお宝 -> ã, ãƒžãƒªãƒ, šå
                'Iptc.Envelope.CharacterSet': '\x1b%G',
                'Iptc.Application2.Keywords': self.hashtags
            }
            img.modify_iptc(iptc)

            xmp = {
                'Xmp.dc.subject': "Twitter Favorites Archive Project"
            }
            img.modify_xmp(xmp)

            img.modify_comment(" ".join(self.url))

            img.close()

    def TFAP(self):

        # Connect to the SQLite database
        conn = sqlite3.connect("liked_tweets.db")
        cursor = conn.cursor()

        # Create the table to store the data if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS liked_tweets (
            tweet_id TEXT PRIMARY KEY,
            tweet_time TEXT
        )
        """)

        # Create an instance of the Twython client
        twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

        # 定义一个初始的最大ID
        max_id = None

        # 遍历点赞列表
        while True:
            # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list
            # 获取当前登录用户的点赞
            liked_tweets = twitter.get_favorites(max_id=max_id, count=200)

            # 如果列表为空，退出循环
            if not liked_tweets:
                break

            # 遍历点赞列表
            for tweet in liked_tweets:
                # Get the tweet id
                self.tweet_id = tweet["id_str"]

                # Check if the tweet is already in the database
                cursor.execute(
                    "SELECT * FROM liked_tweets WHERE tweet_id=?", (self.tweet_id,))
                if cursor.fetchone():
                    # Skip this tweet if it's already in the database
                    continue

                self.full_text = re.compile(
                    r'(https?://\S+)', re.S).sub("", tweet['text'])
                self.hashtags = []
                for hashtag in tweet['entities']['hashtags']:
                    self.hashtags.append(hashtag['text'])
                self.url = re.findall(r'(https?://\S+)', tweet['text'])

                # Get the screen name of the tweet author
                self.user_name = tweet["user"]["screen_name"]

                # Create the directory for the author
                author_dir = os.path.join(SAVE_PATH, self.user_name)
                os.makedirs(author_dir, exist_ok=True)

                # Get the year and month from the tweet time
                dt_object = datetime.strptime(
                    tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')
                self.created_at = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                print(self.created_at)
                # 年
                year = dt_object.strftime("%Y")

                # 月
                month = dt_object.strftime("%m")

                # Create the subdirectory for year and month
                self.year_month_dir = os.path.join(author_dir, year, month)
                os.makedirs(self.year_month_dir, exist_ok=True)

                # Get the media entities for the tweet
                try:
                    # extended_entities可能不存在
                    media_entities = tweet["extended_entities"].get(
                        "media", [])
                except:
                    print("Failed to get media of ", self.url)
                    continue
                image_url = None

                # Iterate over each media entity
                for i, media_entity in enumerate(media_entities):
                    # media type. see also: https://www.rubydoc.info/gems/twitter/Twitter/Media, https://docs.tweepy.org/en/stable/v2_models.html#tweepy.Media
                    if media_entity["type"] == "photo":
                        # Get the image URL
                        image_url = media_entity["media_url_https"] + \
                            "?format=jpg&name=large"

                        self.save_image(image_url, i)

                    # 1. download video with highest bitrate
                    # 2. video does not support some metadata fields, so download image too
                    if media_entity["type"] in ["video", "animated_gif"]:
                        image_url = media_entity["media_url_https"] + \
                            "?format=jpg&name=large"
                        self.save_image(image_url, i)

                        max_bitrate = 0
                        video_url = None
                        for variant in media_entity['video_info']['variants']:
                            if 'bitrate' in variant and variant['bitrate'] >= max_bitrate:
                                max_bitrate = variant['bitrate']
                                video_url = variant['url']
                            # Close the database connection
                        self.save_image(video_url, i)
                # Insert the tweet into the database
                cursor.execute("""
                INSERT OR REPLACE INTO liked_tweets (tweet_id, tweet_time)
                VALUES (?, ?)
                """, (self.tweet_id, self.created_at))

                conn.commit()

            # 设置最大ID为最后一条点赞的ID
            max_id = liked_tweets[-1]['id'] - 1

        conn.close()


tfap = TFAP()
tfap.TFAP()
