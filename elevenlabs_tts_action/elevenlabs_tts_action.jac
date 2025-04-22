import:py logging;
import:py traceback;
import:py requests;
import:py uuid;
import:py os;
import:py base64;
import:py from typing { Iterator }
import:py from logging { Logger }
import:py from elevenlabs { Voice, VoiceSettings, stream, play }
import:py from elevenlabs.client { ElevenLabs }
import:jac from jivas.agent.action.tts_action { TTSAction }


node ElevenlabsTTSAction :TTSAction: {
    # A speech action which integrates with the Deepgram speech to text and text to speech API.

    # set up logger
    static has logger:Logger = logging.getLogger(__name__);

    has model:str = "eleven_turbo_v2";
    has voice:str = "IRIS";

    can invoke(text:str, as_base64:bool=False, as_url:bool=True) {
        # """
        # Convert text to speech and save the audio file using Deepgram API.

        # :param text: Text to convert to speech
        # :param base64_mode: outputs audio file as base64 encoded string
        # :return: Path to the saved audio file or base64 encoded string
        # """
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

    can get_voices() {
        # returns all available voices
        client = ElevenLabs(api_key=self.api_key);
        if( result := client.voices.get_all() ) {
            return result;
        }
        return [];
    }

    can get_models() {
        # returns all available models
        client = ElevenLabs(api_key=self.api_key);
        if( result := client.models.get_all() ) {
            return result;
        }
        return [];
    }

    can healthcheck() -> bool {
        try {
            if(self.model and self.api_key and self.voice){
                return True;
            }
            return False;
        } except Exception as e {
            self.logger.error(f"An exception occurred in {self.label}:\n{traceback.format_exc()}\n");
            return False;
        }
    }

}