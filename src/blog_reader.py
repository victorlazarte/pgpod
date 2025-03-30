import requests
from bs4 import BeautifulSoup
from elevenlabs import generate, save, set_api_key, voices
import os
from dotenv import load_dotenv
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_rss_feed(audio_path: str, title: str, description: str):
    # Create the RSS feed structure
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    
    channel = ET.SubElement(rss, 'channel')
    
    # Add podcast metadata
    ET.SubElement(channel, 'title').text = title
    ET.SubElement(channel, 'description').text = description
    ET.SubElement(channel, 'link').text = 'https://paulgraham.com'
    ET.SubElement(channel, 'language').text = 'en-us'
    ET.SubElement(channel, 'pubDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # Add the episode
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = title
    ET.SubElement(item, 'description').text = description
    ET.SubElement(item, 'pubDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # Add audio file enclosure
    enclosure = ET.SubElement(item, 'enclosure')
    # Use GitHub Pages URL
    github_username = os.getenv('GITHUB_USERNAME', 'your-username')  # You'll need to set this in .env
    enclosure.set('url', f'https://{github_username}.github.io/pgpod/{audio_path}')
    enclosure.set('type', 'audio/mpeg')
    enclosure.set('length', str(os.path.getsize(audio_path)))
    
    # Create the XML file
    xmlstr = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="   ")
    
    # Save the RSS feed
    rss_path = os.path.join('output', 'feed.xml')
    with open(rss_path, 'w') as f:
        f.write(xmlstr)
    
    print(f"\nRSS feed saved to: {rss_path}")
    print("\nTo listen to this podcast:")
    print(f"Add this URL to your podcast app: https://{github_username}.github.io/pgpod/output/feed.xml")

def fetch_content(url: str):
    try:
        print(f"Fetching {url}...")
        response = requests.get(url)
        print(f"Got response with status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Parsed HTML")
        
        # Get all text from the page
        text = soup.get_text()
        
        # Clean up the text by removing extra whitespace and newlines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = ' '.join(lines)
        
        print("\nFirst few lines of the essay:")
        first_lines = text.split('.')[:3]
        for line in first_lines:
            print(f"- {line.strip()}.")
            
        # Generate audio from the first three sentences
        print("\nGenerating audio...")
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
            
        set_api_key(api_key)
        
        # List available voices
        print("\nAvailable voices:")
        available_voices = voices()
        for voice in available_voices:
            print(f"- {voice.name}")
        
        # Use the first available voice
        voice_name = available_voices[0].name
        print(f"\nUsing voice: {voice_name}")
        
        # Combine the first three sentences
        text_to_speak = '. '.join(first_lines)
        print(f"Text to speak: {text_to_speak}")
        
        # Generate audio
        audio = generate(
            text=text_to_speak,
            voice="Sarah",
            model="eleven_monolingual_v1"
        )
        
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the audio file in the output directory
        output_path = os.path.join(output_dir, "first_paragraph.mp3")
        save(audio, output_path)
        print(f"\nAudio saved to: {output_path}")
        
        # Create RSS feed
        create_rss_feed(
            output_path,
            "Paul Graham: How to Do Great Work",
            "First paragraph of Paul Graham's essay 'How to Do Great Work'"
        )
        
        return text
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def list_voices():
    try:
        print("Loading API key...")
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
            
        set_api_key(api_key)
        
        # List available voices
        print("\nAvailable voices:")
        available_voices = voices()
        for voice in available_voices:
            print(f"- {voice.name}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    url = "https://paulgraham.com/greatwork.html"
    fetch_content(url) 