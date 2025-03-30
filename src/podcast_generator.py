from feedgen.feed import FeedGenerator
from datetime import datetime
import os
from dateutil import tz

class PodcastGenerator:
    def __init__(self, title: str, description: str, website_url: str):
        self.fg = FeedGenerator()
        self.fg.title(title)
        self.fg.description(description)
        self.fg.link(href=website_url)
        self.fg.language('en')
        self.fg.lastBuildDate(datetime.now(tz.UTC))

    def add_episode(self, title: str, description: str, audio_url: str, pub_date: datetime = None):
        """
        Add an episode to the podcast feed.
        """
        fe = self.fg.add_entry()
        fe.title(title)
        fe.description(description)
        fe.enclosure(audio_url, 0, 'audio/mpeg')
        fe.pubdate(pub_date or datetime.now(tz.UTC))

    def generate_feed(self, output_path: str) -> str:
        """
        Generate the RSS feed and save it to a file.
        """
        try:
            # Create the feed
            feed = self.fg.rss_str(pretty=True)
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(feed)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating feed: {e}")
            return None 