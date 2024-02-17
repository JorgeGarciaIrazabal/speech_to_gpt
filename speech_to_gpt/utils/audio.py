import pyaudio



def gen_header(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

def generate_audio(channels, rate, sample, chunk):
    #CHANNELS = 2
    #RATE = 44100 #44100 #48000
    #CHUNK = 2048 #1024 #2048
    #RECORD_SECONDS = 5
    FORMAT = pyaudio.paInt16 #pyaudio.paInt16 #pyaudio.paFloat32 #salah tunning jadi suara aneh
    CHUNK = 262144 #131072 #65536 #32768 #16384 #8192 #7168 #6144 #5120 #4096 #1024 mulai normal
    CHANNELS = channels
    RATE = 44100 #48000
    sampleRate = rate
    bitsPerSample = sample
    channels = channels
    wav_header = gen_header(sampleRate, bitsPerSample, channels)
    return wav_header + chunk
