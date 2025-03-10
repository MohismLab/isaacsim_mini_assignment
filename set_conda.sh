#!/bin/bash

current_path=$(pwd)
echo "Current path: $current_path"

if ! command -v conda &> /dev/null
then
    echo "conda could not be found. Please ensure conda is installed and available in your PATH."
    exit 1
fi


conda activate isaaclab


cd ~/.local/share/ov/pkg/isaac-sim-4.2.0


source ./setup_conda_env.sh


cd $current_path