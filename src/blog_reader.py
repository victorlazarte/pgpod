import requests
from bs4 import BeautifulSoup
from elevenlabs import generate, save, set_api_key, voices
import os
from dotenv import load_dotenv
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import argparse
import hashlib
from pydub import AudioSegment
import time
import concurrent.futures
import json

def get_essay_filename(url: str, title: str) -> str:
    """Generate a filename based on the URL title"""
    # Get the exact title from the URL and convert to filename format
    url_title = url.split('/')[-1].replace('.html', '')
    return f"{url_title}.mp3"

def find_audio_file(output_dir: str, expected_filename: str) -> str:
    """Find an audio file in the output directory, case-insensitive"""
    expected_name = expected_filename.lower()
    print(f"Looking for file matching: {expected_name}")
    
    for filename in os.listdir(output_dir):
        print(f"Checking file: {filename}")
        if filename.lower() == expected_name:
            full_path = os.path.join(output_dir, filename)
            print(f"Found matching file: {full_path}")
            return full_path
    
    print(f"No matching file found for {expected_name}")
    return None

def split_text_into_chunks(text: str, max_chars: int = 4000) -> list:
    """Split text into chunks that are safe for the API"""
    chunks = []
    current_chunk = []
    current_length = 0
    
    # Split by sentences to avoid cutting mid-sentence
    sentences = text.split('. ')
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length > max_chars:
            chunks.append('. '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append('. '.join(current_chunk))
    
    return chunks

def generate_chunk_audio(chunk: str, chunk_path: str, api_key: str, voice: str = "Sarah"):
    """Generate audio for a single chunk using a specific API key"""
    try:
        set_api_key(api_key)
        audio = generate(
            text=chunk,
            voice=voice,
            model="eleven_monolingual_v1"
        )
        save(audio, chunk_path)
        return chunk_path
    except Exception as e:
        print(f"Error generating audio for chunk: {str(e)}")
        return None

def generate_audio_for_text(text: str, output_path: str, api_keys: list, voice: str = "Sarah"):
    """Generate audio for text, handling it in chunks if necessary"""
    print(f"Generating audio for text (length: {len(text)} characters)...")
    
    # Split text into chunks if it's too long
    chunks = split_text_into_chunks(text)
    print(f"Split text into {len(chunks)} chunks")
    
    # Generate audio for each chunk in parallel
    audio_segments = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_keys)) as executor:
        future_to_chunk = {}
        for i, chunk in enumerate(chunks, 1):
            chunk_path = f"{output_path}.part{i}"
            # Round-robin API key assignment
            api_key = api_keys[(i-1) % len(api_keys)]
            future = executor.submit(generate_chunk_audio, chunk, chunk_path, api_key, voice)
            future_to_chunk[future] = chunk_path
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_path = future_to_chunk[future]
            try:
                result = future.result()
                if result:
                    audio_segments.append(result)
                    print(f"Generated audio for chunk: {chunk_path}")
            except Exception as e:
                print(f"Error processing chunk {chunk_path}: {str(e)}")
    
    # Combine all chunks into one file
    if len(audio_segments) > 1:
        print(f"\nCombining {len(audio_segments)} audio chunks...")
        try:
            # Load the first chunk
            print(f"Loading first chunk: {audio_segments[0]}")
            combined = AudioSegment.from_mp3(audio_segments[0])
            
            # Add the rest of the chunks
            for i, segment_path in enumerate(audio_segments[1:], 1):
                print(f"Adding chunk {i+1}: {segment_path}")
                segment = AudioSegment.from_mp3(segment_path)
                combined += segment
            
            # Export the combined audio
            print(f"Exporting combined audio to: {output_path}")
            combined.export(output_path, format="mp3")
            print(f"Successfully combined audio saved to {output_path}")
            
            # Clean up temporary chunk files
            print("Cleaning up temporary chunk files...")
            for segment_path in audio_segments:
                try:
                    os.remove(segment_path)
                    print(f"Removed temporary file: {segment_path}")
                except Exception as e:
                    print(f"Warning: Could not remove temporary file {segment_path}: {str(e)}")
            
        except Exception as e:
            print(f"Error combining audio chunks: {str(e)}")
            print("Keeping temporary chunk files for debugging")
            raise
    else:
        # If there's only one chunk, just rename it
        try:
            print(f"Only one chunk, renaming {audio_segments[0]} to {output_path}")
            os.rename(audio_segments[0], output_path)
            print(f"Audio saved to {output_path}")
        except Exception as e:
            print(f"Error renaming single chunk: {str(e)}")
            raise

