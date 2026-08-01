# Usage

## Start the studio

```bash
python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Local audio environments

### ACE-Step 1.5 music

Install ACE-Step from its official repository in a separate environment and launch its REST server:

```bash
git clone https://github.com/ace-step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep-api
```

For an 8GB GPU, use the ACE-Step 2B Turbo model, the `acestep-5Hz-lm-0.6B` planner, the PyTorch LM backend, INT8 quantization, and CPU offload in the ACE-Step configuration.

Configure this application:

```env
ACESTEP_API_URL=http://127.0.0.1:8001
ACESTEP_API_KEY=
```

Only localhost URLs are accepted.

### Stable Audio 3 sound effects

Install Stable Audio 3 from its official repository. Point this application to the generated `stable-audio` executable:

```env
STABLE_AUDIO_CLI=C:/models/stable-audio-3/.venv/Scripts/stable-audio.exe
```

The adapter uses `small-sfx`, which can run on CPU and avoids competing with image and video models for VRAM.

### Chatterbox expressive voices

Use Python 3.11 for the Chatterbox environment:

```bash
python -m pip install -r requirements-voices.txt
```

Chatterbox Turbo requires a reference clip. Multilingual V3 can use its default voice or a consented reference voice.

## Register voice consent

```bash
curl -X POST http://127.0.0.1:8000/voices/consents \
  -H "Content-Type: application/json" \
  -d '{
    "voice_name": "Channel host",
    "owner_name": "Voice owner",
    "reference_path": "C:/voices/host-reference.wav",
    "usage_scope": "Narration and podcast episodes for this local project",
    "confirmed": true
  }'
```

The record stores a SHA-256 fingerprint of the reference clip. Chatterbox rejects a missing, revoked, or mismatched consent record.

List or revoke records:

```bash
curl http://127.0.0.1:8000/voices/consents
curl -X DELETE http://127.0.0.1:8000/voices/consents/CONSENT_ID
```

## Generate expressive speech

```bash
curl -X POST http://127.0.0.1:8000/audio-ai/speech \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome back to the channel [chuckle].",
    "model": "speech.chatterbox-turbo",
    "reference_path": "C:/voices/host-reference.wav",
    "consent_id": "CONSENT_ID",
    "project": "episode-01"
  }'
```

## Generate music

```bash
curl -X POST http://127.0.0.1:8000/audio-ai/music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "calm futuristic documentary music, instrumental, subtle pulse",
    "duration": 30,
    "instrumental": true,
    "project": "episode-01"
  }'
```

ACE-Step runs asynchronously on its localhost server. The main job polls the local task and copies the completed audio into the project output folder.

## Generate a sound effect

```bash
curl -X POST http://127.0.0.1:8000/audio-ai/sound-effect \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "clean cinematic technology transition whoosh",
    "duration": 3,
    "project": "episode-01"
  }'
```

## Podcast workflow

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.podcast \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Local AI Creator Podcast",
    "project": "podcast-01",
    "music_prompt": "soft technology podcast music, instrumental",
    "segments": [
      {
        "speaker": "Host",
        "text": "Welcome to the show.",
        "tts_model": "speech.kokoro",
        "voice": "af_heart"
      },
      {
        "speaker": "Guest",
        "text": "Thanks for having me.",
        "tts_model": "speech.chatterbox-multilingual-v3",
        "language": "en",
        "reference_path": "C:/voices/guest.wav",
        "consent_id": "CONSENT_ID"
      }
    ]
  }'
```

The workflow generates each segment, inserts configured pauses, assembles and normalizes the dialogue, optionally mixes an ACE-Step music bed, writes a transcript, validates duration and peak volume, and creates a manifest.

## Mixed AI Short

Add `music_prompt` to generate a background bed. Add `sfx_prompt` to individual scenes to generate timed effects:

```json
{
  "script": "A short local AI demonstration.",
  "project": "short-01",
  "music_prompt": "minimal electronic documentary underscore",
  "music_volume": 0.12,
  "scenes": [
    {
      "prompt": "a local AI workstation",
      "sfx_prompt": "subtle computer startup sound",
      "sfx_volume": 0.3
    }
  ]
}
```

Music and sound effects are optional. If an optional backend is unavailable, the workflow still finishes with narration and visuals and records the reason in its manifest.

## Audio validation

Final podcast and Short audio records:

- duration
- mean volume
- maximum volume
- clipping-risk flag

All mixes are normalized with FFmpeg. The application never silently publishes or uploads generated media.

## Runtime rules for 8GB VRAM

- Keep batch size at one.
- Generate images and video before requesting ACE-Step music.
- Keep Stable Audio Small-SFX on CPU.
- Use one Chatterbox model at a time.
- Prefer Kokoro for ordinary narration and Chatterbox only when expressive or multilingual speech is needed.
- Review all cloned-voice consent records before sharing a project.
