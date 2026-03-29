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

## 🔌 API Endpoints

The system provides multiple REST API endpoints for model inference:

- `/predict_rf` → Random Forest model  
- `/predict_lstm_csv` → LSTM model  
- `/predict_cnn_combined` → CNN model  
- `/predict_cnn_lstm_combined` → Hybrid CNN-LSTM model  

Each endpoint returns:
- Prediction (Real / Deepfake)
- Confidence score
- Timestamp
  
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
- Uses **multiple machine learning and deep learning models**:
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

1. 🎙️ Voice Input (Upload / Live Recording)  
2. 🧹 Audio Preprocessing (Noise Reduction)  
3. 📊 Feature Extraction (MFCC)  
4. 🔍 Speaker Verification (Cosine Similarity)  
5. 🎭 Deepfake Detection Model  
6. 📈 Visualization & Results Dashboard  

---

## 🧰 Tech Stack

- Python
- Flask  
- Librosa  
- Scikit-learn / NumPy / Pandas
- TensorFlow / Keras (Deep Learning)
- Whisper  
- gTTS  
- Plotly & Matplotlib  
- SQLite  
- HTML, CSS, JavaScript  

---

## 📁 Project Structure
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
├── models/


---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Sowmya-2348562/ai-voice-authentication-deepfake-detection.git
cd ai-voice-authentication-deepfake-detection

2️⃣ Create Virtual Environment
python -m venv venv

Activate:

Windows:
venv\Scripts\activate
Mac/Linux:
source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables
Create .env file:
GROQ_API_KEY=your_api_key_here

5️⃣ Run the Application
python app.py

📸 Screenshots

<img width="635" height="924" alt="image" src="https://github.com/user-attachments/assets/ef9bbc6e-0070-4fb0-86d5-9460b3d9aeb8" />
<img width="1450" height="547" alt="image" src="https://github.com/user-attachments/assets/25b1c1b7-5c95-413d-abe0-05f799c9b93e" />
<img width="1339" height="463" alt="image" src="https://github.com/user-attachments/assets/13c0f9d0-d714-4301-af68-326d12bda11a" />
<img width="1442" height="845" alt="image" src="https://github.com/user-attachments/assets/539066bd-0339-471e-9089-d00356b87d5f" />
<img width="1450" height="743" alt="image" src="https://github.com/user-attachments/assets/805c73fa-114f-420b-9f11-05c801aa0f5f" />
<img width="1450" height="565" alt="image" src="https://github.com/user-attachments/assets/7ebcb435-2542-4758-8b1a-7f40c7b10a8d" />
<img width="1450" height="500" alt="image" src="https://github.com/user-attachments/assets/dee7246a-3863-4d80-bb40-b6e4f50d3a51" />
<img width="1450" height="814" alt="image" src="https://github.com/user-attachments/assets/8d2dfb0b-bca6-4a3f-8f2b-ef5d5d1e98e8" />
<img width="1450" height="923" alt="image" src="https://github.com/user-attachments/assets/faf94cb9-92aa-4f72-a17e-dcb7a2d9e982" />
<img width="1208" height="958" alt="Screenshot 2025-04-12 003923" src="https://github.com/user-attachments/assets/b58b953f-f3a2-473f-8973-edf933962294" />
<img width="1223" height="574" alt="image" src="https://github.com/user-attachments/assets/d2bdf4a1-e6e2-495d-959f-ee250a1dee35" />
<img width="1519" height="855" alt="image" src="https://github.com/user-attachments/assets/040863d9-acab-40bc-a571-515288975a7b" />
<img width="1467" height="851" alt="image" src="https://github.com/user-attachments/assets/4ee82995-0632-43ce-b7f3-669b2aac72e1" />

⚠️ Important Notes
.env file is not included
Large model files may not be included
Some features use external APIs

## 💡 Use Cases

- 🔐 Secure login using voice biometrics  
- 🏦 Fraud detection in banking & finance  
- 🎙️ Deepfake voice detection for media verification  
- 🧑‍💻 Identity verification in remote systems  
- 🌍 Multilingual voice-based applications

## 👩‍💻 Author

**Sowmya C**  
AI | NLP | Generative AI Enthusiast

## 🌟 Why This Project Matters

With the rise of AI-generated voices, traditional authentication systems are vulnerable.  
This project addresses real-world challenges by combining **voice biometrics, deepfake detection, and AI intelligence** into a single unified platform.


