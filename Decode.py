import numpy as np
import scipy.fftpack, os, subprocess
from pydub import AudioSegment

import sys

if sys.argv[1] == None:
    raise ValueError("No argument supplied")

file = sys.argv[1]
duration = 0.1
timestamp = 0

filename, ext_audio = os.path.splitext(file)
retrieved_extension=""
extension_lenght = 1


if ext_audio !=".wav" and ext_audio !=".flac":
    print("converting audio file to wav")
    output_file = filename+".wav"


    command = [
        'ffmpeg',
        '-i', file,
        '-b:a', "8k",
        '-bitexact',
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', "8k",
        output_file
    ]

    subprocess.run(command, check=True)
    os.remove(file)
    print("BAAM deleted the old audio file and you didn't even saw")
    file = filename+".wav"

print("Opening your file, It's gonna take like 2 minutes dude chill....")
sound = AudioSegment.from_file(file, format="wav")
sample_rate = sound.frame_rate
audio_data = np.array(sound.get_array_of_samples())
audio_data = audio_data / np.max(np.abs(audio_data))

#get frequency
print("Analyzing frequencies...")
with open(filename, "wb+") as f:
    while True:

        start_sample = int(timestamp * sample_rate)
        end_sample = start_sample + int(duration * sample_rate)
        
        segment = audio_data[start_sample:end_sample]
        
        if len(segment) == 1 or len(segment) == 0:
            break
            
        
        N = len(segment)
        T = 1.0 / sample_rate
        yf = scipy.fftpack.fft(segment)
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        
        idx = np.argmax(np.abs(yf[:N//2]))
        freq = xf[idx]
        
        f.write(bytes([int((freq-100)/10)]))
        
        timestamp += duration
    f.close()
#find the right extension of the file
with open(filename, "r+b") as f:
    filesize = os.path.getsize(filename)
    while True:
        f.seek(filesize - extension_lenght)
        chunk = f.read(extension_lenght)
        if chunk.startswith(".".encode('ascii')):
            retrieved_extension = chunk.decode('ascii')
            f.truncate(filesize - extension_lenght)
            break
        extension_lenght+=1
    f.close()
#write file
num_of_file = 0
while True:
    try:
        num_of_file +=1
        os.rename(filename, filename +str(num_of_file)+ retrieved_extension)
        break
    except FileExistsError:
        continue
