#!/bin/bash

# Test the model selection prompt
source /store/Answering_Agriculture2/install_agri_bot.sh

# Simulate non-CLI mode
MODEL_SET_VIA_CLI=false
OLLAMA_MODEL="gemma3:1b"

echo "Testing model selection prompt..."
echo
prompt_llm_model_selection
echo
echo "Selected model: $OLLAMA_MODEL"
