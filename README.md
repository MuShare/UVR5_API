# UVR5_API

Used UVR5 to separate vocals from the audio.

# Model
- VR

# API

```
POST /voice/vocal_process
Query: ossFilePath 
```

# Usage

```shell
git clone https://github.com/MuShare/UVR5_API.git
cd UVR5_API
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt
uvicorn main:app --host 0.0.0.0
```

# Reference Repo
- https://github.com/lililuya/UVR_api
- https://github.com/NextAudioGen/ultimatevocalremover_api
- https://github.com/RVC-Boss/GPT-SoVITS