def create_rss_feed(essays: list):
    try:
        print("\nCreating RSS feed...")
        # Create the RSS feed structure
        rss = ET.Element('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        
        channel = ET.SubElement(rss, 'channel')
        
        # Add podcast metadata
        ET.SubElement(channel, 'title').text = "Paul Graham Essays"
        ET.SubElement(channel, 'description').text = "Audio versions of Paul Graham's essays"
        ET.SubElement(channel, 'link').text = 'https://paulgraham.com'
        ET.SubElement(channel, 'language').text = 'en-us'
        ET.SubElement(channel, 'pubDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Add iTunes-specific tags
        ET.SubElement(channel, 'itunes:title').text = "Paul Graham Essays"
        ET.SubElement(channel, 'itunes:author').text = 'Paul Graham'
        ET.SubElement(channel, 'itunes:summary').text = "Audio versions of Paul Graham's essays"
        ET.SubElement(channel, 'itunes:type').text = 'episodic'
        ET.SubElement(channel, 'itunes:explicit').text = 'no'
        
        # Add each essay as an episode
        for essay in essays:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = essay['title']
            ET.SubElement(item, 'description').text = essay['description']
            ET.SubElement(item, 'pubDate').text = essay['pub_date']
            
            # Add iTunes-specific tags for the episode
            ET.SubElement(item, 'itunes:title').text = essay['title']
            ET.SubElement(item, 'itunes:author').text = 'Paul Graham'
            ET.SubElement(item, 'itunes:summary').text = essay['description']
            ET.SubElement(item, 'itunes:episodeType').text = 'full'
            ET.SubElement(item, 'itunes:explicit').text = 'no'
            
            # Add audio file enclosure
            enclosure = ET.SubElement(item, 'enclosure')
            github_username = os.getenv('GITHUB_USERNAME', 'victorlazarte')
            enclosure_url = f'https://{github_username}.github.io/pgpod/{essay["audio_path"]}'
            print(f"Setting enclosure URL for {essay['title']}: {enclosure_url}")
            enclosure.set('url', enclosure_url)
            enclosure.set('type', 'audio/mpeg')
            enclosure.set('length', str(os.path.getsize(essay['audio_path'])))
        
        # Create the XML file
        xmlstr = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="   ")
        
        # Save the RSS feed
        rss_path = os.path.join('output', 'feed.xml')
        print(f"Saving RSS feed to: {rss_path}")
        with open(rss_path, 'w') as f:
            f.write(xmlstr)
        
        print(f"RSS feed saved successfully")
        print(f"Feed URL: https://{github_username}.github.io/pgpod/output/feed.xml")
        
    except Exception as e:
        print(f"Error creating RSS feed: {str(e)}")
        raise

def fetch_content(url: str, generate_audio: bool = False, api_keys: list = None):
    try:
        print(f"\nFetching {url}...")
        response = requests.get(url)
        print(f"Got response with status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Parsed HTML")
        
        # Get all text from the page
        text = soup.get_text()
        
        # Clean up the text by removing extra whitespace and newlines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = ' '.join(lines)
        
        # Get the title from the URL
        title = url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
        
        print(f"\nProcessing essay: {title}")
        print("\nFirst few lines of the essay:")
        first_lines = text.split('.')[:3]
        for line in first_lines:
            print(f"- {line.strip()}.")
            
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on the essay title
        audio_filename = get_essay_filename(url, title)
        print(f"Generated filename: {audio_filename}")
        output_path = os.path.join(output_dir, audio_filename)
        
        # Check if file exists (case-insensitive)
        existing_file = find_audio_file(output_dir, audio_filename)
        if existing_file:
            print(f"Found existing audio file: {existing_file}")
            output_path = existing_file
        else:
            print(f"Listing all files in output directory:")
            for f in os.listdir(output_dir):
                print(f"- {f}")
        
        # Generate audio only if requested and file doesn't exist
        if generate_audio and not existing_file:
            print(f"\nGenerating audio for {title}...")
            if not api_keys:
                raise ValueError("No API keys provided")
            
            # Generate audio for the entire essay
            generate_audio_for_text(text, output_path, api_keys)
            print(f"\nAudio saved to: {output_path}")
        elif existing_file:
            print(f"Audio file already exists for {title}")
        else:
            print(f"Error: Audio file not found for {title}. Run with --generate-audio to create it.")
            return None
        
        return {
            'title': title,
            'description': f"Audio version of Paul Graham's essay '{title}'",
            'audio_path': output_path,
            'pub_date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S %z')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def load_api_keys():
    """Load API keys from environment variables"""
    load_dotenv()
    api_keys = []
    i = 1
    while True:
        key = os.getenv(f'ELEVENLABS_API_KEY_{i}')
        if not key:
            break
        api_keys.append(key)
        i += 1
    
    # Fallback to single API key if no numbered keys found
    if not api_keys:
        key = os.getenv('ELEVENLABS_API_KEY')
        if key:
            api_keys.append(key)
    
    return api_keys

def recombine_chunks(output_path: str):
    """Recombine existing audio chunks into a single file"""
    try:
        # Find all chunk files
        chunk_files = []
        i = 1
        while True:
            chunk_path = f"{output_path}.part{i}"
            if not os.path.exists(chunk_path):
                break
            chunk_files.append(chunk_path)
            i += 1
        
        if not chunk_files:
            print(f"No chunk files found for {output_path}")
            return False
            
        print(f"\nFound {len(chunk_files)} chunk files to combine")
        
        # Load the first chunk
        print(f"Loading first chunk: {chunk_files[0]}")
        combined = AudioSegment.from_mp3(chunk_files[0])
        
        # Add the rest of the chunks
        for i, segment_path in enumerate(chunk_files[1:], 1):
            print(f"Adding chunk {i+1}: {segment_path}")
            segment = AudioSegment.from_mp3(segment_path)
            combined += segment
        
        # Export the combined audio
        print(f"Exporting combined audio to: {output_path}")
        combined.export(output_path, format="mp3")
        print(f"Successfully combined audio saved to {output_path}")
        
        # Clean up temporary chunk files
        print("Cleaning up temporary chunk files...")
        for segment_path in chunk_files:
            try:
                os.remove(segment_path)
                print(f"Removed temporary file: {segment_path}")
            except Exception as e:
                print(f"Warning: Could not remove temporary file {segment_path}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"Error combining audio chunks: {str(e)}")
        print("Keeping temporary chunk files for debugging")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate podcast from Paul Graham essays')
    parser.add_argument('--generate-audio', action='store_true', help='Generate audio files')
    parser.add_argument('--recombine', action='store_true', help='Recombine existing audio chunks')
    args = parser.parse_args()
    
    # Load API keys
    api_keys = load_api_keys()
    if args.generate_audio and not api_keys:
        print("Error: No API keys found. Please set ELEVENLABS_API_KEY or ELEVENLABS_API_KEY_1 in your .env file")
        exit(1)
    
    print(f"Loaded {len(api_keys)} API key(s)")
    
    # List of essays to process
    essays = [
        "https://paulgraham.com/greatwork.html",
        "https://paulgraham.com/wealth.html"
    ]
    
    # Process each essay
    processed_essays = []
    for url in essays:
        # Generate unique filename for this essay
        audio_filename = get_essay_filename(url, url.split('/')[-1].replace('.html', '').replace('-', ' ').title())
        output_path = os.path.join('output', audio_filename)
        
        # Recombine chunks if requested
        if args.recombine:
            if recombine_chunks(output_path):
                print(f"Successfully recombined chunks for {url}")
            else:
                print(f"Failed to recombine chunks for {url}")
                continue
        
        essay_data = fetch_content(url, args.generate_audio, api_keys)
        if essay_data:
            processed_essays.append(essay_data)
    
    # Create RSS feed with all processed essays
    if processed_essays:
        create_rss_feed(processed_essays) 