# PGPod - Paul Graham Podcast

A tool that converts Paul Graham's essays into audio podcasts.

## Features

- Fetches essays from paulgraham.com
- Converts text to speech using ElevenLabs
- Generates podcast RSS feed
- Hosts audio files and feed on GitHub Pages

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your ElevenLabs API key:
   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ```

## Usage

Run the script to generate audio from an essay:
```bash
python3 src/blog_reader.py
```

This will:
1. Fetch the essay from paulgraham.com
2. Generate audio using ElevenLabs
3. Create an RSS feed for podcast apps

## Listening to the Podcast

Add the following RSS feed URL to your podcast app:
```
https://your-username.github.io/pgpod/output/feed.xml
```

## License

MIT License 