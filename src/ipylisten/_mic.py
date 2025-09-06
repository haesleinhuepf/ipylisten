from __future__ import annotations

from typing import Optional
import os
import time
import tempfile
from collections import deque

import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI

# ---- TUNABLES -------------------------------------------------------------
SAMPLE_RATE = 16000          # 16 kHz mono
CHANNELS = 1
BLOCK_DUR = 0.03             # seconds per audio block (~30 ms)
CALIBRATION_TIME = 0.5       # seconds to measure ambient noise
THRESHOLD_MULT = 3.0         # speech threshold = noise_rms * this
MIN_THRESHOLD = 0.010        # floor on threshold (float32 RMS)
SILENCE_TO_STOP = 2.0       # seconds of silence to end recording
PRE_SPEECH_PAD = 0.20        # keep a little audio before first speech
LISTEN_TIMEOUT = 120         # max time to wait overall (sec)
MODEL = "gpt-4o-mini-transcribe"  # or "whisper-1"
# --------------------------------------------------------------------------


def listen_to_microphone(
    microphone_index: Optional[int] = None,
    timeout: Optional[float] = None,
) -> Optional[str]:
    """Recognizes speech from microphone and returns it as a string.

    Parameters
    ----------
    microphone_index: int | None
        Index from ``list_microphones()``; defaults to system default microphone.
    timeout: float | None
        Seconds to wait for a phrase and maximum phrase length.
    """

    audio = record_until_silence()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        save_wav(temp_file.name, audio)
        text = transcribe_wav(temp_file.name)


    print("You said:", text)
    return text



def rms(y: np.ndarray) -> float:
    # y is float32 in [-1,1]
    return float(np.sqrt(np.mean(np.square(y), dtype=np.float64)))

def record_until_silence() -> np.ndarray:
    blocksize = int(SAMPLE_RATE * BLOCK_DUR)
    calib_blocks = max(1, int(CALIBRATION_TIME / BLOCK_DUR))
    prepad_len = max(1, int(PRE_SPEECH_PAD / BLOCK_DUR))

    print("Opening microphone…")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32") as stream:
        # Calibrate ambient noise
        print(f"Calibrating noise floor ({CALIBRATION_TIME:.2f}s)…")
        noise_vals = []
        for _ in range(calib_blocks):
            data, _ = stream.read(blocksize)
            noise_vals.append(rms(data))
        noise_rms = float(np.median(noise_vals)) if noise_vals else 0.0
        threshold = max(noise_rms * THRESHOLD_MULT, MIN_THRESHOLD)
        print(f"Noise RMS≈{noise_rms:.4f}, threshold≈{threshold:.4f}")
        print("Listening… start speaking. (Ctrl+C to cancel)")

        pre_roll = deque(maxlen=prepad_len)
        chunks = []
        speaking = False
        silence_accum = 0.0
        start_time = time.time()

        while True:
            if time.time() - start_time > LISTEN_TIMEOUT:
                if not speaking:
                    print("Timeout: no speech detected.")
                else:
                    print("Timeout reached, stopping.")
                break

            data, _ = stream.read(blocksize)   # shape: (frames, channels)
            y = data.reshape(-1)               # mono float32
            pre_roll.append(data.copy())       # keep original dtype/shape
            level = rms(y)

            if not speaking:
                if level > threshold:
                    speaking = True
                    # include pre-speech padding
                    chunks.extend(list(pre_roll))
                    pre_roll.clear()
                    chunks.append(data.copy())
                    silence_accum = 0.0
                # else: still waiting for speech
            else:
                chunks.append(data.copy())
                if level > threshold:
                    silence_accum = 0.0
                else:
                    silence_accum += BLOCK_DUR
                    if silence_accum >= SILENCE_TO_STOP:
                        print("Silence detected — stopping.")
                        break

        if not chunks:
            return np.zeros((0, CHANNELS), dtype="float32")

        audio = np.vstack(chunks)
        return audio

def save_wav(path: str, audio: np.ndarray):
    sf.write(path, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")

def transcribe_wav(path: str, model: str = MODEL) -> str:
    client = OpenAI()  # uses OPENAI_API_KEY
    with open(path, "rb") as f:
        resp = client.audio.transcriptions.create(model=model, file=f)
    return resp.text