import os
from elevenlabs import generate, save, set_api_key
from typing import Optional
from dotenv import load_dotenv

class TextToSpeech:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        print("Setting up ElevenLabs API key...")
        set_api_key(api_key)

    def generate_audio(self, text: str, output_path: str, voice: str = "Rachel") -> Optional[str]:
        """
        Generate audio from text using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the audio file
            voice: The voice to use (default: Rachel)
            
        Returns:
            Path to the generated audio file if successful, None otherwise
        """
        try:
            print(f"Generating audio with voice: {voice}")
            print(f"Text length: {len(text)} characters")
            
            # Split text into sentences
            sentences = text.split('.')
            print(f"Split into {len(sentences)} sentences")
            
            # Process only the first 5 sentences
            chunk_size = 5
            chunk = '. '.join(sentences[:chunk_size])
            print(f"\nProcessing first chunk only")
            print(f"Chunk length: {len(chunk)} characters")
            print(f"Chunk content: {chunk}")
            
            # Generate audio for this chunk
            print("Calling ElevenLabs API...")
            audio = generate(
                text=chunk,
                voice=voice,
                model="eleven_monolingual_v1"
            )
            
            # Save the audio file
            print("Saving audio to file...")
            with open(output_path, 'wb') as f:
                f.write(audio)
            
            print(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            print(f"Error type: {type(e)}")
            return None 