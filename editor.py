import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def combine_video_and_audio(video_path,audio_path,temp_path):
    """
    Add audio to a video file using ffmpeg.

    :param video_path: Path to the input video file.
    :param audio_path: Path to the audio file (e.g., .mp3).
    :param output_path: Path where the output video with audio will be saved.
    """
    # FFmpeg command to combine video and audio
    ffmpeg_command = [
      'ffmpeg',
      '-i', video_path,
      '-i', audio_path,
      '-c:v', 'copy',
      '-c:a', 'aac',
      '-strict', 'experimental',
      temp_path
    ]
    
    logger.info(f"adding audio from {audio_path} to {video_path}")
    # Run the FFmpeg command
    subprocess.run(ffmpeg_command, check=True)
    
    # Replace the original file with the temporary file
    os.replace(temp_path, video_path)
    
    logger.info(f"Video and audio combined successfully. Output file: {video_path}")

def add_subtitles(video_path,sutitle_path,temp_path):
    """
    Add subtitles to a video file using ffmpeg.

    :param video_path: Path to the input video file.
    :param subtitle_path: Path to the subtitle file (e.g., .srt).
    :param output_path: Path where the output video with subtitles will be saved.
    """
    # FFmpeg command to combine video and subtitle
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-i', sutitle_path,
        '-c', 'copy',
        '-c:s', 'move_text',
        temp_path
      ]
    
    logger.info(f"adding subtitles from {sutitle_path} to {video_path} ...")
    # Run the FFmpeg command
    subprocess.run(ffmpeg_command, check=True)
      
    # Replace the original file with the temporary file
    os.replace(temp_path, video_path)
      
    logger.info(f"Video and subtitle combined successfully. Output file: {video_path}")
