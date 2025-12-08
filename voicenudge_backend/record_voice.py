import sounddevice as sd
from scipy.io.wavfile import write

# 🎚️ Settings
fs = 16000          # Sampling rate (Hz)
duration = 15        # seconds to record
filename = "samples/Nikitha_1.wav"

print("🎤 Recording... Speak now!")
audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()  # Wait until recording is finished

# 💾 Save as .wav
write(filename, fs, audio)
print(f"✅ Saved recording to {filename}")
