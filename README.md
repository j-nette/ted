# ted
cmd-f 2025

## Python Setup

### Make your virtual environment
``sudo apt update``

``sudo apt install python3 python3-venv``

``cd ./.../ted``

``python3 -m venv .venv``

``source .venv/bin/activate``

### Install the following packages
``pip install -q -U google-genai``

``pip install python-dotenv``

``pip install pyserial ``

### Add the API key
Create a ``.env`` file. Add the following to the file:

KEY="YOUR_KEY"