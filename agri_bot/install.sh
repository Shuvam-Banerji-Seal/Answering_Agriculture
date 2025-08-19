#!/bin/bash
set -e  # stop on first error

# Make sure you're already inside your virtual environment before running this script

# Step 1: Install torch, torchvision, torchaudio (initial)
pip install torch torchvision torchaudio

# Step 2: Install packaging
pip install packaging

# Step 3: Install huggingface_hub specific version
pip install huggingface_hub==0.23.2

# Step 4: Clone NeMo if not already present
if [ ! -d "NeMo" ]; then
    git clone https://github.com/AI4Bharat/NeMo.git
fi

# Step 5: Install torch specific versions
pip install torch==2.8.0
pip install torchvision==0.23.0

# Step 6: Remove torchaudio
pip uninstall -y torchaudio

# Step 7: Install IndicTransToolkit
pip install IndicTransToolkit

# Step 8: Reinstall NeMo from source
cd NeMo
bash reinstall.sh
cd ..

# Step 9: Install sarvamai
pip install -U sarvamai

# Step 10: Re-install torch, transformers, huggingface-hub
pip install torch transformers huggingface-hub

# Step 11: Fix pyarrow version
pip install pyarrow==14.0.2

# Step 12: Fix numpy version
pip install numpy==1.26.0

echo "✅ Setup complete! (run inside your already-activated venv)"
