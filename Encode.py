import numpy as np
import wave
import os
import argparse
from typing import List, Generator
import logging
from colorama import init, Fore, Style
from tqdm import tqdm

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SAMPLE_RATE = 7500
AMPLITUDE = 0.5
BASE_FREQUENCY = 100
FREQUENCY_MULTIPLIER = 10
DURATION = 0.1
MAX_INT16 = 32767  # Maximum positive value for a 16-bit signed integer
CHUNK_SIZE = 1024  # Size of each chunk to read

def generate_frequency(frequency: float, duration: float, sample_rate: int = SAMPLE_RATE, amplitude: float = AMPLITUDE) -> np.ndarray:
    """Generate a sound wave for a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def read_file_in_chunks(file_path: str, chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    """Generator to read a file in chunks."""
    with open(file_path, "rb") as file:
        while chunk := file.read(chunk_size):
            yield chunk

def process_chunk_to_frequencies(chunk: bytes, ext_data: bytes) -> List[np.ndarray]:
    """Generate frequencies based on a chunk of file bytes and extension bytes."""
    frequencies = []

    for byte in chunk:
        freq = generate_frequency((byte * FREQUENCY_MULTIPLIER) + BASE_FREQUENCY, DURATION)
        frequencies.append(freq)

    # Add extension data frequencies once per chunk (optional)
    for byte in ext_data:
        freq = generate_frequency((byte * FREQUENCY_MULTIPLIER) + BASE_FREQUENCY, DURATION)
        frequencies.append(freq)

    return frequencies

def write_wave_file(output_path: str, frequencies: List[np.ndarray], sample_rate: int = SAMPLE_RATE) -> None:
    """Write frequencies to a .wav file."""
    with wave.open(output_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        
        for freq in tqdm(frequencies, desc="Writing output file"):
            wave_data = (freq * MAX_INT16).astype(np.int16)
            wf.writeframes(wave_data.tobytes())

def validate_file(file_path: str) -> str:
    """Validate if the file exists."""
    if not os.path.exists(file_path):
        raise argparse.ArgumentTypeError(f"{Fore.RED}Error: {file_path} does not exist")
    return file_path

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate sound from file bytes.')
    parser.add_argument('input', type=validate_file, help='Input file')
    parser.add_argument('-o', '--output', type=str, help='Output .wav file path')
    args = parser.parse_args()

    file_path = args.input
    if args.output:
        output_path = args.output
    else:
        output_path = os.path.splitext(file_path)[0] + ".wav"

    ext = os.path.splitext(file_path)[1]
    ext_byte = bytes(ext, "ascii")

    file_size = os.path.getsize(file_path)
    num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

    logger.info(Fore.YELLOW + "Reading bytes from file in chunks: %s", file_path)

    all_frequencies = []
    for chunk in tqdm(read_file_in_chunks(file_path), total=num_chunks, desc="Processing chunks"):
        frequencies = process_chunk_to_frequencies(chunk, ext_byte)
        all_frequencies.extend(frequencies)

    logger.info(Fore.GREEN + "Writing wave file to: %s", output_path)
    write_wave_file(output_path, all_frequencies)

    logger.info(Fore.GREEN + "Sound wave successfully written to %s", output_path)
    logger.info(Fore.YELLOW + "Process complete.")

if __name__ == '__main__':
    main()