import panel as pn
import sounddevice as sd
import soundfile as sf

def record_audio(event):
    duration = 5  # Duration of the recording in seconds
    fs = 44100  # Sample rate
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    sf.write('recorded_audio.wav', recording, fs)  # Save the recorded audio to a file

button = pn.widgets.Button(name='Record Audio')
button.on_click(record_audio)

app = pn.Column(button)
app.show()
