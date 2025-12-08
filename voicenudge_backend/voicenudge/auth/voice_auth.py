import os
import torch
import numpy as np
import tempfile
import torchaudio
import soundfile as sf
from scipy.spatial.distance import cosine
import subprocess

# ----------------------------------------------
# ✅ Import SpeechBrain (no network required)
# ----------------------------------------------
try:
    from speechbrain.inference import EncoderClassifier
except ImportError:
    from speechbrain.pretrained import EncoderClassifier


class VoiceAuth:
    """Handles voice embedding extraction and similarity comparison."""

    def __init__(self):
        print("🔄 Loading SpeechBrain voice model (Offline Local Mode)...")

        # Path to your manually downloaded model folder
        model_dir = os.path.join(
            os.getcwd(), "pretrained_models", "ecapa_voxceleb_offline"
        )

        if not os.path.exists(model_dir):
            raise FileNotFoundError(
                f"❌ Model folder not found at: {model_dir}\n"
                "Please ensure you downloaded the model files manually from:\n"
                "https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb"
            )

        self.model = EncoderClassifier.from_hparams(
            source=model_dir,
            savedir=model_dir,
            run_opts={"device": "cpu"},
        )
        print("✅ Model loaded successfully (Offline Local Mode).")

    # ---------------------- 🔹 Extract Embedding ----------------------
    def get_embedding(self, wav_path):
        """Safely extract embedding (handles mic recordings + enforces 15s duration)."""
        import time

        # ✅ Always copy to /tmp — guaranteed writable inside Docker
        tmp_path = f"/tmp/{os.path.basename(wav_path)}"
        os.makedirs("/tmp", exist_ok=True)
        os.system(f"cp {wav_path} {tmp_path}")
        fixed_wav = tmp_path

        # 🕒 ensure file write is complete
        for _ in range(3):
            if os.path.exists(fixed_wav) and os.path.getsize(fixed_wav) > 1000:
                break
            time.sleep(0.5)

        # 🔄 Auto-convert mic recordings → WAV using ffmpeg
        if not fixed_wav.lower().endswith(".wav"):
            tmp_wav = tempfile.mktemp(suffix=".wav", dir="/tmp")
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", fixed_wav, "-ac", "1", "-ar", "16000", tmp_wav],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                fixed_wav = tmp_wav
                print(f"🎧 Converted mic recording → {fixed_wav}")
            except Exception as e:
                raise RuntimeError(f"FFmpeg failed to convert file: {e}")

        # ✅ Load using torchaudio (safe retry)
        try:
            signal, sr = torchaudio.load(fixed_wav)
        except Exception as e:
            print(f"⚠️ torchaudio load failed ({e}), retrying with ffmpeg decode...")
            tmp_fixed = tempfile.mktemp(suffix=".wav", dir="/tmp")
            subprocess.run(
                ["ffmpeg", "-y", "-i", fixed_wav, "-ac", "1", "-ar", "16000", tmp_fixed],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            )
            signal, sr = torchaudio.load(tmp_fixed)

        duration = signal.shape[1] / sr
        if duration < 15:
            raise ValueError("Voice sample too short — please record at least 15 seconds")

        emb = self.model.encode_batch(signal)
        print(f"✅ Successfully extracted embedding ({duration:.2f}s audio).")
        return emb.squeeze().detach().cpu().numpy()

    # ---------------------- 🔹 Compare two voice files ----------------------
    def compare_voices(self, file1, file2):
        """Compare two audio files (paths) and return similarity score."""
        emb1 = self.get_embedding(file1)
        emb2 = self.get_embedding(file2)
        return self.compare_embeddings(emb1, emb2)

    # ---------------------- 🔹 Compare embeddings directly ----------------------
    def compare_embeddings(self, emb1, emb2):
        """Compare two embeddings (arrays) using cosine similarity."""
        emb1 = np.squeeze(np.array(emb1, dtype=np.float32))
        emb2 = np.squeeze(np.array(emb2, dtype=np.float32))
        return float(1 - cosine(emb1, emb2))


# ----------------------------------------------
# 🧪 Optional: Self-test
# ----------------------------------------------
if __name__ == "__main__":
    print("🧪 Testing offline model load...")
    VoiceAuth()
    print("✅ Offline model loaded successfully.")
