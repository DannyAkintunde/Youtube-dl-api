from quart import Quart, request, jsonify, url_for, send_file
from pytubefix import YouTube, Search
from pytubefix.cli import on_progress
from pytubefix.exceptions import AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable, RegexMatchError
from apscheduler.schedulers.background import BackgroundScheduler
from editor import combine_video_and_audio, add_subtitles
from utils import remove_duplicates, get_avaliable_resolutions, get_avaliable_bitrates, get_avaliable_captions, get_proxies,is_valid_youtube_url, get_info, download_content, get_captions, delete_file_after_delay, write_creds_to_file
from settings import DEBUG, AUTH, ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES, VISITOR_DATA, PO_TOKEN, MAX_DOWNLOAD_SIZE, TEMP_DIR, AUTH_DIR, AUTH_FILE_NAME, EXPIRATION_DELAY
import re
import os
import time
import threading
import logging
import asyncio

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

setup_logging()

logger= logging.getLogger(__name__)

app = Quart(__name__)

if AUTH:
      os.makedirs(TEMP_DIR, exist_ok=True)
      os.makedirs(AUTH_DIR, exist_ok=True)
      AUTH_FILE_PATH = os.path.join(AUTH_DIR,AUTH_FILE_NAME)
      logger.info(f"auth file path {AUTH_FILE_PATH}")
      write_creds_to_file(ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES, VISITOR_DATA, PO_TOKEN, AUTH_FILE_PATH)

bitrate_regrex = '\d{2,3}kbps'
resolution_regrex = '\d{3,}p'
lang_code_regrex = '^((a\.)?[a-z]{2})(-[A-Z]{2})?$'


@app.route("/ping")
async def handle_ping():
    return jsonify({"message":"pong"}), 200

def parse_search_results(results):
    parsed_results = []
    if results and len(results) > 0:
      for result in results:
        video_info, e = get_info(result)
        if video_info:
          parsed_results.append(video_info)
    return parsed_results


@app.route('/search', methods=['GET'])
async def search():
    data = request.args or await request.get_json()
    if not data:
      return jsonify({"error": "No prameters passed"}), 500
    q = data.get('q') or data.get('query')
    
    if not q:
      return jsonify({"error": "Missing 'query'/'q' parameter in the request body."}), 400
    
    try:
        s = Search(q, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH)
        results = s.videos
        parsed_results = parse_search_results(results)
        print(parsed_results)
        if parsed_results and len(parsed_results) > 0:
          res = {
            "search": q,
            "search_suggestions": s.completion_suggestions,
            "lenght": len(parsed_results),
            "results": parsed_results
          }
          return jsonify(res), 200
        else:
          return jsonify({"error":"No results found."}), 400
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error geting videos info: {e}")
      return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"Error searching query: {e}")
        return jsonify({"error": f"An error occored please report this to the devloper.: {e}"}), 500

