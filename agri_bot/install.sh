#!/bin/bash
set -e  # stop on first error

# Make sure you're already inside your virtual environment before running this script

# Step 1: Install torch, torchvision, torchaudio (initial)
pip install torch torchvision torchaudio

# Step 2: Install packaging
pip install packaging

# Step 3: Install huggingface_hub (only if not already compatible)
current_hf_hub=$(pip show huggingface-hub 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
if [[ "$current_hf_hub" == "none" ]] || python3 -c "
import pkg_resources
try:
    pkg_resources.require('huggingface-hub>=0.20.0')
    exit(1)  # Already compatible, don't install
except:
    exit(0)  # Not compatible, install specific version
"; then
    pip install huggingface_hub==0.23.2
else
    echo "Compatible huggingface-hub already installed: $current_hf_hub"
fi

# Step 4: Clone NeMo if not already present
if [ ! -d "NeMo" ]; then
    git clone https://github.com/AI4Bharat/NeMo.git
fi

# Step 5: Install torch specific versions
pip install torch==2.8.0
pip install torchvision==0.23.0

# Step 6: Remove torchaudio
pip uninstall -y torchaudio

# Step 7: Install IndicTransToolkit (with error handling)
pip install IndicTransToolkit || pip install indictrans2 || echo "Warning: IndicTrans installation failed"

# Step 8: Reinstall NeMo from source
cd NeMo
bash reinstall.sh
cd ..

# Step 9: Install sarvamai
pip install -U sarvamai

# Step 10: Re-install torch, transformers, huggingface-hub (only if needed)
# Check if transformers is already compatible
current_transformers=$(pip show transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
if [[ "$current_transformers" == "none" ]] || python3 -c "
import pkg_resources
try:
    pkg_resources.require('transformers>=4.41.0,<5.0.0')
    print('Compatible transformers already installed: $current_transformers')
    exit(1)  # Already compatible, don't reinstall
except:
    exit(0)  # Not compatible, reinstall
"; then
    pip install torch transformers huggingface-hub
else
    echo "Compatible transformers already installed, skipping reinstall"
    pip install torch  # Only reinstall torch
fi

# Step 11: Fix pyarrow version
pip install pyarrow==14.0.2

# Step 12: Fix numpy version
pip install numpy==1.26.0

echo "✅ Setup complete! (run inside your already-activated venv)"
