"""# 1️⃣ Create a fresh ARM Python virtual environment
/opt/homebrew/bin/python3 -m venv ~/venvs/venv-basicpitch-arm
source ~/venvs/venv-basicpitch-arm/bin/activate

# 2️⃣ Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# 3️⃣ Install ARM-native TensorFlow for Apple Silicon
pip install tensorflow-macos==2.12.0 tensorflow-metal==1.1.0

# 4️⃣ Install basic-pitch without pulling Intel TensorFlow
pip install --no-deps basic-pitch

# 5️⃣ Install other ARM-compatible dependencies
pip install numpy==1.23.5 librosa==0.11.0 soundfile==0.13.1 soxr==1.0.0

# 6️⃣ Optional: install htdemucs if you need model separation
pip install htdemucs==4.6.0

# ✅ Ready to run
echo "Setup complete! Activate with: source ~/venvs/venv-basicpitch-arm/bin/activate"
"""