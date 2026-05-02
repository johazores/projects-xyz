# Python AI Audio Studio

A clean beginner-friendly Python backend for:

- Uploading audio
- Converting audio to MP3
- Normalizing audio volume
- Trimming audio
- Generating basic AI audio from text using `suno/bark-small`

This is not yet a Suno-level music generator. It is a clean foundation for learning audio processing and AI audio generation using Python.

---

## Project structure

```txt
audio-process/
  app/
    api/
      audio_routes.py
    core/
      config.py
      errors.py
    services/
      audio_generation_service.py
      ffmpeg_service.py
    utils/
      files.py
    main.py
  uploads/
  processed/
  main.py
  requirements.txt
  .env.example
  README.md
```

---

## 1. Install Python on Windows using CLI

Open PowerShell and run:

```powershell
winget install Python.Python.3.12
```

Close PowerShell, then open it again.

Check Python:

```powershell
py --version
pip --version
```

---

## 2. Install Python on Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```

---

## 3. Install FFmpeg

### Windows

```powershell
winget install Gyan.FFmpeg
```

Then close and reopen PowerShell.

Check:

```powershell
ffmpeg -version
```

If `ffmpeg` is not recognized, add this folder to PATH:

```txt
C:\Users\YOUR_USERNAME\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin
```

Do not add `ffmpeg.exe` itself. Add only the `bin` folder.

### Ubuntu

```bash
sudo apt update
sudo apt install -y ffmpeg
ffmpeg -version
```

### macOS

```bash
brew install ffmpeg
ffmpeg -version
```

---

## 4. Setup project

### Windows PowerShell

```powershell
cd path\to\python-ai-audio-studio
py -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install torch torchaudio
copy .env.example .env
```

### Ubuntu / macOS

```bash
cd path/to/python-ai-audio-studio
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install torch torchaudio
cp .env.example .env
```

---

## 5. Run the app

### Windows

```powershell
uvicorn main:app --reload
```

### Ubuntu / macOS

```bash
uvicorn main:app --reload
```

Open:

```txt
http://localhost:8000/docs
```

---

## 6. Available endpoints

### Health check

```txt
GET /health
```

### Convert to MP3

```txt
POST /audio/convert-to-mp3
```

Upload an audio file.

### Normalize audio

```txt
POST /audio/normalize
```

Upload an audio file.

### Trim audio

```txt
POST /audio/trim
```

Form fields:

```txt
audio = file
start = 0
duration = 10
```

### Generate audio from text

```txt
POST /audio/generate
```

Body:

```json
{
  "text": "Hello, this is my first generated audio using Python."
}
```

The first generation will be slow because the model downloads first.

---

## 7. RTX 4060 Ti GPU note

Your RTX 4060 Ti can help with AI generation, but only if PyTorch detects CUDA.

Check inside your virtual environment:

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
```

If it says `False`, install the CUDA PyTorch build from the official PyTorch selector.

Common CUDA install command:

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Then test again:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 8. Important notes

- FFmpeg is required for upload processing endpoints.
- AI generation endpoint uses `suno/bark-small`.
- First AI request downloads the model and can take time.
- CPU generation works but can be slow.
- GPU generation is better but requires CUDA-enabled PyTorch.
- Generated and processed files are saved inside `processed/`.

---

## 9. Recommended learning path

1. Make `/audio/convert-to-mp3` work.
2. Make `/audio/normalize` work.
3. Make `/audio/trim` work.
4. Try `/audio/generate` on CPU.
5. Enable CUDA for your RTX 4060 Ti.
6. Later add MusicGen for actual music generation.
