"""
Split MP3 file to Midi
python3 -m venv spleeter-env
source spleeter-env/bin/activate

# 2. Install compatible core deps first (use prebuilt wheels)
pip install -U pip wheel setuptools
pip install "numpy<2.0" "numba>=0.59,<0.61"

# 3. Install Apple’s TensorFlow build
pip install tensorflow-macos==2.12 tensorflow-metal==1.1.0

# 4. Finally install Spleeter (without its outdated deps)
pip install spleeter --no-deps
pip install librosa soundfile
"""



def main():


if __name__ == "__main__":
    main()