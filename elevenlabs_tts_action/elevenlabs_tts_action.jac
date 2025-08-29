import logging;
import traceback;
import requests;
import uuid;
import os;
import base64;
import from typing { Iterator, Union }
import from logging { Logger }
import from elevenlabs { Voice, VoiceSettings, stream, play }
import from elevenlabs.client { ElevenLabs }
import from jivas.agent.action.tts_action { TTSAction }


node ElevenLabsTTSAction(TTSAction) {
    # A speech action which integrates with the Deepgram speech to text and text to speech API.

    # set up logger
    static has logger:Logger = logging.getLogger(__name__);

    has model:str = "eleven_turbo_v2";
    has voice:str = "Sarah";

    def invoke(text:str, as_base64:bool=False, as_url:bool=True) {
        # """
        # Convert text to speech and save the audio file using Deepgram API.

        # :param text: Text to convert to speech
        # :param base64_mode: outputs audio file as base64 encoded string
        # :return: Path to the saved audio file or base64 encoded string
        # """

        if not self.api_key {
            return None;
        }

        audio = None;
        # overridden with specifics of TTS model
        try {

            client = ElevenLabs(api_key=self.api_key); # Defaults to ELEVEN_API_KEY
            if( response := client.generate(
                text = text,
                voice = self.voice,
                model = self.model
            )) {
                # unify the byte chunks of audio data that comes back
                audio = b''.join(response);
            }

        } except Exception as e {
            self.logger.error(f"an exception occurred, {traceback.format_exc()}");
        }

        return self.get_audio_as(audio, as_base64, as_url);
    }

    def get_voices() {
        # returns all available voices
        client = ElevenLabs(api_key=self.api_key);
        if( result := client.voices.get_all() ) {
            voices = [];
            for voice in result.voices {
                voices.append({
                    "name": voice.name,
                    "voice_id": voice.voice_id,
                    "category": voice.category,
                });
            }
            return voices;
        }
        return [];
    }

    def get_models() {
        # returns all available models
        client = ElevenLabs(api_key=self.api_key);
        if( result := client.models.get_all() ) {
            models = [];
            for model in result {
                models.append({
                    "name": model.name,
                    "model_id": model.model_id,
                    "description": model.description

                });
            }
            return models;
        }
        return [];
    }

    def healthcheck() -> Union[bool, dict] {
        try {
            if(not self.api_key) {
                return {
                    "status": False,
                    "message": f"ElevenLabs API key is not set.",
                    "severity": "error"
                };
            }
            if self.get_models() {
                return True;
            }
        } except Exception as e {
            self.logger.error(f"An exception occurred in {self.label}:\n{traceback.format_exc()}\n");
            return {
                "status": False,
                "message": f"Check ElevenLabs TTS Action configuration: {e}",
                "severity": "error"
            };
        }

        return {
            "status": False,
            "message": f"ElevenLabs TTS Action API key may be incorrect or your subscription may be expired.",
            "severity": "error"
        };
    }

}