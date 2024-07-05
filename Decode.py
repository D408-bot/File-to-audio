import numpy as np
import scipy.fftpack
import os
import subprocess
from pydub import AudioSegment
import argparse
from typing import Tuple
from colorama import init, Fore, Style
import logging

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Rainbow colors
rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

# Constants
DURATION = 0.1
EXTENSIONS = [".wav", ".flac"]
SAMPLE_RATE = 8000
BASE_FREQUENCY = 100
FREQUENCY_MULTIPLIER = 10

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_to_wav(file_path: str, output_file: str) -> None:
    """Convert audio file to wav format using ffmpeg."""
    logger.info(Fore.YELLOW + "Converting audio file to WAV format...")
    command = [
        'ffmpeg',
        '-i', file_path,
        '-b:a', "8k",
        '-bitexact',
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', str(SAMPLE_RATE),
        output_file
    ]

    subprocess.run(command, check=True)
    os.remove(file_path)
    logger.info(Fore.GREEN + "Old audio file deleted.")

def read_audio_file(file_path: str) -> Tuple[int, np.ndarray]:
    """Read audio file and return sample rate and audio data."""
    logger.info(Fore.CYAN + "Opening audio file and reading data...")
    sound = AudioSegment.from_file(file_path, format="wav")
    sample_rate = sound.frame_rate
    audio_data = np.array(sound.get_array_of_samples())
    audio_data = audio_data / np.max(np.abs(audio_data))
    return sample_rate, audio_data

def analyze_frequencies(sample_rate: int, audio_data: np.ndarray, output_file: str) -> None:
    """Analyze frequencies and write decoded data to output file."""
    timestamp = 0
    with open(output_file, "wb+") as f:
        logger.info(Fore.MAGENTA + "Analyzing frequencies and writing decoded data...")
        while True:
            start_sample = int(timestamp * sample_rate)
            end_sample = start_sample + int(DURATION * sample_rate)
            segment = audio_data[start_sample:end_sample]
            
            if len(segment) == 1 or len(segment) == 0:
                break

            N = len(segment)
            T = 1.0 / sample_rate
            yf = scipy.fftpack.fft(segment)
            xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
            
            idx = np.argmax(np.abs(yf[:N//2]))
            freq = xf[idx]
            
            f.write(bytes([int((freq - BASE_FREQUENCY) / FREQUENCY_MULTIPLIER)]))
            
            timestamp += DURATION

def retrieve_extension(file_path: str) -> str:
    """Retrieve the original extension of the encoded file."""
    extension_length = 1
    with open(file_path, "r+b") as f:
        filesize = os.path.getsize(file_path)
        while True:
            f.seek(filesize - extension_length)
            chunk = f.read(extension_length)
            if chunk.startswith(".".encode('ascii')):
                retrieved_extension = chunk.decode('ascii')
                f.truncate(filesize - extension_length)
                return retrieved_extension
            extension_length += 1

def rename_file(output_file: str, retrieved_extension: str) -> None:
    """Rename the decoded file with the retrieved extension."""
    num_of_file = 0
    while True:
        try:
            num_of_file += 1
            new_filename = output_file + str(num_of_file) + retrieved_extension
            os.rename(output_file, new_filename)
            break
        except FileExistsError:
            continue

def validate_file(file_path: str) -> str:
    """Validate if the file exists."""
    if not os.path.exists(file_path):
        raise argparse.ArgumentTypeError(f"{Fore.RED}Error: {file_path} does not exist")
    return file_path

def main() -> None:
    parser = argparse.ArgumentParser(description='Decode sound from an audio file.')
    parser.add_argument('input', type=validate_file, help='Input audio file')
    parser.add_argument('-o', '--output', type=str, help='Output file path')
    args = parser.parse_args()

    file_path = args.input
    output_file = args.output if args.output else os.path.splitext(file_path)[0]

    ext_audio = os.path.splitext(file_path)[1]

    if ext_audio not in EXTENSIONS:
        convert_to_wav(file_path, output_file + ".wav")
        file_path = output_file + ".wav"

    sample_rate, audio_data = read_audio_file(file_path)
    analyze_frequencies(sample_rate, audio_data, output_file)

    retrieved_extension = retrieve_extension(output_file)
    rename_file(output_file, retrieved_extension)

    logger.info(Fore.GREEN + "Decoding completed successfully!")

if __name__ == '__main__':
    main()
