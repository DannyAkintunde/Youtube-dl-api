import os
import logging
import shutil
import subprocess
from languagecodes import iso_639_alpha3
from settings import CODECS

logger = logging.getLogger(__name__)

def combine_video_and_audio(video_path,audio_path,temp_path):
    """
    Add audio to a video file using ffmpeg.

    :param video_path: Path to the input video file.
    :param audio_path: Path to the audio file (e.g., .mp3).
    :param output_path: Path where the output video with audio will be saved.
    """
    if os.path.exists(temp_path):
      logger.info("Deleting temp file " + temp_path)
      os.remove(temp_path)
    # FFmpeg command to combine video and audio
    ffmpeg_command = [
      'ffmpeg',
      '-i', video_path,
      '-i', audio_path,
      '-c:v', 'copy',
      '-c:a', CODECS[1],
      '-preset', 'fast',
      '-tune', 'film',
      #'-strict', 'experimental',
      temp_path
    ]
    
    logger.info(f"adding audio from {audio_path} to {video_path}")
    # Run the FFmpeg command
    subprocess.run(ffmpeg_command, check=True)
    
    # Ensure the temporary file has been written and is not in use
    if os.path.isfile(temp_path):
        # Replace the original file with the temporary file
        shutil.move(temp_path, video_path)
        logger.info(f"Video and subtitle combined successfully. Output file: {video_path}")
    else:
        logger.warning(f"Temporary file {temp_path} not found.")
    
 
    logger.info(f"Video and audio combined successfully. Output file: {video_path}")
    

def add_subtitles(video_path, subtitle_path, temp_path, burn= True, lang_code="en"):
    """
    Add subtitles to a video file using ffmpeg.

    :param video_path: Path to the input video file.
    :param subtitle_path: Path to the subtitle file (e.g., .srt).
    :param temp_path: Path where the temporary output video with subtitles will be saved.
    """
    
    if os.path.exists(temp_path):
      logger.info("Deleting temp file " + temp_path)
      os.remove(temp_path)
    
    # FFmpeg command to combine video and subtitle
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles='{subtitle_path}':force_style='Alignment=2'",
        '-crf', '18',
        '-preset', 'fast',
        '-tune', 'film',
        temp_path
    ]
    
    if not burn:
      lang_code = iso_639_alpha3(lang_code.replace("a.", ""))
      ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-i', subtitle_path,
        '-c', 'copy',
        '-c:s', 'mov_text' ,
        '-metadata:s:s:0', f'language={lang_code}',
        temp_path
        ]

    logger.info(f"Adding subtitles from {subtitle_path} to {video_path}... with presets burn={burn} and lang: {lang_code}")
    
    # Run the FFmpeg command
    subprocess.run(ffmpeg_command, check=True)
    
    # Ensure the temporary file has been written and is not in use
    if os.path.isfile(temp_path):
        # Replace the original file with the temporary file
        shutil.move(temp_path, video_path)
        logger.info(f"Video and subtitle combined successfully. Output file: {video_path}")
    else:
        logger.warning(f"Temporary file {temp_path} not found.")
    
