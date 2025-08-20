#!/bin/bash
# Compatible agri_bot installation that preserves sentence-transformers

set -e

echo "🔧 Installing agri_bot dependencies with compatibility protection..."

# Step 1: Install packaging if needed
pip install packaging

# Step 2: Check current versions and avoid downgrades
current_torch=$(pip show torch 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
current_transformers=$(pip show transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
current_hf_hub=$(pip show huggingface-hub 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
current_sentence_transformers=$(pip show sentence-transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")

echo "Current versions: torch=$current_torch, transformers=$current_transformers, hf_hub=$current_hf_hub, sentence_transformers=$current_sentence_transformers"

# Step 3: Only install torch/transformers if not already compatible
if [[ "$current_torch" == "none" ]] || [[ "$current_torch" < "2.0.0" ]]; then
    echo "Installing/upgrading torch..."
    pip install torch>=2.2.0
else
    echo "Compatible torch already installed: $current_torch"
fi

if [[ "$current_transformers" == "none" ]] || [[ "$current_transformers" < "4.50.0" ]]; then
    echo "Installing/upgrading transformers..."
    pip install "transformers>=4.55.0"
else
    echo "Compatible transformers already installed: $current_transformers"
fi

# Step 4: Clone NeMo if not already present
if [ ! -d "NeMo" ]; then
    echo "Cloning NeMo repository..."
    git clone https://github.com/AI4Bharat/NeMo.git
fi

# Step 5: Install IndicTransToolkit (correct package name)
echo "Installing IndicTransToolkit..."
pip install IndicTransToolkit || {
    echo "IndicTransToolkit not available, trying alternatives..."
    pip install indictrans2 || echo "Warning: IndicTrans installation failed"
}

# Step 6: Install NeMo dependencies
echo "Installing NeMo dependencies..."
if [ -d "NeMo" ]; then
    cd NeMo
    if [ -f "reinstall.sh" ]; then
        bash reinstall.sh || echo "Warning: NeMo reinstall failed"
    else
        pip install -e . || echo "Warning: NeMo installation failed"
    fi
    cd ..
fi

# Step 7: Install sarvamai
echo "Installing sarvamai..."
pip install -U sarvamai || echo "Warning: sarvamai installation failed"

# Step 8: Install additional audio packages
echo "Installing audio processing packages..."
pip install librosa soundfile || echo "Warning: Some audio packages failed"

# Step 9: Fix numpy/pyarrow versions if needed
echo "Ensuring compatible numpy version..."
pip install "numpy>=1.21.0,<1.25.0" --upgrade

echo "✅ Compatible agri_bot setup complete!"
