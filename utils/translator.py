from googletrans import Translator
import whisper

whisper_model = whisper.load_model("base")
translator = Translator()

def transcribe_audio(file_path):
    try:
        if not file_path.endswith(".wav"):
            return "❌ Only WAV files are supported."
        result = whisper_model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"Transcription error: {str(e)}"

def translate_text(text, target_lang):
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def get_lang_codes():
    return ["en", "hi", "fr", "de", "es", "ta", "kn"]
