from quart import Quart, request, jsonify, url_for, send_file
from pytubefix import YouTube, Search
from pytubefix.cli import on_progress
from youtubesearchpython.__future__ import VideosSearch, ResultMode, Suggestions
from pytubefix.exceptions import AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable, RegexMatchError
from apscheduler.schedulers.background import BackgroundScheduler
from editor import combine_video_and_audio, add_subtitles
from utils import remove_duplicates, get_avaliable_resolutions, get_avaliable_bitrates, get_avaliable_captions ,is_valid_youtube_url, get_info, download_content, get_captions, delete_file_after_delay, write_creds_to_file, fetch_po_token
from settings import *
import re
import os
import time
import threading
import logging
import asyncio
import uuid

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
search_amount_reqrex = '\\b\d+\\b'


@app.route("/ping")
async def handle_ping():
    return jsonify({"message":"pong"}), 200



search_objs = {}

@app.route('/search', methods=['GET'])
async def search():
    data = request.args or await request.get_json()
    if not data:
      return jsonify({"error": "No prameters passed"}), 400
    q = data.get('q') or data.get('query')
    amount = data.get('amount') or DEFUALT_SEARCH_AMOUNT
    
    if not q:
      return jsonify({"error": "Missing 'query'/'q' parameter in the request body."}), 400
    
    if not (amount and re.match(search_amount_reqrex, str(amount))):
      return jsonify({"error": f"The amount parameter must be an integer between or equal to {MIN_SEARCH_AMOUNT} and {MAX_SEARCH_AMOUNT}"}), 400
    amount = int(amount)
    if not (amount >= MIN_SEARCH_AMOUNT and amount <= MAX_SEARCH_AMOUNT):
      return jsonify({"error": f"The amount parameter must be between or equal to {MIN_SEARCH_AMOUNT} and {MAX_SEARCH_AMOUNT}"}), 400
    
    
    try:
        s = VideosSearch(q, limit=amount)
        search_id = uuid.uuid4()
        response = await s.next()
        search_objs[str(search_id)] = s
        suggestions = await Suggestions.get(q)
        results = response['result']
        if response and results and len(results) > 0:
          res = {
            "search": q,
            "search_suggestions": suggestions['result'],
            "lenght": len(results),
            "results": results,
            "search_id": search_id
          }
          return jsonify(res), 200
        else:
          return jsonify({"error":"No results found.", "suggestions": suggestions['result']}), 400
    except Exception as e:
        logger.error(f"Error searching query: {repr(e)}")
        return jsonify({"error": f"An error occored please report this to the devloper.: {repr(e)}"}), 500

@app.route('/search/<search_id>')
async def next_page(search_id):
  try:
    uuid.UUID(search_id,version=4)
    s = search_objs[search_id]
    response = await s.next()
    if response:
      result = response['result']
      return jsonify({
        "length": len(result),
        "results": result,
        "search_id": search_id
      }), 200
    else: 
      logger.info(f"No pages foind for {str(search_id)}")
      return jsonify({"error": "No more pages"}), 400
  except ValueError as e:
    logger.error(f"Invalid search id Error: {repr(e)}")
    return jsonify({"error": "Invalid search id"}), 400
  except KeyError as e:
    logger.error(f"No search found for passed search id Error: {repr(e)}")
    return jsonify({"error": "No seaech found for search id"}), 400
  except Exception as e:
    logger.error(f"an error occore fetching search results : {repr(e)}")
    return jsonify({"error": f"An error occored if you are seing this message pleas report to the dev Error: {repr(e)}"})

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
      yt = YouTube(url,  use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, po_token_verifier=fetch_po_token)
      video_info, error = await asyncio.to_thread(get_info, yt)
      
      if video_info:
        return jsonify(video_info), 200
      else:
        return jsonify({"error": error}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error geting video info: {repr(e)}")
      return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {repr(e)}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored searching content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500
      

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
      yt = YouTube(url,  use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH,on_progress_callback = on_progress, po_token_verifier=fetch_po_token)
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
        logger.error(f"Error geting downloading video: {repr(e)}")
        return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {repr(e)}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500


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
      yt = YouTube(url,  use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress, po_token_verifier=fetch_po_token)
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
        logger.error(f"Error geting downloading video: {repr(e)}")
        return jsonify({"error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {repr(e)}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500
  
@app.route('/download_audio', methods=['POST'])
async def download_highest_quality_audio():
    data = await request.get_json()
    url = data.get('url')
  
    if not url:
      return jsonify({"error": "Missing 'url' parameter in the request body."}), 400
  
    if not is_valid_youtube_url(url):
      return jsonify({"error": "Invalid YouTube URL."}), 400
    try:
      yt = YouTube(url,  use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress, po_token_verifier=fetch_po_token)
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
      logger.error(f"Error getting audio content: {repr(e)}")
      return jsonify({ "error": e.error_string }), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {repr(e)}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500
      

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
      yt = YouTube(url,  use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress, po_token_verifier=fetch_po_token)
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
      logger.error(f"Error getting audio content: {repr(e)}")
      return jsonify({ "error": e.error_string }), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {repr(e)}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500
 
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
      yt = YouTube(url,  use_oauth=AUTH, allow_oauth_cache=True, use_po_token=AUTH, token_file = AUTH and AUTH_FILE_PATH, on_progress_callback = on_progress, po_token_verifier=fetch_po_token)
      captions, error_message = await asyncio.to_thread(get_captions,yt,lang)
      if captions:
        del captions["path"]
        return jsonify(captions), 200
      else:
        return jsonify({"error":error_message}), 500
    except (AgeRestrictedError, LiveStreamError, MaxRetriesExceeded, MembersOnly, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as e:
      logger.error(f"Error getting caption content: {repr(e)}")
      return jsonify({ "error": e.error_string}), 500
    except RegexMatchError as e:
        logger.error(f"an error occored fetching url: {repr(e)}")
        return jsonify({"error": "Invalid YouTube URL."}), 400
    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500


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
      logger.error(f'Failed to delete {file_path}. Reason: {repr(e)}')
  logger.info("Temp files cleared")


if __name__ == '__main__':
    if not DEBUG:
      scheduler = BackgroundScheduler()
      scheduler.add_job(clear_temp_directory, "interval", days=1)
      scheduler.start()
    app.run(debug=DEBUG)
