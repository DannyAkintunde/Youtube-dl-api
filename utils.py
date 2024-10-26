import json
import random
import requests
import logging
import os
import shutil
import time
from langcodes import find
from quart import url_for
# from pytubefix.exceptions import AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable, RegexMatchError
from youtube_urls_validator import validate_url
# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import JSONFormatter, SRTFormatter, TextFormatter
from urllib.parse import urlparse, parse_qs
from settings import MAX_DOWNLOAD_SIZE, TEMP_DIR, CODECS, AUTH, VISITOR_DATA, PO_TOKEN, PROXY, DEBUG

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

def get_proxies():
    reason = "AUTH = False"
    if AUTH:
        reason = "No proxies available"
        if PROXIES:
            logger.info("Using proxies")
            proxies_list = []
            for proxy in PROXIES:
                proxy_dict = {}
                data = proxy.split('@')
                if len(data) == 2:
                    userdata = data[0].split('://')
                    protocol = userdata[0]
                    server = f'{protocol}://{data[1]}'
                    username_password = userdata[1].split(':')
                    username = username_password[0] if len(username_password) > 0 else ''
                    password = username_password[1] if len(username_password) > 1 else ''
                    proxy_dict['server'] = server
                    proxy_dict['username'] = username
                    proxy_dict['password'] = password
                else:
                    proxy_dict['server'] = data[0]  # No authentication case
                proxies_list.append(proxy_dict)
            return proxies_list
    logger.warning("Not using proxies because {}".format(reason))
    return []

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

def is_valid_language(value):
    try:
        find(value)
        return True
    except:
      return False

"""    
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
          proxy_list = response.text.split("\n")
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
"""


def video_id(value):
    if not value return
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    raise ValueError


def get_info(yt):
    try:
        video_info = yt.dict()
        video_info['video_id'] = video_id(video_info.get('view_url'))
        return video_info, None
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None, str(e)


def validate_download(stream):
  if stream.filesize_approx <= MAX_DOWNLOAD_SIZE:
      filesize = stream.filesize
      logger.info(f"stream filesize is {filesize / 1024**3}mb storage left on server is {get_free_mem() / 1024 ** 3}mb")
      if filesize <= get_free_mem():
            logger.info(f"stream filesize is {filesize / 1024**3}mb storage left on server is {get_free_mem() / 1024 ** 3}mb")
            return True, None
      return False, "Not enough memory on the server try agin later"
  return None, f"File excedds max download size of {MAX_DOWNLOAD_SIZE}"
    

def download_content(yt, resolution: str ="", bitrate: str ="", frame_rate: int =30, content_type: str ="video", hdr: bool | None =None):
    try:
        #yt = YouTube(url, use_oauth=AUTH, allow_oauth_cache=True, on_progress_callback = on_progress)
        stream = None
        if content_type.lower() == "video":
            if resolution:
                streams = yt.streams.filter(is_video=True, frame_rate=frame_rate, resolution=resolution, hdr=(hdr if hdr != None else None))
                streams.order_by('hdr')
                if len(streams) > 0:
                    stream = streams.first()
            else:
                stream = yt.streams.get_highest_resolution()
            if stream:
                is_valid, error = True, None # validate_download(yt)
                if is_valid:
                    return stream, None
                else:
                  return None, error
            else:
                available_resolutions = yt.streams.get_available_resolutions()
                available_frame_rates = yt.streams.get_highest_frame_rates()
                return None, f"Video with the specified resolution of frame rate not found. Avaliable resolutions are: {available_resolutions} and frame rates are {available_frame_rates}"
        elif content_type.lower() == "audio":
            if bitrate:
              stream = yt.streams.filter(only_audio=True, abr=bitrate).first()
            else:
              stream = yt.streams.get_audio_only()
            if stream:
                is_valid, error = True, None # validate_download(stream)
                if is_valid:
                    return stream, None
                else:
                    return None, error
            else:
                available_bitrates = yt.streams.get_available_bit_rates()
                return None, f"Audio stream with the specified bitrate not found. Avaliable bitrates are: {available_bitrates}"
        else:
            return None, "Invalid content type specified. Use 'video' or 'audio'."
        
    except Exception as e:
        logger.error(f"Error downloding {content_type} content: {e}")
        return None, f'An error occored: {e} if you are seeing this message please contact administrator or open a issue at github.com/DannyAkintunde/Youtube-dl-api'

def get_captions(yt,lang, translate=False):
    try:
      #yt = YouTube(url, use_oauth=AUTH, allow_oauth_cache=True,on_progress_callback=on_progress)
      
      # transcripts = YouTubeTranscriptApi.list_transcripts(yt.video_id, proxies = proxies)
      captions = yt.captions
      if not translate:
          caption = captions.get_captions_by_lang_code(lang)
          # transcript = transcripts.find_transcript([lang])
      else:
          caption = captions.get_translated_captions_by_lang_code(lang)
      
      if caption:
          return caption, None
      else:
        return None, f"No captions found. Avaliable captions are: {captions.captions} and Translations are {captions.translations}"
    except Exception as e:
      logger.error(f"Error getting caption content: {e}")
      return None, repr(e)

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
    logger.debug(f"creds content: {data}")
    with open(file_path, 'w') as file:
        logger.info("writing creds")
        json.dump(data, file, indent=2)

def fetch_po_token():
  return VISITOR_DATA, PO_TOKEN
  