@app.route('/info', methods=['GET'])
async def video_info():
    data = request.args or await request.get_json()
    if not data:
      return jsonify({"error": "No prameters passed"}), 500
    
    url =  data.get('url')
    
    if not url:
      return jsonify({"error": "Missing 'url' parameter in the request body."}), 400
    
    if not is_valid_youtube_url(url): 
      return jsonify({"error": "Invalid YouTube URL."}), 400
    
    try:
      yt = YouTube(url, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH)
      video_info, error = get_info(yt)
      
      if video_info:
        return jsonify(video_info), 200
      else:
        return jsonify({"error": error}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error geting video info: {e}")
      return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored searching content:{e}")
        return jsonify({"error": f"Server error : {e}"}), 500
      

@app.route('/download', methods=['POST'])
async def download_highest_avaliable_resolution():
    data = await request.get_json()
    url = data.get('url')
    subtitle = data.get('subtitle') or data.get('caption')
    burn = subtitle.get('burn')
    lang = subtitle.get('lang')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    if lang:
      if not re.match(lang_code_regrex, lang):
        return jsonify({"error": "Invalid lang code"}), 400
    
    try:
      yt = YouTube(url, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH,on_progress_callback = on_progress)
      video_file, error_message = await asyncio.to_thread(download_content,yt)
      if not error_message:
          audio_file, error_message = await asyncio.to_thread(download_content, yt, content_type="audio")
          if audio_file:
              await asyncio.to_thread(combine_video_and_audio, video_file,audio_file,os.path.join(TEMP_DIR,f"temp_{os.path.basename(video_file)}"))
              #combine_video_and_audio( video_file,audio_file,os.path.join(TEMP_DIR,f"temp_{os.path.basename(video_file)}"))
              if subtitle:
                caption, error_message = await asyncio.to_thread(get_captions, yt, lang)
                if caption:
                  await asyncio.to_thread(add_subtitles, video_file, caption["path"], os.path.join(TEMP_DIR,f"temp_{os.path.basename(video_file)}"), burn, lang)
                  threading.Thread(target=delete_file_after_delay, args=(caption["path"], EXPIRATION_DELAY)).start()
                  del caption["path"]
                  
              threading.Thread(target=delete_file_after_delay, args=(audio_file, EXPIRATION_DELAY)).start()
         
      
      if video_file:
          threading.Thread(target=delete_file_after_delay, args=(video_file, EXPIRATION_DELAY)).start()
          if data.get("link"):
            download_link =  url_for('get_file', filename=os.path.basename(video_file), _external=True)
            return jsonify({"download_link": download_link}), 200
          else:
            return await send_file(video_file, as_attachment=True), 200
      else:
          return jsonify({"error": error_message}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
        logger.error(f"Error geting downloading video: {e}")
        return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{e}")
        return jsonify({"error": f"Server error : {e}"}), 500


@app.route('/download/<resolution>', methods=['POST'])
async def download_by_resolution(resolution):
    data = await request.get_json()
    url = data.get('url')
    bitrate = data.get('bitrate')
    subtitle = data.get('subtitle') or data.get('caption')
    if isinstance(subtitle, dict):
      burn = subtitle.get('burn')
      lang = subtitle.get('lang')
    else:
      lang = subtitle
      burn = True
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
        
    if not re.match(resolution_regrex,resolution):
        return jsonify({"error": "Invald request URL, input a valid resolution for example 360p"}), 400
    if bitrate:
        if not re.match(bitrate_regrex,bitrate):
            return jsonify({"error": "Invalid request URL, input a valid bitrate for example 48kbps"}), 400
    if lang:
      if not re.match(lang_code_regrex, lang):
        return jsonify({"error": "Invalid lang code"}), 400
        
    try:
      yt = YouTube(url, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress)
      video_file, error_message = await asyncio.to_thread(download_content, yt, resolution)
      if not error_message:
          if bitrate:
            audio_file, error_message = await asyncio.to_thread(download_content, yt, content_type="audio", bitrate=bitrate)
          else:
            audio_file, error_message = await asyncio.to_thread(download_content, yt, content_type="audio", bitrate="")
          if audio_file:
              await asyncio.to_thread(combine_video_and_audio, video_file,audio_file,os.path.join(TEMP_DIR,f"temp_{os.path.basename(video_file)}"))
              if subtitle:
                caption, error_message = await asyncio.to_thread(get_captions, yt, lang)
                if caption:
                  await asyncio.to_thread(add_subtitles, video_file, caption["path"], os.path.join(TEMP_DIR,f"temp_{os.path.basename(video_file)}"), burn, lang)
                  threading.Thread(target=delete_file_after_delay, args=(caption["path"], EXPIRATION_DELAY)).start()
                  del caption["path"]
              threading.Thread(target=delete_file_after_delay, args=(audio_file, EXPIRATION_DELAY)).start()
                   
      if video_file:
          threading.Thread(target=delete_file_after_delay, args=(video_file, EXPIRATION_DELAY)).start()
          if data.get("link"):
            download_link =  url_for('get_file', filename=os.path.basename(video_file), _external=True)
            return jsonify({"download_link": download_link}), 200
          else:
            return await send_file(video_file, as_attachment=True), 200
      else:
          return jsonify({"error": error_message}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
        logger.error(f"Error geting downloading video: {e}")
        return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{e}")
        return jsonify({"error": f"Server error : {e}"}), 500
  
@app.route('/download_audio', methods=['POST'])
async def download_highest_quality_audio():
    data = await request.get_json()
    url = data.get('url')
  
    if not url:
      return jsonify({"error": "Missing 'url' parameter in the request body."}), 400
  
    if not is_valid_youtube_url(url):
      return jsonify({"error": "Invalid YouTube URL."}), 400
    try:
      yt = YouTube(url, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress)
      audio_file, error_message = await asyncio.to_thread(download_content, yt, content_type="audio")
        
      if audio_file:
          threading.Thread(target=delete_file_after_delay, args=(audio_file, EXPIRATION_DELAY)).start()
          if data.get("link"):
              download_link =  url_for('get_file', filename=os.path.basename(audio_file), _external=True)
              return jsonify({"download_link": download_link}), 200
          else:
              return await send_file(audio_file, as_attachment=True), 200
      else:
          return jsonify({"error": error_message}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error getting audio content: {e}")
      return jsonify({ "error": e.error_string }), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{e}")
        return jsonify({"error": f"Server error : {e}"}), 500
      

@app.route('/download_audio/<bitrate>', methods=['POST'])
async def download_audio_by_bitrate(bitrate):
    data = await request.get_json()
    url = data.get('url')
    
    if not url:
      return jsonify({"error": "Missing 'url' parameter in the request body."}), 400
  
    if not is_valid_youtube_url(url):
      return jsonify({"error": "Invalid YouTube URL."}), 400
 
    if not re.match(f"{bitrate_regrex}",bitrate):
       return jsonify({"error": "Invalid request URL, input a valid bitrate for example 48kpbs fuck you"}), 400
 
    try:
      yt = YouTube(url, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress)
      audio_file, error_message = await asyncio.to_thread(download_content, yt, content_type="audio", bitrate=bitrate)
        
      if audio_file:
          threading.Thread(target=delete_file_after_delay, args=(audio_file, EXPIRATION_DELAY)).start()
          if data.get("link"):
              download_link =  url_for('get_file', filename=os.path.basename(audio_file), _external=True)
              return jsonify({"download_link": download_link}), 200
          else:
              return await send_file(audio_file, as_attachment=True), 200
      else:
          return jsonify({"error": error_message}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error getting audio content: {e}")
      return jsonify({ "error": e.error_string }), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{e}")
        return jsonify({"error": f"Server error : {e}"}), 500
 
@app.route('/captions/<lang>',methods=["GET"])
async def get_subtitles(lang):
    lang = lang.lower()
    data = request.args or await request.get_json()
    if not data:
      return jsonify({"error": "No prameters passed"}), 500
    
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400
  
    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    if not re.match(lang_code_regrex,lang):
        return jsonify({"error": "Invalid lang code"}), 400
    try:
      yt = YouTube(url, proxies=get_proxies(), use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress)
      captions, error_message = await asyncio.to_thread(get_captions,yt,lang)
      del captions["path"]
      if captions:
        return jsonify(captions), 200
      else:
        return jsonify({"error":error_message}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error getting caption content: {e}")
      return jsonify({ "error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {e}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{e}")
        return jsonify({"error": f"Server error : {e}"}), 500


@app.route('/temp_file/<filename>', methods=['GET'])
async def get_file(filename):
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return await send_file(file_path, as_attachment=True)
    else:
        logger.warning(f"Requested file not found: {filename}")
        return jsonify({"error": "File not found"}), 404


def clear_temp_directory():
  logging.info("Clearing temp files")
  now = time.time()
  for filename in os.listdir(TEMP_DIR): 
    file_path = os.path.join(TEMP_DIR, filename) 
    try:
      file_age = now - os.path.getmtime(file_path)
      if os.path.isfile(file_path) and file_age > 86400:
        os.remove(file_path)
        logger.info(f"sucessfull deleted {file_path}")
    except Exception as e: 
      logger.error(f'Failed to delete {file_path}. Reason: {e}')
  logger.info("Temp files cleared")


if __name__ == '__main__':
    if not DEBUG:
      scheduler = BackgroundScheduler()
      scheduler.add_job(clear_temp_directory, "interval", days=1)
      scheduler.start()
    app.run(debug=DEBUG)
