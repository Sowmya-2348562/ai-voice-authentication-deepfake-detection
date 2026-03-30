# 🎙️ AI Voice Authentication & Deepfake Detection System

🚀 **Secure | Intelligent | Real-Time Voice AI Platform**

---

## 📌 Overview

This project is an advanced AI-powered system that enables **secure voice-based authentication** and **deepfake audio detection**, enhanced with **speaker intelligence, conversational verification, and multi-agent AI capabilities**.

With the rapid rise of synthetic voices, this system ensures **trustworthy identity verification** using cutting-edge machine learning and audio processing techniques.

---

## 🧠 Model Architecture

The system supports multiple model architectures for robust performance:

- 🌲 Random Forest (baseline model)
- 🔁 LSTM models for sequential audio feature learning
- 🧱 CNN models for spatial feature extraction
- 🔗 CNN-LSTM hybrid models for combined spatio-temporal learning

Each model is exposed via dedicated API endpoints for modular and scalable inference.

---

## 🔌 API Endpoints

The system provides multiple REST API endpoints for model inference:

| Endpoint | Model |
|----------|-------|
| `/predict_rf` | Random Forest |
| `/predict_lstm_csv` | LSTM |
| `/predict_cnn_combined` | CNN |
| `/predict_cnn_lstm_combined` | Hybrid CNN-LSTM |

Each endpoint returns:
- Prediction (Real / Deepfake)
- Confidence score
- Timestamp

---

## 🔥 Key Features

### 🔐 Voice Authentication
- MFCC-based speaker verification
- Cosine similarity matching
- Upload & live voice authentication

### 🧠 Speaker Intelligence
- Unique voice feature extraction
- Personalized voice profile storage
- Voice similarity scoring

### 🗣️ Conversational Authentication
- Natural user interaction with passphrase
- Speech-to-Text based verification

### 🎭 Deepfake Detection
- Detects AI-generated vs real human voice
- Uses multiple machine learning and deep learning models:
  - Random Forest (baseline)
  - LSTM-based models (temporal learning)
  - CNN-based models (feature extraction)
  - Hybrid CNN-LSTM models (spatio-temporal learning)
- Confidence score prediction
- Waveform & spectrogram visualization

### 🌍 Speech Translation
- Converts speech to text
- Multi-language translation support

### 🤖 Multi-Agent AI System
- Qwen Agent
- Whisper Agent
- DeepSeek Agent
- Multi-Agent reasoning system

### 📊 Analytics Dashboard
- Authentication logs
- Usage trends
- Model performance metrics

### 🎧 Additional Features
- Speaker diarization
- Podcast generation & management
- Emotion simulation
- Voice command agent

---

## 🏗️ System Architecture
```
🎙️ Voice Input (Upload / Live Recording)
        ↓
🧹 Audio Preprocessing (Noise Reduction)
        ↓
📊 Feature Extraction (MFCC)
        ↓
🔍 Speaker Verification (Cosine Similarity)
        ↓
🎭 Deepfake Detection Model
        ↓
📈 Visualization & Results Dashboard
```

---

## 🧰 Tech Stack

| Category | Tools |
|----------|-------|
| Backend | Python, Flask |
| Audio Processing | Librosa, Whisper |
| Machine Learning | Scikit-learn, NumPy, Pandas |
| Deep Learning | TensorFlow, Keras |
| Visualization | Plotly, Matplotlib |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| TTS | gTTS |

---

## 📁 Project Structure
```
ai-voice-authentication-deepfake-detection/
│
├── app.py
├── agents.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
├── static/
├── utils/
└── models/
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection.git
cd ai-voice-authentication-deepfake-detection
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
```

Activate:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables
Create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

### 5️⃣ Run the Application
```bash
python app.py
```

---

## 📸 Screenshots

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Voice.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20023326.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20175704.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180135.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180148.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20182453.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180155.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180211.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180222.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180230.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180258.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180320.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180343.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180352.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180401.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180409.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180417.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180454.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20180510.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20182516.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20182531.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20182545.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20182606.png)

![Screenshot](https://raw.githubusercontent.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection/main/assets/Screenshot%202026-03-30%20184004.png)

---

## ⚠️ Important Notes

- `.env` file is not included for security reasons
- Large model files may not be included in the repository
- Some features require external API keys

---

## 💡 Use Cases

- 🔐 Secure login using voice biometrics
- 🏦 Fraud detection in banking & finance
- 🎙️ Deepfake voice detection for media verification
- 🧑‍💻 Identity verification in remote systems
- 🌍 Multilingual voice-based applications

---
## Model Comparison and Final Remarks
Based on the evaluation metrics, confusion matrices, and training curves:
• Best Performing Model: CNN-LSTM (Combined Dataset) – demonstrated
superior accuracy, stable training, and minimal misclassifications, making it ideal
for real-world deployment.
• Close Second: LSTM (Combined) – effectively models temporal dependencies
and performs well, though with slightly higher validation loss and fluctuations.
• Best Classical Model: Random Forest – performed competitively on CSV
features, offering a fast and interpretable baseline.
• Least Effective: 1D CNN – showed signs of overfitting and had limited ability
to capture temporal features in audio data.
Thus, the CNN-LSTM hybrid model was chosen as the final deployment model due to
its strong generalization, high accuracy, and robustness across diverse audio inputs.

## CONCLUSION
This project successfully integrates AI-driven analysis with traditional machine
learning techniques to address the challenges of voice authentication and deepfake
detection. By combining robust audio feature extraction with multiple classification
models—including Random Forest, LSTM, CNN-LSTM, and 1D CNN—the system
offers high accuracy in distinguishing genuine voices from deepfake audio samples.
A user-friendly Flask web interface allows seamless interaction, real-time feedback,
and analytics visualization. Overall, this work lays a solid foundation for future
advancements in secure voice authentication and deepfake mitigation across various
real-world applications.

## 👩‍💻 Author

**Sowmya C**
AI | NLP | Generative AI Enthusiast

---

## 🌟 Why This Project Matters

With the rise of AI-generated voices, traditional authentication systems are vulnerable.
This project addresses real-world challenges by combining **voice biometrics, deepfake detection, and AI intelligence** into a single unified platform.
