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

# List of Paul Graham's essays to process
ESSAY_URLS = [
    # New Essays
    "https://paulgraham.com/do.html",
    "https://paulgraham.com/woke.html",
    "https://paulgraham.com/writes.html",
    "https://paulgraham.com/when.html",
    "https://paulgraham.com/foundermode.html",
    "https://paulgraham.com/persistence.html",
    "https://paulgraham.com/reddits.html",
    "https://paulgraham.com/google.html",
    "https://paulgraham.com/best.html",
    
    # Original Essays
    "http://www.paulgraham.com/superlinear.html",
    "http://www.paulgraham.com/greatwork.html",
    "http://www.paulgraham.com/getideas.html",
    "http://www.paulgraham.com/read.html",
    "http://www.paulgraham.com/want.html",
    "http://www.paulgraham.com/alien.html",
    "http://www.paulgraham.com/users.html",
    "http://www.paulgraham.com/heresy.html",
    "http://www.paulgraham.com/words.html",
    "http://www.paulgraham.com/goodtaste.html",
    "http://www.paulgraham.com/smart.html",
    "http://www.paulgraham.com/weird.html",
    "http://www.paulgraham.com/hwh.html",
    "http://www.paulgraham.com/own.html",
    "http://www.paulgraham.com/fn.html",
    "http://www.paulgraham.com/newideas.html",
    "http://www.paulgraham.com/nft.html",
    "http://www.paulgraham.com/real.html",
    "http://www.paulgraham.com/richnow.html",
    "http://www.paulgraham.com/simply.html",
    "http://www.paulgraham.com/donate.html",
    "http://www.paulgraham.com/worked.html",
    "http://www.paulgraham.com/earnest.html",
    "http://www.paulgraham.com/ace.html",
    "http://www.paulgraham.com/airbnbs.html",
    "http://www.paulgraham.com/think.html",
    "http://www.paulgraham.com/early.html",
    "http://www.paulgraham.com/wtax.html",
    "http://www.paulgraham.com/conformism.html",
    "http://www.paulgraham.com/orth.html",
    "http://www.paulgraham.com/cred.html",
    "http://www.paulgraham.com/useful.html",
    "http://www.paulgraham.com/noob.html",
    "http://www.paulgraham.com/fh.html",
    "http://www.paulgraham.com/mod.html",
    "http://www.paulgraham.com/fp.html",
    "http://www.paulgraham.com/kids.html",
    "http://www.paulgraham.com/lesson.html",
    "http://www.paulgraham.com/nov.html",
    "http://www.paulgraham.com/genius.html",
    "http://www.paulgraham.com/sun.html",
    "http://www.paulgraham.com/pow.html",
    "http://www.paulgraham.com/disc.html",
    "http://www.paulgraham.com/pgh.html",
    "http://www.paulgraham.com/vb.html",
    "http://www.paulgraham.com/ineq.html",
    "http://www.paulgraham.com/re.html",
    "http://www.paulgraham.com/jessica.html",
    "http://www.paulgraham.com/bias.html",
    "http://www.paulgraham.com/talk.html",
    "http://www.paulgraham.com/aord.html",
    "http://www.paulgraham.com/safe.html",
    "http://www.paulgraham.com/name.html",
    "http://www.paulgraham.com/altair.html",
    "http://www.paulgraham.com/ronco.html",
    "http://www.paulgraham.com/work.html",
    "http://www.paulgraham.com/corpdev.html",
    "http://www.paulgraham.com/95.html",
    "http://www.paulgraham.com/ecw.html",
    "http://www.paulgraham.com/know.html",
    "http://www.paulgraham.com/pinch.html",
    "http://www.paulgraham.com/mean.html",
    "http://www.paulgraham.com/before.html",
    "http://www.paulgraham.com/fr.html",
    "http://www.paulgraham.com/herd.html",
    "http://www.paulgraham.com/convince.html",
    "http://www.paulgraham.com/ds.html",
    "http://www.paulgraham.com/invtrend.html",
    "http://www.paulgraham.com/startupideas.html",
    "http://www.paulgraham.com/hw.html",
    "http://www.paulgraham.com/growth.html",
    "http://www.paulgraham.com/swan.html",
    "http://www.paulgraham.com/todo.html",
    "http://www.paulgraham.com/speak.html",
    "http://www.paulgraham.com/ycstart.html",
    "http://www.paulgraham.com/property.html",
    "http://www.paulgraham.com/ambitious.html",
    "http://www.paulgraham.com/word.html",
    "http://www.paulgraham.com/schlep.html",
    "http://www.paulgraham.com/vw.html",
    "http://www.paulgraham.com/hubs.html",
    "http://www.paulgraham.com/patentpledge.html",
    "http://www.paulgraham.com/airbnb.html",
    "http://www.paulgraham.com/control.html",
    "http://www.paulgraham.com/tablets.html",
    "http://www.paulgraham.com/founders.html",
    "http://www.paulgraham.com/superangels.html",
    "http://www.paulgraham.com/seesv.html",
    "http://www.paulgraham.com/hiresfund.html",
    "http://www.paulgraham.com/yahoo.html",
    "http://www.paulgraham.com/future.html",
    "http://www.paulgraham.com/addiction.html",
    "http://www.paulgraham.com/top.html",
    "http://www.paulgraham.com/selfindulgence.html",
    "http://www.paulgraham.com/organic.html",
    "http://www.paulgraham.com/apple.html",
    "http://www.paulgraham.com/really.html",
    "http://www.paulgraham.com/discover.html",
    "http://www.paulgraham.com/publishing.html",
    "http://www.paulgraham.com/nthings.html",
    "http://www.paulgraham.com/determination.html",
    "http://www.paulgraham.com/kate.html",
    "http://www.paulgraham.com/segway.html",
    "http://www.paulgraham.com/ramenprofitable.html",
    "http://www.paulgraham.com/makersschedule.html",
    "http://www.paulgraham.com/revolution.html",
    "http://www.paulgraham.com/twitter.html",
    "http://www.paulgraham.com/foundervisa.html",
    "http://www.paulgraham.com/5founders.html",
    "http://www.paulgraham.com/relres.html",
    "http://www.paulgraham.com/angelinvesting.html",
    "http://www.paulgraham.com/convergence.html",
    "http://www.paulgraham.com/maybe.html",
    "http://www.paulgraham.com/hackernews.html",
    "http://www.paulgraham.com/13sentences.html",
    "http://www.paulgraham.com/identity.html",
    "http://www.paulgraham.com/credentials.html",
    "http://www.paulgraham.com/divergence.html",
    "http://www.paulgraham.com/highres.html",
    "http://www.paulgraham.com/artistsship.html",
    "http://www.paulgraham.com/badeconomy.html",
    "http://www.paulgraham.com/fundraising.html",
    "http://www.paulgraham.com/prcmc.html",
    "http://www.paulgraham.com/cities.html",
    "http://www.paulgraham.com/distraction.html",
    "http://www.paulgraham.com/lies.html",
    "http://www.paulgraham.com/good.html",
    "http://www.paulgraham.com/googles.html",
    "http://www.paulgraham.com/heroes.html",
    "http://www.paulgraham.com/disagree.html",
    "http://www.paulgraham.com/boss.html",
    "http://www.paulgraham.com/ycombinator.html",
    "http://www.paulgraham.com/trolls.html",
    "http://www.paulgraham.com/newthings.html",
    "http://www.paulgraham.com/startuphubs.html",
    "http://www.paulgraham.com/webstartups.html",
    "http://www.paulgraham.com/philosophy.html",
    "http://www.paulgraham.com/colleges.html",
    "http://www.paulgraham.com/die.html",
    "http://www.paulgraham.com/head.html",
    "http://www.paulgraham.com/stuff.html",
    "http://www.paulgraham.com/equity.html",
    "http://www.paulgraham.com/unions.html",
    "http://www.paulgraham.com/guidetoinvestors.html",
    "http://www.paulgraham.com/judgement.html",
    "http://www.paulgraham.com/microsoft.html",
    "http://www.paulgraham.com/notnot.html",
    "http://www.paulgraham.com/wisdom.html",
    "http://www.paulgraham.com/foundersatwork.html",
    "http://www.paulgraham.com/goodart.html",
    "http://www.paulgraham.com/startupmistakes.html",
    "http://www.paulgraham.com/mit.html",
    "http://www.paulgraham.com/investors.html",
    "http://www.paulgraham.com/copy.html",
    "http://www.paulgraham.com/island.html",
    "http://www.paulgraham.com/marginal.html",
    "http://www.paulgraham.com/america.html",
    "http://www.paulgraham.com/siliconvalley.html",
    "http://www.paulgraham.com/startuplessons.html",
    "http://www.paulgraham.com/randomness.html",
    "http://www.paulgraham.com/softwarepatents.html",
    "http://www.paulgraham.com/6631327.html",
    "http://www.paulgraham.com/whyyc.html",
    "http://www.paulgraham.com/love.html",
    "http://www.paulgraham.com/procrastination.html",
    "http://www.paulgraham.com/web20.html",
    "http://www.paulgraham.com/startupfunding.html",
    "http://www.paulgraham.com/vcsqueeze.html",
    "http://www.paulgraham.com/ideas.html",
    "http://www.paulgraham.com/sfp.html",
    "http://www.paulgraham.com/inequality.html",
    "http://www.paulgraham.com/ladder.html",
    "http://www.paulgraham.com/opensource.html",
    "http://www.paulgraham.com/hiring.html",
    "http://www.paulgraham.com/submarine.html",
    "http://www.paulgraham.com/bronze.html",
    "http://www.paulgraham.com/mac.html",
    "http://www.paulgraham.com/writing44.html",
    "http://www.paulgraham.com/college.html",
    "http://www.paulgraham.com/venturecapital.html",
    "http://www.paulgraham.com/start.html",
    "http://www.paulgraham.com/hs.html",
    "http://www.paulgraham.com/usa.html",
    "http://www.paulgraham.com/charisma.html",
    "http://www.paulgraham.com/polls.html",
    "http://www.paulgraham.com/laundry.html",
    "http://www.paulgraham.com/bubble.html",
    "http://www.paulgraham.com/essay.html",
    "http://www.paulgraham.com/pypar.html",
    "http://www.paulgraham.com/gh.html",
    "http://www.paulgraham.com/gap.html",
    "http://www.paulgraham.com/wealth.html",
    "http://www.paulgraham.com/gba.html",
    "http://www.paulgraham.com/say.html",
    "http://www.paulgraham.com/ffb.html",
    "http://www.paulgraham.com/hp.html",
    "http://www.paulgraham.com/iflisp.html",
    "http://www.paulgraham.com/hundred.html",
    "http://www.paulgraham.com/nerds.html",
    "http://www.paulgraham.com/better.html",
    "http://www.paulgraham.com/desres.html",
    "http://www.paulgraham.com/spam.html",
    "http://www.paulgraham.com/icad.html",
    "http://www.paulgraham.com/power.html",
    "http://www.paulgraham.com/fix.html",
    "http://www.paulgraham.com/taste.html",
    "http://www.paulgraham.com/noop.html",
    "http://www.paulgraham.com/diff.html",
    "http://www.paulgraham.com/road.html",
    "http://www.paulgraham.com/rootsoflisp.html",
    "http://www.paulgraham.com/langdes.html",
    "http://www.paulgraham.com/popular.html",
    "http://www.paulgraham.com/javacover.html",
    "http://www.paulgraham.com/avg.html",
    "http://www.paulgraham.com/lwba.html",
    "http://www.paulgraham.com/acl1.txt",
    "http://www.paulgraham.com/acl2.txt",
    "http://www.paulgraham.com/progbot.html",
    "http://www.paulgraham.com/prop62.html"
]

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
    essays = ESSAY_URLS
    
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