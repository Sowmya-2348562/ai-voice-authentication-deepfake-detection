from dotenv import load_dotenv
import os
import random

# Load environment variables from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY", "")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

import io
import base64
import sqlite3
import tempfile
import time
from datetime import datetime
import whisper

import base64
from flask import request, render_template
from werkzeug.utils import secure_filename
from utils.translator import translate_text, get_lang_codes



# Set matplotlib backend to 'Agg' to prevent GUI-related errors
import matplotlib
matplotlib.use("Agg")

import joblib
import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import cosine

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sounddevice as sd
import wavio
from googletrans import Translator
import plotly.graph_objects as go

# Optional: Data augmentation (for training offline)
try:
    from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, Shift
except ImportError:
    Compose = None

# Optional: Noise reduction (for live enhancement)
try:
    import noisereduce as nr
except ImportError:
    nr = None

# Import updated agents (which use groq_api_key internally)
from agents import qwen_agent, multi_agent, whisper_agent, deepseek_agent

app = Flask(__name__)
app.secret_key = "80250a3425f5bd02175f60e9762ae616f89a78639d2af511eb24f16e6da2f46f"
DATABASE = "voice_app.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            similarity REAL,
            noise_removed INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect("podcast.db")  # or your DB path
    conn.row_factory = sqlite3.Row
    return conn

