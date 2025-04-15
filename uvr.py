import os
import tempfile
import time

from my_utils import clean_path
from vr import AudioPre
import ffmpeg
import torch

def check_if_reformat_needed(input_path, ffprobe_path='/opt/homebrew/bin/ffprobe'):
    """
    Check if an audio file needs to be reformatted.
    Returns True if reformatting is needed, False otherwise.
    """
    need_reformat = True
    try:
        info = ffmpeg.probe(input_path, cmd=ffprobe_path)
        channel_count = info["streams"][0]["channels"]
        sample_rate = info["streams"][0]["sample_rate"]

        # No need to reformat if:
        # - channel count is not 2, OR
        # - sample rate is 44100
        if channel_count != 2 or sample_rate == "44100":
            need_reformat = False
    except Exception as e:
        print(f"Error checking format: {e}")
    return need_reformat

def convert_audio(input_path, output_path, ar=44100, ac=2):
    try:
        ffmpeg.input(input_path)\
              .output(output_path, format='wav', acodec='pcm_s16le', ac=ac, ar=ar)\
              .overwrite_output()\
              .run(quiet=True)
        return True
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"Error converting audio: {str(e)}")
        return False

def get_torch_device():
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return "mps"  # Mac MPS
    elif torch.cuda.is_available():
        return "cuda"  # NVIDIA CUDA
    else:
        return "cpu"   # CPU fallback

def my_uvr(model_name, save_root_vocal, input_path, audio_format):
    weight_uvr5_root = "uvr5_weights"
    save_root_vocal = clean_path(save_root_vocal)
    device = get_torch_device()
    pre_fun = AudioPre(
        agg=2,
        model_path=os.path.join(weight_uvr5_root, model_name + ".pth"),
        device=device,
        is_half=False,
    )

    if check_if_reformat_needed(input_path):
        tmp_file_name = f"{os.path.basename(input_path)}.reformatted.wav"
        tmp_file_path = os.path.join(tempfile.gettempdir(), tmp_file_name)
        convert_audio(input_path, tmp_file_path)
        input_path = tmp_file_path

    try:
        pre_fun.handle_audio(
            music_file=input_path,
            ins_root=None,
            vocal_root=save_root_vocal,
            format=audio_format,
            is_hp3=False
        )
    except Exception as e:
        print("pre_fun.handle_audio error =>", e)
    finally:
        try:
            del pre_fun.model
            del pre_fun
        except Exception as e:
            print("del pre_fun.model =>", e)

        print("clean_empty_cache")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def main():
    start_time = time.perf_counter()
    my_uvr(
        model_name='HP5_only_main_vocal',
        save_root_vocal='/Users/yin.yan/Desktop/outputs/',
        input_path='/Users/yin.yan/Downloads/f2532a57ba0a833ef6f70e0b68b2dd9577020a174c976e0cf21e8994991ede09.mp3',
        audio_format='mp3'
    )
    end = time.perf_counter()
    print(f"Execution time: {end - start_time:.2f} seconds")

# main()
if __name__ == "__main__":
    main()
