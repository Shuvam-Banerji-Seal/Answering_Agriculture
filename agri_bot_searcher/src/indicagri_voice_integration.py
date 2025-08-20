#!/usr/bin/env python3
"""
IndicAgri Voice Transcription Integration Module

This module integrates the agri_bot voice transcription functionality
into the agri_bot_searcher system with proper language support.
"""

import os
import sys
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Add agri_bot to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
agri_bot_path = project_root / 'agri_bot'
sys.path.insert(0, str(agri_bot_path))

try:
    from agri_bot.new_bot import main as transcribe_audio
    from agri_bot.utility import mono_channel, speech_to_text_bharat, translate_indic, speech_to_text
    from agri_bot.load import ai_bharat, load_indic_trans, login_in
    HAS_AGRI_BOT = True
except ImportError as e:
    HAS_AGRI_BOT = False
    logging.warning(f"agri_bot modules not available: {e}")


class IndicAgriVoiceTranscriber:
    """
    Enhanced voice transcriber for IndicAgri using agri_bot functionality
    """
    
    # Language mappings for IndicAgri
    LANGUAGE_MAPPINGS = {
        'asm_Beng': {'name': 'Assamese (Bengali script)', 'code': 'asm_Beng'},
        'ben_Beng': {'name': 'Bengali', 'code': 'ben_Beng'},
        'brx_Deva': {'name': 'Bodo', 'code': 'brx_Deva'},
        'doi_Deva': {'name': 'Dogri', 'code': 'doi_Deva'},
        'guj_Gujr': {'name': 'Gujarati', 'code': 'guj_Gujr'},
        'hin_Deva': {'name': 'Hindi', 'code': 'hin_Deva'},
        'kan_Knda': {'name': 'Kannada', 'code': 'kan_Knda'},
        'gom_Deva': {'name': 'Konkani', 'code': 'gom_Deva'},
        'kas_Arab': {'name': 'Kashmiri (Arabic script)', 'code': 'kas_Arab'},
        'kas_Deva': {'name': 'Kashmiri (Devanagari script)', 'code': 'kas_Deva'},
        'mai_Deva': {'name': 'Maithili', 'code': 'mai_Deva'},
        'mal_Mlym': {'name': 'Malayalam', 'code': 'mal_Mlym'},
        'mni_Beng': {'name': 'Manipuri (Bengali script)', 'code': 'mni_Beng'},
        'mni_Mtei': {'name': 'Manipuri (Meitei script)', 'code': 'mni_Mtei'},
        'mar_Deva': {'name': 'Marathi', 'code': 'mar_Deva'},
        'npi_Deva': {'name': 'Nepali', 'code': 'npi_Deva'},
        'ory_Orya': {'name': 'Odia', 'code': 'ory_Orya'},
        'pan_Guru': {'name': 'Punjabi', 'code': 'pan_Guru'},
        'san_Deva': {'name': 'Sanskrit', 'code': 'san_Deva'},
        'sat_Olck': {'name': 'Santali (Ol Chiki script)', 'code': 'sat_Olck'},
        'snd_Arab': {'name': 'Sindhi (Arabic script)', 'code': 'snd_Arab'},
        'snd_Deva': {'name': 'Sindhi (Devanagari script)', 'code': 'snd_Deva'},
        'urd_Arab': {'name': 'Urdu', 'code': 'urd_Arab'},
        'eng_Latn': {'name': 'English (Latin script)', 'code': 'eng_Latn'}
    }
    
    def __init__(self):
        """Initialize the IndicAgri voice transcriber"""
        self.agri_bot_available = HAS_AGRI_BOT
        self._models_loaded = False
        self._ai_bharat_model = None
        self._indic_model = None
        self._indic_tokenizer = None
        
        if not self.agri_bot_available:
            logging.warning("agri_bot modules not available. Voice transcription will be limited.")
    
    def _ensure_models_loaded(self, use_local_model: bool = True, hf_token: Optional[str] = None):
        """Ensure models are loaded if using local models"""
        if not self.agri_bot_available or not use_local_model:
            return
            
        if self._models_loaded:
            return
            
        try:
            # Login to Hugging Face if token provided
            if hf_token:
                login_in(hf_token)
            
            # Load AI Bharat model
            logging.info("Loading AI Bharat model...")
            self._ai_bharat_model = ai_bharat()
            
            # Load IndicTrans model
            logging.info("Loading IndicTrans model...")
            self._indic_model, self._indic_tokenizer = load_indic_trans()
            
            self._models_loaded = True
            logging.info("Models loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            raise
    
    def _prepare_audio_file(self, audio_path: str) -> str:
        """
        Prepare audio file for transcription (convert to mono, 16kHz)
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Path to the processed audio file
        """
        try:
            # Use agri_bot's mono_channel function
            processed_path = mono_channel(audio_path)
            return processed_path
        except Exception as e:
            logging.error(f"Error processing audio file: {e}")
            # Fallback: try manual conversion
            return self._manual_audio_conversion(audio_path)
    
    def _manual_audio_conversion(self, audio_path: str) -> str:
        """
        Manual audio conversion using ffmpeg
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Path to the processed audio file
        """
        output_path = tempfile.mktemp(suffix='_mono.wav')
        
        try:
            command = [
                'ffmpeg', '-y', '-i', audio_path,
                '-ac', '1',  # mono channel
                '-ar', '16000',  # 16kHz sample rate
                '-f', 'wav',  # WAV format
                output_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg conversion failed: {result.stderr}")
                
            return output_path
            
        except Exception as e:
            logging.error(f"Manual audio conversion failed: {e}")
            # If conversion fails, return original path and hope for the best
            return audio_path
    
    def transcribe_audio(self, 
                        audio_path: str,
                        language_code: str = 'hin_Deva',
                        use_local_model: bool = True,
                        api_key: Optional[str] = None,
                        hf_token: Optional[str] = None) -> Tuple[str, str]:
        """
        Transcribe audio file and return both original and English text
        
        Args:
            audio_path: Path to the audio file
            language_code: Language code (e.g., 'hin_Deva', 'mar_Deva')
            use_local_model: Whether to use local models or SarvamAI
            api_key: SarvamAI API key (if using SarvamAI)
            hf_token: Hugging Face token (if using local models)
            
        Returns:
            Tuple of (original_text, english_text)
        """
        if not self.agri_bot_available:
            return "Voice transcription not available", "Voice transcription not available - agri_bot modules not found"
        
        try:
            # Validate language code
            if language_code not in self.LANGUAGE_MAPPINGS:
                logging.warning(f"Unknown language code: {language_code}, using Hindi as fallback")
                language_code = 'hin_Deva'
            
            # Prepare audio file
            processed_audio_path = self._prepare_audio_file(audio_path)
            
            try:
                if use_local_model:
                    # Use local models
                    self._ensure_models_loaded(use_local_model, hf_token)
                    
                    # Transcribe using AI Bharat
                    original_text = speech_to_text_bharat(
                        model=self._ai_bharat_model,
                        audio_path=processed_audio_path
                    )
                    
                    # Translate to English using IndicTrans
                    english_text = translate_indic(
                        model=self._indic_model,
                        tokenizer=self._indic_tokenizer,
                        text=[original_text],
                        audio_code=language_code
                    )[0]
                    
                else:
                    # Use SarvamAI
                    if not api_key:
                        return "SarvamAI API key required", "SarvamAI API key required for external transcription"
                    
                    english_text = speech_to_text(
                        audio_path=processed_audio_path,
                        sarvam_api=api_key
                    )
                    original_text = english_text  # SarvamAI returns English directly
                
                return original_text, english_text
                
            finally:
                # Clean up processed audio file if it's different from original
                if processed_audio_path != audio_path:
                    try:
                        os.unlink(processed_audio_path)
                    except OSError:
                        pass
                        
        except Exception as e:
            error_msg = f"Transcription error: {str(e)}"
            logging.error(error_msg)
            return error_msg, error_msg
    
    def transcribe_from_blob(self,
                           audio_blob: bytes,
                           language_code: str = 'hin_Deva',
                           use_local_model: bool = True,
                           api_key: Optional[str] = None,
                           hf_token: Optional[str] = None) -> Tuple[str, str]:
        """
        Transcribe audio from binary blob
        
        Args:
            audio_blob: Audio data as bytes
            language_code: Language code
            use_local_model: Whether to use local models
            api_key: SarvamAI API key
            hf_token: Hugging Face token
            
        Returns:
            Tuple of (original_text, english_text)
        """
        # Save blob to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_blob)
            temp_path = tmp_file.name
        
        try:
            return self.transcribe_audio(
                audio_path=temp_path,
                language_code=language_code,
                use_local_model=use_local_model,
                api_key=api_key,
                hf_token=hf_token
            )
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get dictionary of supported languages"""
        return self.LANGUAGE_MAPPINGS.copy()
    
    def is_available(self) -> bool:
        """Check if voice transcription is available"""
        return self.agri_bot_available
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name from code"""
        return self.LANGUAGE_MAPPINGS.get(language_code, {}).get('name', 'Unknown Language')


# Create a global instance for easy import
indicagri_transcriber = IndicAgriVoiceTranscriber()


def transcribe_audio_file(audio_path: str,
                         language_code: str = 'hin_Deva',
                         use_local_model: bool = True,
                         api_key: Optional[str] = None,
                         hf_token: Optional[str] = None) -> Tuple[str, str]:
    """
    Convenience function for transcribing audio files
    
    Args:
        audio_path: Path to the audio file
        language_code: Language code (e.g., 'hin_Deva')
        use_local_model: Whether to use local models
        api_key: SarvamAI API key
        hf_token: Hugging Face token
        
    Returns:
        Tuple of (original_text, english_text)
    """
    return indicagri_transcriber.transcribe_audio(
        audio_path=audio_path,
        language_code=language_code,
        use_local_model=use_local_model,
        api_key=api_key,
        hf_token=hf_token
    )


def get_supported_languages() -> Dict[str, Dict[str, str]]:
    """Get dictionary of supported languages"""
    return indicagri_transcriber.get_supported_languages()


if __name__ == '__main__':
    # Simple test
    import argparse
    
    parser = argparse.ArgumentParser(description='Test IndicAgri Voice Transcription')
    parser.add_argument('--audio', required=True, help='Path to audio file')
    parser.add_argument('--language', default='hin_Deva', help='Language code')
    parser.add_argument('--use-sarvam', action='store_true', help='Use SarvamAI instead of local models')
    parser.add_argument('--api-key', help='SarvamAI API key')
    parser.add_argument('--hf-token', help='Hugging Face token')
    
    args = parser.parse_args()
    
    transcriber = IndicAgriVoiceTranscriber()
    
    if not transcriber.is_available():
        print("Voice transcription not available - agri_bot modules not found")
        sys.exit(1)
    
    print(f"Transcribing audio: {args.audio}")
    print(f"Language: {transcriber.get_language_name(args.language)}")
    print(f"Using: {'SarvamAI' if args.use_sarvam else 'Local models'}")
    
    original, english = transcriber.transcribe_audio(
        audio_path=args.audio,
        language_code=args.language,
        use_local_model=not args.use_sarvam,
        api_key=args.api_key,
        hf_token=args.hf_token
    )
    
    print(f"\nOriginal: {original}")
    print(f"English: {english}")
