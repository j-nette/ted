# ted
cmd-f 2025

## Python Setup

### Make your virtual environment
sudo apt update
sudo apt install python3 python3-venv
cd ./.../ted
python3 -m venv .venv
source .venv/bin/activate

### Install the following packages
pip install -q -U google-genai
pip install python-dotenv

### Add the API key as
KEY="YOUR_KEY"