import wave
import numpy as np

def load_wave_file(file_path):
    with wave.open(file_path, 'r') as wave_file:
        signal = wave_file.readframes(-1)
        signal = np.frombuffer(signal, dtype='int16')
        file_name = file_path.split('/')[-1]
        frames = wave_file.getnframes()
        sampwidth = wave_file.getsampwidth()
        channels = wave_file.getnchannels()
        rate = wave_file.getframerate()
        time = np.linspace(0, len(signal) / rate, num=len(signal))
        length = frames / rate
        size_bytes = frames * sampwidth * channels
        size_kb = size_bytes / 1024
        
        details = f"Name: {file_name}\nSize: {length:.2f} sec - {size_kb:.0f}KB\n" \
                            f"Bps: {sampwidth * 8}\nChannels: {channels}\nRate: {rate}Hz"
        return signal, time, details, frames,channels
