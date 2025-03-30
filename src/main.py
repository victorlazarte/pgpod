import argparse
import os
import json
from datetime import datetime
from blog_reader import BlogReader
from text_to_speech import TextToSpeech
from podcast_generator import PodcastGenerator

def process_blog_post(url: str, title: str, output_dir: str, voice: str, podcast: PodcastGenerator):
    """
    Process a single blog post and add it to the podcast feed.
    """
    print(f"\nProcessing blog post: {title}")
    print(f"URL: {url}")
    
    # Initialize components
    blog_reader = BlogReader()
    tts = TextToSpeech()
    
    # Fetch and process blog content
    print(f"Fetching content from {url}...")
    content = blog_reader.fetch_content(url)
    if not content:
        print(f"Failed to fetch blog content for {title}")
        return False
    
    print(f"Successfully fetched content, length: {len(content)} characters")
    
    # Clean the text
    content = blog_reader.clean_text(content)
    
    # Generate audio file
    audio_path = os.path.join(output_dir, f"{title.lower().replace(' ', '_')}.mp3")
    print(f"Generating audio for {title}...")
    if not tts.generate_audio(content, audio_path, voice):
        print(f"Failed to generate audio for {title}")
        return False
    
    print(f"Successfully generated audio at: {audio_path}")
    
    # Add the episode to the podcast feed
    podcast.add_episode(
        title=title,
        description=f"Audio version of: {title}",
        audio_url=audio_path,
        pub_date=datetime.utcnow()
    )
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Convert blog posts to podcast episodes')
    parser.add_argument('--input-file', default='blog_posts.json', help='JSON file containing blog posts')
    parser.add_argument('--output-dir', default='output', help='Directory to save output files')
    parser.add_argument('--voice', default='Rachel', help='ElevenLabs voice to use')
    parser.add_argument('--podcast-title', default='Blog to Podcast', help='Title of the podcast')
    parser.add_argument('--podcast-description', default='Converted blog posts to audio', help='Description of the podcast')
    parser.add_argument('--website-url', default='https://example.com', help='Website URL for the podcast')
    
    args = parser.parse_args()
    
    print(f"Starting script with input file: {args.input_file}")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Created/verified output directory: {args.output_dir}")
    
    # Read blog posts from JSON file
    try:
        print(f"Reading blog posts from {args.input_file}...")
        with open(args.input_file, 'r') as f:
            data = json.load(f)
            blog_posts = data.get('blog_posts', [])
            print(f"Found {len(blog_posts)} blog posts in the file")
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    if not blog_posts:
        print("No blog posts found in the input file")
        return
    
    # Initialize podcast generator
    podcast = PodcastGenerator(
        title=args.podcast_title,
        description=args.podcast_description,
        website_url=args.website_url
    )
    
    # Process each blog post
    successful_posts = 0
    for post in blog_posts:
        url = post.get('url')
        title = post.get('title')
        
        if not url or not title:
            print(f"Skipping invalid blog post entry: {post}")
            continue
        
        if process_blog_post(url, title, args.output_dir, args.voice, podcast):
            successful_posts += 1
    
    if successful_posts > 0:
        # Save the feed
        feed_path = os.path.join(args.output_dir, "feed.xml")
        if podcast.generate_feed(feed_path):
            print(f"Successfully generated podcast feed at {feed_path}")
            print(f"Processed {successful_posts} out of {len(blog_posts)} blog posts")
        else:
            print("Failed to generate podcast feed")
    else:
        print("No blog posts were successfully processed")

if __name__ == "__main__":
    main() 