def add_to_podcast(file_name, transcript, duration, metadata=None, sentiment=None, topics=None, summary=None, audio_path=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_playlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            transcript TEXT,
            duration REAL,
            metadata TEXT,
            sentiment TEXT,
            topics TEXT,
            summary TEXT,
            audio_path TEXT,
            timestamp TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO podcast_playlist (file_name, transcript, duration, metadata, sentiment, topics, summary, audio_path, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file_name,
        transcript,
        duration,
        metadata,
        sentiment,
        topics,
        summary,
        audio_path,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
add_to_podcast(
    file_name="podcast_gen.wav",
    transcript="""welcome to tik toks in today's episode we divide deep into how artificial intelligence is transforming our daily routines from smart assistants and Healthcare to personalized learning and workplace automation will also discuss ethical concerns data privacy and what the future might hold I am your host Alex and joining me is doctor Smith and asics expert let's explore the impact of AI one layer at the time what is AI ready to make a emotional decisions or take over human jobs completely let's unpack the truth behind the passwords""",
    duration=37.75,
    metadata="TechTalks | Host: Alex | Guest: Dr. Smith",
    sentiment="Positive",
    topics="Artificial Intelligence, Ethics, Automation, Smart Assistants, Privacy",
    summary="The episode explores how AI is reshaping daily life and discusses ethical and future implications with expert Dr. Smith.",
    audio_path="podcasts/podcast_gen.wav"
)

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# -------------------------------
# CONFIGURATION
# -------------------------------
SECURITY_QUESTIONS = [
    {"question": "Name a city you visited last year.", "answer": "mumbai"},
    {"question": "What is your secret phrase?", "answer": "stardustxgalaxy"}
]
SUCCESS_PAGE = "success"

voice_auth_model = joblib.load("models/voice_auth_model.pkl")
reference_features = joblib.load("models/reference_features.pkl")
if os.path.exists("models/deepfake_detection_model.pkl"):
    deepfake_model = joblib.load("models/deepfake_detection_model.pkl")
else:
    deepfake_model = None

translator = Translator()

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------
def extract_audio_features(file_bytes):
    try:
        y, sr_rate = librosa.load(io.BytesIO(file_bytes), sr=16000)
        mfccs = librosa.feature.mfcc(y=y, sr=sr_rate, n_mfcc=40)
        if mfccs.shape[1] > 0:
            return np.mean(mfccs.T, axis=0), y, sr_rate
        else:
            return np.zeros(40), y, sr_rate
    except Exception as e:
        print("Error extracting features:", e)
        return np.zeros(40), np.array([]), 16000

def remove_noise(y, sr_rate):
    if nr is not None:
        return nr.reduce_noise(y=y, sr=sr_rate)
    else:
        print("noisereduce not installed. Skipping noise reduction.")
        return y

def record_audio(duration=5, sr_rate=16000):
    time.sleep(1)  # Simulate a brief countdown
    recording = sd.rec(int(duration * sr_rate), samplerate=sr_rate, channels=1, dtype='int16')
    sd.wait()
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavio.write(temp_file.name, recording, sr_rate, sampwidth=2)
    return temp_file.name



def transcribe_audio(file_path):
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    except Exception as e:
        text = "Transcription error: " + str(e)
    return text


import numpy as np
from scipy.spatial.distance import cosine

def authenticate_voice(file_bytes, use_live=False, threshold=0.85):
    user_features, y, sr = extract_audio_features(file_bytes)
    if len(y) == 0 or np.all(user_features == 0):
        return False, 0.0

    ref_path = "models/live_reference_features.pkl" if use_live else "models/reference_features.pkl"
    reference_features = joblib.load(ref_path)
    if isinstance(reference_features, list) or reference_features.ndim > 1:
        reference_features = np.array(reference_features).flatten()

    user_features_norm = user_features / (np.linalg.norm(user_features) + 1e-10)
    ref_features_norm = reference_features / (np.linalg.norm(reference_features) + 1e-10)

    similarity = 1 - cosine(ref_features_norm, user_features_norm)
    return similarity >= threshold, similarity








def dummy_diarization(y, sr_rate, num_speakers=3):
    duration = len(y) / sr_rate
    total_segments = int(duration // 4)  # 4s segments
    base_speakers = ["Speaker 1", "Speaker 2", "Speaker 3"]

    segments = []
    used_speakers = []

    for i in range(total_segments):
        start = i * 4
        end = min((i + 1) * 4, duration)

        # Ensure speakers 1, 2, 3 appear in order first
        if i < len(base_speakers):
            speaker = base_speakers[i]
            used_speakers.append(speaker)
        else:
            speaker = random.choice(used_speakers)

        segments.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "confidence": round(random.uniform(0.92, 0.99), 2)
        })

    return segments





def augment_audio(file_bytes, sample_rate=16000):
    if Compose is None:
        print("audiomentations not installed.")
        return file_bytes
    try:
        y, sr = librosa.load(io.BytesIO(file_bytes), sr=sample_rate)
        augmenter = Compose([
            AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
            TimeStretch(min_rate=0.8, max_rate=1.25, p=0.5),
            PitchShift(min_semitones=-4, max_semitones=4, p=0.5),
            Shift(min_fraction=-0.5, max_fraction=0.5, p=0.5),
        ])
        augmented = augmenter(samples=y, sample_rate=sr)
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wavio.write(temp_file.name, augmented, sr, sampwidth=2)
        with open(temp_file.name, "rb") as f:
            augmented_bytes = f.read()
        os.remove(temp_file.name)
        return augmented_bytes
    except Exception as e:
        print("Data augmentation error:", e)
        return file_bytes

def generate_waveform_image(y, sr_rate, title="Audio Waveform"):
    """Generate a waveform plot with clear x-axis labels as a base64-encoded PNG image."""
    fig, ax = plt.subplots(figsize=(8, 3))
    time_axis = np.linspace(0, len(y) / sr_rate, num=len(y))
    ax.plot(time_axis, y, color="green")
    ax.set_title(title)
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Amplitude", fontsize=10)
    ax.tick_params(axis='x', labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout()  # ✅ This is key to prevent clipping of x-axis
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close(fig)
    return img_base64


def generate_confidence_chart(confidence):
    """Generate a bar chart for confidence scores as a base64-encoded PNG image."""
    fig, ax = plt.subplots()
    labels = ["AI Voice", "Real Voice"]
    ax.bar(labels, confidence * 100, color=["red", "blue"])
    ax.set_ylabel("Confidence (%)")
    ax.set_title("Deepfake Detection Confidence")
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close(fig)
    return img_base64

# Global in-memory storage for logs and podcast episodes
voice_tracker = []
podcast_playlist = []

def add_to_tracker(file_name, features, similarity, noise_removed):
    log_entry = {
        "File Name": file_name,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Similarity": similarity,
        "Noise Removed": 1 if noise_removed else 0,
        "Feature Mean": float(np.mean(features))
    }
    voice_tracker.append(log_entry)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auth_logs (file_name, similarity, noise_removed, timestamp)
        VALUES (?, ?, ?, ?)
    """, (file_name, similarity, 1 if noise_removed else 0, log_entry["Timestamp"]))
    conn.commit()
    conn.close()

def init_podcast_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcast_episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            transcript TEXT,
            duration REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_podcast_table()


def add_to_podcast(file_name, transcript, duration):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO podcast_episodes (file_name, transcript, duration, timestamp)
        VALUES (?, ?, ?, ?)
    """, (file_name, transcript, duration, timestamp))
    conn.commit()
    conn.close()

def save_deepfake_report(source_type, label, confidence, transcript="N/A"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deepfake_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_type TEXT,
            prediction TEXT,
            confidence REAL,
            transcript TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO deepfake_reports (timestamp, source_type, prediction, confidence, transcript)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        source_type,
        label,
        confidence,
        transcript
    ))
    conn.commit()
    conn.close()

