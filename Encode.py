import numpy as np
import wave, os.path

frequencies = []
file = r"Sample/funny_guy.png"

filename, ext = os.path.splitext(file)
ext_byte = bytes(ext, "ascii")

def generate_frequency(frequency, duration, sample_rate=7500 , amplitude=0.5):
    # generate the sound wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    
    frequencies.append(wave)


with open(filename + ext, "rb") as f:
    print("Generating sound...")
    byte = f.read()
    #generate frequency based on the bytes of the file
    for i in range(len(byte)):
        generate_frequency(((byte[i]*10)+100), 0.1)
    #generate frequency for extension of file
    for i in range(len(ext)):
        generate_frequency((ext_byte[i]*10)+100, 0.1)


#write file
with wave.open(filename+".wav", 'w') as wf:
    print("Writing file...")
    wf.setnchannels(1)
    wf.setsampwidth(2) 
    wf.setframerate(7500)
        
    for i in range(len(frequencies)):

        wave_data = (frequencies[i] * 32767).astype(np.int16)
        wf.writeframes(wave_data.tobytes())
    