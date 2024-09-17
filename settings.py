import os

DEBUG = os.environ.get("DEBUG", True)
AUTH = os.environ.get("AUTH", False)
MAX_DOWNLOAD_SIZE = os.environ.get("MAX_SIZE", 2_147_483_648)
EXPIRATION_DELAY = os.environ.get("EXPIRATION", 1800)
TEMP_DIR = 'temp_files'  # Directory to store temporary files (videos,audios e.t.c)
CODECS = tuple(os.environ.get("CODECS","avc1,acc").split(","))