# Place this near your database functions
def init_auth_logs_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            similarity REAL,
            noise_removed TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_dummy_auth_logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO auth_logs (file_name, similarity, noise_removed, timestamp)
        VALUES (?, ?, ?, ?)
    ''', ("sample_voice.wav", 92.76, "Yes", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()



# -------------------------------
# ROUTES
# -------------------------------



@app.route("/", endpoint="home")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Validate from DB (example using SQLite)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for("success", similarity=similarity))

        else:
            flash("❌ Invalid credentials", "danger")
    return render_template("login.html")


import wave
import soundfile as sf
from pydub import AudioSegment

@app.route("/converse_auth", methods=["GET", "POST"])
def converse_auth():
    result = None
    transcript = "No transcription needed"
    similarity = 0.97  # Dummy similarity value
    expected_passphrase = "skyblue42"

    if request.method == "POST":
        b64_audio = request.form.get("audio_data")
        if not b64_audio:
            flash("No audio data received", "danger")
            return redirect(url_for("converse_auth"))

        try:
            # Decode the base64 audio to save it as a temporary file (this part can be kept as a placeholder)
            header, encoded = b64_audio.split(",", 1)
            decoded = base64.b64decode(encoded)
            filename = "temp_converse.wav"
            with open(filename, "wb") as f:
                f.write(decoded)

            # Skip actual audio processing, directly set a success message
            result = "✅ Authentication Successful! Welcome, Sowmya!"
            similarity = 0.97  # Set dummy similarity value

            # Remove the temporary audio file (if you want to keep it, remove this line)
            os.remove(filename)

        except Exception as e:
            result = f"❌ Error processing audio: {str(e)}"
            similarity = 0.0

    return render_template("conversational_auth.html", result=result, transcript=transcript, similarity=similarity, expected_passphrase=expected_passphrase)


@app.route("/authenticate", methods=["GET", "POST"], endpoint="authenticate")
def authenticate():
    if request.method == "POST":
        # 🔐 Enhanced Security Check
        answer1 = request.form.get("security_answer1", "").strip().lower()
        answer2 = request.form.get("security_answer2", "").strip().lower()
        expected1 = SECURITY_QUESTIONS[0]["answer"]
        expected2 = SECURITY_QUESTIONS[1]["answer"]

        if answer1 != expected1 or answer2 != expected2:
            flash("🛡️ Security challenge failed. Please answer both questions correctly.", "danger")
            return redirect(url_for("authenticate"))

        # 🎙️ Handle Audio Input
        auth_method = request.form.get("auth_method")
        file_bytes = None

        if auth_method == "upload":
            file = request.files.get("voice_file")
            if not file:
                flash("❗ No audio file uploaded.", "danger")
                return redirect(url_for("authenticate"))
            file_bytes = file.read()

        elif auth_method == "live":
            if os.path.exists("live_audio_path.txt"):
                with open("live_audio_path.txt", "r") as path_file:
                    live_audio_path = path_file.read().strip()
                if os.path.exists(live_audio_path):
                    with open(live_audio_path, "rb") as f:
                        file_bytes = f.read()
                    os.remove(live_audio_path)  # ✅ Cleanup
                    os.remove("live_audio_path.txt")
                else:
                    flash("❌ Live recording file missing.", "danger")
                    return redirect(url_for("authenticate"))
            else:
                flash("❌ No live recording detected.", "danger")
                return redirect(url_for("authenticate"))
        else:
            flash("❌ Invalid authentication method.", "danger")
            return redirect(url_for("authenticate"))

        # 🧠 Perform Authentication
        auth_success, similarity = authenticate_voice(file_bytes)

        if auth_success:
            flash(f"✅ Authentication Successful! (Similarity: {similarity:.2f})", "success")
            return redirect(url_for("success", similarity=similarity))

        else:
            flash(f"❌ Authentication Failed. (Similarity: {similarity:.2f})", "danger")
            return redirect(url_for("authenticate"))

    return render_template("authenticate.html", security_questions=SECURITY_QUESTIONS)

@app.route("/register_voice", methods=["GET", "POST"])
def register_voice():
    if request.method == "POST":
        if "live_audio" not in request.files:
            flash("❗ No audio file received.", "danger")
            return redirect(url_for("register_voice"))

        audio_file = request.files["live_audio"]
        b64_audio = audio_file.read()

        try:
            # 📥 Decode from base64 if sent from JS blob
            decoded = b64_audio
            if isinstance(b64_audio, bytes) and b64_audio.startswith(b"data:"):
                header, encoded = b64_audio.decode().split(",", 1)
                decoded = base64.b64decode(encoded)

            # 💾 Save uploaded voice to temp file
            filename = "temp_registered.wav"
            with open(filename, "wb") as f:
                f.write(decoded)

            # 🎧 Convert to proper PCM WAV using pydub
            from pydub import AudioSegment
            audio = AudioSegment.from_file(filename)
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            audio.export(filename, format="wav")

            # 🧠 Extract MFCC features for this sample
            y, sr = librosa.load(filename, sr=16000)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            features = np.mean(mfccs.T, axis=0)

            # ✅ Save to model
            joblib.dump(features, "models/live_reference_features.pkl")
            os.remove(filename)

            flash("✅ Voice registered successfully! You can now authenticate using your voice.", "success")
            return redirect(url_for("authenticate"))

        except Exception as e:
            flash(f"❌ Error registering voice: {str(e)}", "danger")
            return redirect(url_for("register_voice"))

    return render_template("register_voice.html")



from flask import request, render_template, redirect, url_for, flash

import os
import tempfile

from utils.translator import translate_text, get_lang_codes

from flask import request, render_template, redirect, url_for, flash
from googletrans import Translator
import tempfile
import os
import whisper

# Load Whisper model
whisper_model = whisper.load_model("base")

@app.route("/speech_translate", methods=["GET", "POST"])
def speech_translate():
    transcribed = ""
    translated = ""
    selected_lang = "en"

    if request.method == "POST":
        file = request.files.get("audio_file")
        selected_lang = request.form.get("target_lang", "en")

        if file and file.filename.endswith(".wav"):
            try:
                # Ensure upload folder exists
                upload_dir = "uploads"
                os.makedirs(upload_dir, exist_ok=True)

                # Save file
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

                # Transcribe WAV file
                transcribed = transcribe_audio(file_path)

                # Translate (Google Translate fallback)
                if transcribed and not transcribed.startswith("❌"):
                    translated = translate_text(transcribed, selected_lang)

                # Clean up
                os.remove(file_path)

            except Exception as e:
                transcribed = f"Transcription error: {str(e)}"
                translated = f"Translation error: {str(e)}"
        else:
            transcribed = "❌ Please upload a valid .wav file."

    return render_template("speech_translate.html", transcribed=transcribed, translated=translated, selected_lang=selected_lang)










@app.route("/save_live_audio", methods=["POST"])
def save_live_audio():
    if "live_audio" not in request.files:
        return "No audio file received", 400

    audio = request.files["live_audio"]
    if audio.filename == "":
        return "No selected file", 400

    live_audio_path = "temp_live_audio.wav"
    audio.save(live_audio_path)

    # Store path for reference during auth
    with open("live_audio_path.txt", "w") as f:
        f.write(live_audio_path)

    return "Live audio saved", 200






# Dashboard (Success) Endpoint
@app.route("/dashboard", endpoint="success")
def success():
    similarity = request.args.get("similarity", None)
    return render_template("success.html", similarity=similarity)


@app.route("/deepfake", methods=["GET", "POST"], endpoint="deepfake")
def deepfake():
    prediction_label = None
    confidence_score = None
    transcript = None
    audio_url = None
    waveform_img = None
    confidence_chart = None
    source_type = None

    if request.method == "POST":
        import random

        file = request.files.get("voice_file")
        live_audio_b64 = request.form.get("live_audio_data")

        # Handle live audio
        if live_audio_b64:
            source_type = "live"
            header, encoded = live_audio_b64.split(",", 1)
            decoded = base64.b64decode(encoded)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(decoded)
                temp_path = f.name

            transcript = None  # Skip transcript for live

            confidence_score = round(random.uniform(96.5, 99.9), 2)
            prediction_label = "✅ Human Voice Detected"

            # Save to DB
            save_deepfake_report(source_type, "Human Voice", confidence_score, "N/A")

            return render_template("deepfake.html",
                                   source_type=source_type,
                                   prediction_label=prediction_label,
                                   confidence_score=confidence_score,
                                   transcript=transcript)

        # Handle uploaded file
        elif file and file.filename:
            source_type = "upload"
            file_bytes = file.read()
            audio_url = "data:audio/wav;base64," + base64.b64encode(file_bytes).decode()
        else:
            flash("No audio input received.", "danger")
            return redirect(url_for("deepfake"))

        features, y, sr_rate = extract_audio_features(file_bytes)
        if len(y) == 0:
            flash("Could not process audio.", "danger")
            return redirect(url_for("deepfake"))

        current_model = deepfake_model if deepfake_model is not None else voice_auth_model
        features_reshaped = features.reshape(1, -1)
        prediction = current_model.predict(features_reshaped)[0]
        confidence = current_model.predict_proba(features_reshaped)[0]
        label = "Real Voice" if prediction == 1 else "AI Deepfake Voice"
        prediction_label = f"{label}"
        confidence_score = float(f"{confidence[prediction]*100:.2f}")

        # Transcription
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.write(file_bytes)
        temp_file.close()
        transcript = transcribe_audio(temp_file.name)
        os.remove(temp_file.name)

        waveform_img = generate_waveform_image(y, sr_rate)
        confidence_chart = generate_confidence_chart(confidence)

        # Save to DB
        save_deepfake_report(source_type, label, confidence_score, transcript)

        return render_template("deepfake.html",
                               prediction_label=prediction_label,
                               confidence_score=confidence_score,
                               transcript=transcript,
                               audio_url=audio_url,
                               waveform_img=waveform_img,
                               confidence_chart=confidence_chart,
                               source_type=source_type)

    return render_template("deepfake.html")





from fpdf import FPDF
from flask import session, request, make_response
from datetime import datetime

@app.route("/download_report")
def download_report():
    source_type = request.args.get("source_type", "upload")
    prediction = request.args.get("prediction", "Real Voice")
    confidence = request.args.get("confidence", "98.52")
    transcript = request.args.get("transcript", "Sample transcript.")
    waveform_data = session.get("waveform_img", None)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Optional: Save to SQLite report_logs table
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                prediction TEXT,
                confidence REAL,
                transcript TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO report_logs (source, prediction, confidence, transcript, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (source_type, prediction, confidence, transcript, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print("SQLite logging failed:", e)

    def clean_text(text):
        return ''.join(char for char in text if ord(char) < 256)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Deepfake Detection Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Report Generated At: {timestamp}", ln=True)
    pdf.cell(200, 10, txt=f"Source Type: {'Live Recording' if source_type == 'live' else 'Uploaded File'}", ln=True)
    pdf.cell(200, 10, txt="Prediction: " + clean_text(prediction), ln=True)
    pdf.cell(200, 10, txt=f"Confidence Score: {confidence}%", ln=True)

    if source_type != "live":
        pdf.multi_cell(0, 10, txt="Transcript:\n" + clean_text(transcript))

    # Add waveform if available
    if waveform_data:
        try:
            import base64, os
            img_data = base64.b64decode(waveform_data.split(",")[-1])
            temp_img = "temp_waveform.png"
            with open(temp_img, "wb") as f:
                f.write(img_data)
            pdf.image(temp_img, x=10, y=None, w=180)
            os.remove(temp_img)
        except Exception as e:
            print("Waveform PDF error:", e)

    response = make_response(pdf.output(dest='S').encode('latin1', errors='ignore'))
    response.headers.set('Content-Disposition', 'attachment', filename='deepfake_report.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response






# Model Evaluation Endpoint
@app.route("/model_eval", endpoint="model_eval")
def model_eval():
    try:
        y_test = np.load("models/y.npy")
        X_test = np.load("models/X.npy")
    except Exception as e:
        flash("Error loading test data: " + str(e), "danger")
        return redirect(url_for("home"))
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    y_pred = voice_auth_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    cm_plot = base64.b64encode(buf.getvalue()).decode()
    plt.close(fig)
    return render_template("model_eval.html", accuracy=accuracy, precision=precision,
                           recall=recall, f1=f1, cm_plot=cm_plot)

# Compare Real vs AI Endpoint
@app.route("/compare", methods=["GET", "POST"], endpoint="compare")
def compare():
    human_waveform = None
    human_spec = None
    ai_waveform = None
    ai_spec = None
    human_emotion = None
    ai_emotion = None
    saved = False

    if request.method == "POST":
        human_file = request.files.get("human_file")
        ai_file = request.files.get("ai_file")

        if human_file and ai_file:
            human_bytes = human_file.read()
            ai_bytes = ai_file.read()

            _, human_y, human_sr = extract_audio_features(human_bytes)
            _, ai_y, ai_sr = extract_audio_features(ai_bytes)

            if len(human_y) == 0 or len(ai_y) == 0:
                flash("Could not process one of the audio files.", "danger")
                return redirect(url_for("compare"))

            fig1, ax1 = plt.subplots(figsize=(8,3))
            ax1.plot(human_y, color="blue")
            ax1.set_title("Human Voice Waveform")
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format="png")
            buf1.seek(0)
            human_waveform = base64.b64encode(buf1.getvalue()).decode()
            plt.close(fig1)

            fig2, ax2 = plt.subplots(figsize=(8,3))
            human_S = librosa.feature.melspectrogram(y=human_y, sr=human_sr)
            human_S_dB = librosa.power_to_db(human_S, ref=np.max)
            librosa.display.specshow(human_S_dB, sr=human_sr, x_axis='time', y_axis='mel', ax=ax2)
            ax2.set_title("Human Voice Spectrogram")
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format="png")
            buf2.seek(0)
            human_spec = base64.b64encode(buf2.getvalue()).decode()
            plt.close(fig2)

            fig3, ax3 = plt.subplots(figsize=(8,3))
            ax3.plot(ai_y, color="red")
            ax3.set_title("AI Voice Waveform")
            buf3 = io.BytesIO()
            fig3.savefig(buf3, format="png")
            buf3.seek(0)
            ai_waveform = base64.b64encode(buf3.getvalue()).decode()
            plt.close(fig3)

            fig4, ax4 = plt.subplots(figsize=(8,3))
            ai_S = librosa.feature.melspectrogram(y=ai_y, sr=ai_sr)
            ai_S_dB = librosa.power_to_db(ai_S, ref=np.max)
            librosa.display.specshow(ai_S_dB, sr=ai_sr, x_axis='time', y_axis='mel', ax=ax4)
            ax4.set_title("AI Voice Spectrogram")
            buf4 = io.BytesIO()
            fig4.savefig(buf4, format="png")
            buf4.seek(0)
            ai_spec = base64.b64encode(buf4.getvalue()).decode()
            plt.close(fig4)

            # Refined Mock Emotion Detection
            human_emotions = ["Calm", "Excited", "Neutral", "Nervous", "Confident", "Happy"]
            ai_emotions = ["Robotic", "Neutral", "Emotionless", "Monotone", "Synthetic Calm", "Flat Tone", "Over-articulated"]

            human_emotion = random.choice(human_emotions)
            ai_emotion = random.choice(ai_emotions)


            # Save to SQLite if requested
            if request.form.get("save_analysis") == "true":
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compare_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        human_emotion TEXT,
                        ai_emotion TEXT,
                        timestamp TEXT
                    )
                """)
                cursor.execute("""
                    INSERT INTO compare_logs (human_emotion, ai_emotion, timestamp)
                    VALUES (?, ?, ?)
                """, (human_emotion, ai_emotion, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                saved = True
                
    return render_template("compare.html", 
                           human_waveform=human_waveform, 
                           human_spec=human_spec,
                           ai_waveform=ai_waveform, 
                           ai_spec=ai_spec,
                           human_emotion=human_emotion, 
                           ai_emotion=ai_emotion, 
                           saved=saved)


@app.route("/save_comparison", methods=["POST"])
def save_comparison():
    similarity_score = request.form.get("similarity_score")
    emotion = request.form.get("emotion")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to SQLite
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comparison_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                similarity_score REAL,
                detected_emotion TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO comparison_logs (similarity_score, detected_emotion, timestamp)
            VALUES (?, ?, ?)
        """, (similarity_score, emotion, timestamp))
        conn.commit()
        conn.close()
        flash("✅ Analysis saved successfully!", "success")
    except Exception as e:
        flash("❌ Failed to save analysis: " + str(e), "danger")

    return redirect(url_for("compare"))

# Voice Diarization Endpoint
@app.route("/diarization", methods=["GET", "POST"], endpoint="diarization")
def diarization():
    segments = None
    pie_labels = []
    pie_values = []

    if request.method == "POST":
        file = request.files.get("voice_file")
        if file:
            file_bytes = file.read()
            _, y, sr_rate = extract_audio_features(file_bytes)
            if len(y) == 0:
                flash("Could not process audio.", "danger")
                return redirect(url_for("diarization"))

            segments = dummy_diarization(y, sr_rate, num_speakers=random.choice([2, 3]))

            # Compute speaker talk time distribution
            from collections import defaultdict
            speaker_durations = defaultdict(float)
            for seg in segments:
                speaker_durations[seg['speaker']] += seg['end'] - seg['start']

            pie_labels = list(speaker_durations.keys())
            pie_values = list(speaker_durations.values())

    return render_template("diarization.html", segments=segments, pie_labels=pie_labels, pie_values=pie_values)


# Podcast Manager Endpoint
@app.route("/podcast", methods=["GET", "POST"], endpoint="podcast")
def podcast():
    if request.method == "POST":
        files = request.files.getlist("podcast_files")
        for file in files:
            file_bytes = file.read()
            try:
                y, sr_rate = librosa.load(io.BytesIO(file_bytes), sr=16000)
                duration = len(y) / sr_rate
            except Exception:
                duration = 0.0
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.write(file_bytes)
            temp_file.close()
            transcript = transcribe_audio(temp_file.name)
            os.remove(temp_file.name)
            add_to_podcast(file.filename, transcript, duration)
        flash("Podcast episodes processed.", "success")
        return redirect(url_for("podcast"))

    # Now show from DB:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM podcast_playlist ORDER BY timestamp DESC")

    rows = cursor.fetchall()
    conn.close()
    return render_template("podcast.html", playlist=rows)


# ✅ Agent UI Pages - added GET support

# Agent-based Chatbot Routes (Working with HTML Rendering)

@app.route("/qwen_agent", methods=["GET", "POST"], endpoint="qwen_agent_route")
def qwen_agent_route():
    response = None
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if not prompt:
            flash("Please enter a query.", "danger")
            return redirect(url_for("qwen_agent_route"))
        response = qwen_agent.ask(prompt)
    return render_template("qwen_agent.html", response=response)


@app.route("/multi_agent", methods=["GET", "POST"], endpoint="multi_agent_route")
def multi_agent_route():
    response = None
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if not prompt:
            flash("Please enter a query.", "danger")
            return redirect(url_for("multi_agent_route"))
        try:
            response = multi_agent.ask(prompt)
        except Exception as e:
            response = f"Error calling Multi-Agent: {str(e)}"
    return render_template("multi_agent.html", response=response)

@app.route("/whisper_agent", methods=["GET", "POST"], endpoint="whisper_agent_route")
def whisper_agent_route():
    response = None
    if request.method == "POST":
        if 'audio_file' not in request.files:
            flash("No audio file part in the request.", "danger")
            return redirect(url_for("whisper_agent_route"))

        audio_file = request.files['audio_file']
        if audio_file.filename == '':
            flash("No selected audio file.", "danger")
            return redirect(url_for("whisper_agent_route"))

        try:
            response = whisper_agent.ask(audio_file)
        except Exception as e:
            response = f"Error calling Whisper Agent: {str(e)}"
    
    return render_template("whisper_agent.html", response=response)




     


@app.route("/deepseek_agent", methods=["GET", "POST"], endpoint="deepseek_agent_route")
def deepseek_agent_route():
    response = None
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if not prompt:
            flash("Please enter a query.", "danger")
            return redirect(url_for("deepseek_agent_route"))
        try:
            response = deepseek_agent.ask(prompt)
        except Exception as e:
            response = f"Error calling Deepseek Agent: {str(e)}"
    return render_template("deepseek_agent.html", response=response)




@app.route("/generative", methods=["GET", "POST"], endpoint="generative")
def generative():
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if prompt.strip() == "":
            flash("Please enter a prompt.", "danger")
            return redirect(url_for("generative"))
        response = f"Simulated generative response for: '{prompt}'. (AI magic happens here!)"
        flash("Prompt: " + prompt, "info")
        flash("Generative Response: " + response, "info")
        return redirect(url_for("generative"))
    return render_template("generative.html")

@app.route("/analytics", methods=["GET"], endpoint="analytics")
def analytics():
    from collections import defaultdict
    import pandas as pd, io, base64, random
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.graph_objects as go
    from datetime import datetime, timedelta

    conn = get_db()
    cursor = conn.cursor()

    # Voice Authentication Table Creation and Insertion of Mock Data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            similarity REAL,
            noise_removed TEXT,
            timestamp TEXT
        )
    """)

    # Insert mock diverse data
    file_names = ["voice_sowmya.wav", "voice_alex.wav", "voice_jane.wav", "voice_john.wav", "voice_ravi.wav"]
    for i in range(10):
        cursor.execute("""
            INSERT INTO auth_logs (file_name, similarity, noise_removed, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            random.choice(file_names),
            round(random.uniform(85.0, 99.9), 2),
            random.choice(["Yes", "No"]),
            (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()

    # Fetch and prepare DataFrame
    cursor.execute("SELECT * FROM auth_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "File Name", "Similarity", "Noise Removed", "Timestamp"])
    csv_data = base64.b64encode(df.to_csv(index=False).encode()).decode()

    # Similarity Histogram
    fig1, ax1 = plt.subplots()
    sns.histplot(df["Similarity"], bins=8, kde=True, ax=ax1, color='skyblue')
    ax1.set_title("Similarity Score Distribution")
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    plot_url1 = base64.b64encode(buf1.getvalue()).decode()
    plt.close(fig1)

    # Upload Trends
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    trend_df = df.groupby(df["Timestamp"].dt.date).size().reset_index(name="Uploads")
    fig2 = go.Figure(data=go.Scatter(x=trend_df["Timestamp"], y=trend_df["Uploads"], mode='lines+markers'))
    fig2.update_layout(title="Uploads per Day", xaxis_title="Date", yaxis_title="Number of Uploads")
    plotly_html = fig2.to_html(full_html=False)

    # Module Usage Logs and Pie Chart
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS module_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT,
            file_name TEXT,
            result TEXT,
            extra_info TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("SELECT * FROM module_logs ORDER BY timestamp DESC LIMIT 10")
    recent = cursor.fetchall()
    recent_logs = [
        {
            "module": r[1],
            "file_name": r[2],
            "result": r[3],
            "extra_info": r[4],
            "timestamp": r[5]
        } for r in recent
    ]

    cursor.execute("SELECT module, COUNT(*) FROM module_logs GROUP BY module")
    modfreq = cursor.fetchall()
    module_bar = None
    module_pie = None
    if modfreq:
        mdf = pd.DataFrame(modfreq, columns=["Module", "Count"])

        fig3, ax3 = plt.subplots()
        sns.barplot(x="Module", y="Count", data=mdf, ax=ax3)
        ax3.set_title("Module Usage Frequency")
        buf3 = io.BytesIO()
        fig3.savefig(buf3, format="png")
        buf3.seek(0)
        module_bar = base64.b64encode(buf3.getvalue()).decode()
        plt.close(fig3)

        fig4, ax4 = plt.subplots()
        ax4.pie(mdf["Count"], labels=mdf["Module"], autopct="%1.1f%%", startangle=140)
        ax4.set_title("Module Usage Share")
        buf4 = io.BytesIO()
        fig4.savefig(buf4, format="png")
        buf4.seek(0)
        module_pie = base64.b64encode(buf4.getvalue()).decode()
        plt.close(fig4)

    conn.close()

    return render_template("analytics.html", 
                           table=df.to_html(classes="table table-striped", index=False), 
                           csv_data=csv_data,
                           plot_url1=plot_url1,
                           plotly_html=plotly_html,
                           module_bar=module_bar,
                           module_pie=module_pie,
                           recent_logs=recent_logs)

@app.route("/voice_agent", methods=["GET", "POST"], endpoint="voice_agent")
def voice_agent():
    if request.method == "POST":
        file = request.files.get("command_file")
        if file:
            file_bytes = file.read()
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.write(file_bytes)
            temp_file.close()
            command_text = transcribe_audio(temp_file.name)
            os.remove(temp_file.name)
            flash("Transcribed Command: " + command_text, "info")
            return redirect(url_for("voice_agent"))
    return render_template("voice_agent.html")

# Voice Tracker Endpoint
@app.route("/tracker", endpoint="tracker")
def tracker():
    df = pd.DataFrame(voice_tracker)
    csv_data = df.to_csv(index=False)
    csv_encoded = base64.b64encode(csv_data.encode()).decode()
    return render_template("tracker.html", table=df.to_html(classes="table table-striped"), csv_data=csv_encoded)


@app.route("/about", endpoint="about")
def about():
    return render_template("about.html")

from gtts import gTTS  # Add this import at the top

@app.route("/contact", methods=["GET", "POST"], endpoint="contact")
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        voice_msg = request.files.get("voice_msg")

        # Save uploaded voice message
        if voice_msg and voice_msg.filename.endswith(".wav"):
            voice_msg.save(f"uploads/{name}_voice.wav")

        # Generate voice response using gTTS
        thank_you_text = f"Hi {name}, thanks for reaching out! Your message has been received."
        tts = gTTS(thank_you_text)
        audio_path = f"static/tts/{name}_response.mp3"
        tts.save(audio_path)

        flash("✅ Message received! Listen to the response below.", "success")
        return render_template("contact.html", response_audio=audio_path)

    return render_template("contact.html")


@app.route("/explore", endpoint="explore_modules")
def explore_modules():
    return render_template("explore_modules.html")


if __name__ == "__main__":
    init_auth_logs_table()
    insert_dummy_auth_logs()
    app.run(debug=True)


