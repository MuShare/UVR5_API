from ast import Not
from typing import Union
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from uvr import my_uvr
import tempfile
import os
import uuid
import requests

app = FastAPI()

@app.get("/")
async def read_root():
    return {
        "Hello": "World"
    }


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {
        "item_id": item_id,
        "q": q
    }

async def download_file(url: str, temp_file_path: str):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"File downloaded successfully to {temp_file_path}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error downloading file: {e}")

def get_file(keyword: str, endswith: str, in_dir: str) -> str | None:
    # 获取所有子文件
    subfiles = os.listdir(in_dir)
    for file_name in subfiles:
        if file_name.endswith(endswith) and keyword in file_name:
            return os.path.join(in_dir, file_name)
    return None

@app.post("/voice/vocal_process", response_class=FileResponse)
async def process_vocal(
    ossFilePath: str = Query(
        None,
        title="aliyun OSS file path",
        description="The path to the audio file in aliyun OSS",
        example="https://bucket-name/path/to/file.mp3"
    ),
):
    tempdir = tempfile.gettempdir()
    random_uuid = str(uuid.uuid4())
    temp_file_path = os.path.join(tempdir, f"{random_uuid}.mp3")

    try:
        await download_file(ossFilePath, temp_file_path)

        my_uvr(
            model_name='HP5_only_main_vocal',
            save_root_vocal='./vocal_voice/',
            input_path=temp_file_path,
            audio_format='wav'
        )

        saved_vocal_path = get_file(random_uuid, '.mp3', './vocal_voice/')
        if saved_vocal_path is None:
            raise Exception("Vocal file not found")

        return FileResponse(saved_vocal_path, media_type="audio/mpeg")
    except Exception as e:
        print(f"Error processing vocal: {e}")
