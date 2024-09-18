import json
import random
import requests
import logging
import os
import shutil
import time
from quart import url_for
from pytubefix.exceptions import AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable, RegexMatchError
from youtube_urls_validator import validate_url
from settings import MAX_DOWNLOAD_SIZE, TEMP_DIR, CODECS, AUTH

logger = logging.getLogger(__name__)

def get_free_mem() -> int:
  disc = shutil.disk_usage('/')
  return disc[2]

def get_first_item(my_list):
    return my_list[0] if my_list else None

def remove_duplicates(items):
  return list(set(items))

def get_avaliable_resolutions(yt):
    return sorted(remove_duplicates(filter(lambda x: x is not None, [stream.resolution for stream in yt.streams.filter(file_extension='mp4', adaptive=True)])), key= lambda char: int(char[:-1]),reverse=True)

def get_avaliable_bitrates(yt):
    return sorted(remove_duplicates(filter(lambda x: x is not None, [stream.abr for stream in yt.streams.filter(only_audio=True)])), key= lambda char: int(char[:-4]),reverse=True)

def get_avaliable_captions(yt):
    return sorted(remove_duplicates(filter(lambda x: x is not None, [caption.code for caption in yt.captions])), key= lambda char: char,reverse=True)

def filter_stream_by_codec(streams, codec):
    return [stream  for stream in streams if codec in stream.video_codec]
    


def is_valid_youtube_url(url):
    #pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    try:
      if validate_url(url=url):
         return True
    except:
      return False
      #return re.match(pattern, url) is not None
    
def get_proxies():
    if AUTH:
      try:
        payload = {
          "request": "display_proxies",
          "protocol": "http",
          "proxy_format": "protocolipport",
          "format": "text",
          "anonymity": "Elite,Anonymous",
          "timeout": 150
        }
        response = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get", params=payload)
        logger.info(f"fetching proxies from {response.url}")
        response.raise_for_status()
        if response.status_code == 200:
          proxy_list = requests.text.split("\n")
          if len(proxy_list) >= 10:
            proxy_list = proxy_list[:10]
          else:
            proxy_list = proxy_list
      except requests.exceptions.HTTPError as e:
        logger.error(f"An error occored fetching proxy list from {response.url}:\n  {e.args[0]}")
        return {}
      except requests.exceptions.Timeout as e:
        logger.error(f"Connection timed out when fetching proxy list from {response.url}:\n {e}")
        return {}
      else:
        proxy = random.choice(proxy_list)
        return {
          "http": proxy,
          "https": proxy
        }
    else:
      logger.info(f"Cannot use proxies with authentication")
      return {}

def get_info(yt):
    try:
        video_info = {
            "id": yt.video_id,
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "resolutions": get_avaliable_resolutions(yt),
            "bitrates": get_avaliable_bitrates(yt),
            "subtitles": get_avaliable_captions(yt),
            "watch_url": yt.watch_url,
            "thumbnail_url": yt.thumbnail_url,
            "keywords": yt.keywords,
            "channel_id": yt.channel_id,
            "channel_url": yt.channel_url,
            "description": yt.description,
            "publish_date": yt.publish_date,
            "url": {
                "video": {stream.resolution: stream.url for stream in yt.streams.filter(progressive=True)},
                "audio": {stream.abr: stream.url for stream in yt.streams.filter(only_audio=True)}
            }
        }
        return video_info, None
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None, str(e)

def validate_download(stream):
  if stream.filesize_approx <= MAX_DOWNLOAD_SIZE:
      filesize = stream.filesize
      logger.info(f"stream filesize is {filesize / 1024**3}mb storage left on server is {get_free_mem() / 1024 ** 3}mb")
      if filesize <= get_free_mem():
            logger.info(f"stream filesize is {filesize / 1024*3}mb storage left on server is {get_free_mem() / 1024 ** 3}mb")
            return True, None
      return False, "Not enough memory on the server try agin later"
  return None, f"File excedds max download size of {MAX_DOWNLOAD_SIZE}"
    

def download_content(yt, resolution="", bitrate="", content_type="video"):
    try:
        #yt = YouTube(url, use_oauth=AUTH, allow_oauth_cache=True, on_progress_callback = on_progress)
        if content_type.lower() == "video":
            if resolution:
                streams = yt.streams.filter(file_extension='mp4',adaptive=True, resolution=resolution)
                stream = get_first_item(filter_stream_by_codec(streams, CODECS[0]))
            else:
                streams = yt.streams.filter(file_extension='mp4', adaptive=True).order_by('resolution').desc()
               # print(streams)
                stream = get_first_item(filter_stream_by_codec(streams, CODECS[0]))
              #  print(f"stream:>>> {stream}")
            if stream:
                is_vald, error = validate_download(stream)
                if is_vald:
                    video_file = stream.download(output_path=TEMP_DIR)
                    return video_file, None
                else:
                  return None, error
            else:
                available_resolutions = get_avaliable_resolutions(yt)
                return None, f"Video with the specified resolution not found. Avaliable resolutions are: {available_resolutions}"
        elif content_type.lower() == "audio":
            if bitrate:
              stream = yt.streams.filter(only_audio=True, abr=bitrate).first()
            else:
              stream = yt.streams.get_audio_only()
            if stream:
                is_vald, error = validate_download(stream)
                if is_vald:
                    audio_file = stream.download(output_path=TEMP_DIR, mp3=True)
                    return audio_file, None
                else:
                    return None, error
            else:
                available_bitrates = get_avaliable_bitrates(yt)
                return None, f"Audio stream with the specified bitrate not found. Avaliable bitrates are: {available_bitrates}"
        else:
            return None, "Invalid content type specified. Use 'video' or 'audio'."
        
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
        logger.error(f"Error downloding {content_type} content: {e}")
        return None, e.error_string

def get_captions(yt,lang):
    try:
      #yt = YouTube(url, use_oauth=AUTH, allow_oauth_cache=True,on_progress_callback=on_progress)
      caption = yt.captions.get_by_language_code(lang)
      if caption:
        lang = caption.code
      else:
        caption = yt.captions.get_by_language_code(f"a.{lang}")
        if caption:
          lang = f"Autogenerated {caption.code}"
      if caption:
        caption.save_captions(os.path.join(TEMP_DIR, f"{yt.title}.srt"))
        caption_file = url_for('get_file', filename=f"{yt.title}.srt", _external=True)
        return {"lang": lang, "captions": caption.generate_srt_captions(), "file":caption_file, "path":os.path.join(TEMP_DIR, f"{yt.title}.srt")}, None
      else:
        return None, f"No captions found. Avaliable captions are: {get_avaliable_captions(yt)}"
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error gettinh caption content: {e}")
      return None, e.error_string

def delete_file_after_delay(file_path, delay):
    time.sleep(delay)
    if os.path.exists(file_path):
        logger.info("Deleting temp file " + file_path)
        os.remove(file_path)


def write_creds_to_file(access_token, refresh_token, expires, visitor_data, po_token, file_path):
    if os.path.exists(file_path): return
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires": int(expires),
        "visitorData": visitor_data,
        "po_token": po_token
    }
    with open(file_path, 'w') as file:
        logger.info("writing creds")
        json.dump(data, file, indent=2)
