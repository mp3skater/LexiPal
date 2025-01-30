import speech_recognition as sr


def recognize_multilingual_speech(audio_file_path, languages=None):
    if languages is None:
        languages = ['en-US', 'ja-JP']
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file_path) as source:
            print("Listening to the audio...")
            audio_data = recognizer.record(source)

        print("Processing the audio...")
        recognized_text = recognizer.recognize_google(audio_data, language=",".join(languages))

        print("Recognition successful!")
        return recognized_text

    except sr.UnknownValueError:
        return "Speech could not be understood."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


# Example Usage
audio_path = "path/to/audio/file.wav"  # Replace with the actual path
print(recognize_multilingual_speech(audio_path))
