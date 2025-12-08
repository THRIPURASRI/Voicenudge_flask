import torchaudio

# --- ✅ Temporary compatibility patch for SpeechBrain 1.x (Torchaudio ≥2.9) ---
if not hasattr(torchaudio, "list_audio_backends"):
    # Newer torchaudio removed this method; SpeechBrain still calls it.
    torchaudio.list_audio_backends = lambda: ["sox_io", "soundfile"]
# ------------------------------------------------------------------------------

# ✅ Ensure symlink issues on Windows/Docker are handled safely
import patch_speechbrain_symlinks
from voicenudge import create_app
from dotenv import load_dotenv

# ✅ Automatically load environment variables from .env
load_dotenv()

# ✅ Create the Flask app
app = create_app()

# ✅ Run the Flask app (for local or Docker dev)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
