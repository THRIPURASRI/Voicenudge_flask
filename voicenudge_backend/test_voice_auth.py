from voicenudge.auth.voice_auth import VoiceAuth

# Initialize the voice authentication system
va = VoiceAuth()

# Compare the two voices
score = va.compare_voices("samples/Nikitha_1.wav", "samples/other_person.wav")

# Display the result
print(f"🔊 Similarity Score: {score:.4f}")

# Decision threshold (can be tuned)

if score > 0.65:
    print("✅ Same person (Match)")
else:
    print("❌ Different person (No match)")

