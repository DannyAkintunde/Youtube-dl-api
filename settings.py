import os

# DEBUG mode: Determines if debugging is enabled. Defaults to True if not set.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# PROXY: list of proxies
PROXIES = os.environ.get("PROXIES","").split(",")

# AUTH: Determines if authentication is required. Defaults to False if not set.
AUTH = os.environ.get("AUTH", "False") == "True"

#fill if auth is true
ACCESS_TOKEN =  os.environ.get("ACCESS_TOKEN")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
EXPIRES = os.environ.get("EXPIRES")
VISITOR_DATA = os.environ.get("VISITOR_DATA")
PO_TOKEN = os.environ.get("PO_TOKEN")

# MAX_DOWNLOAD_SIZE: Maximum size (in bytes) allowed for downloads. Defaults to 2 GB if not set.
MAX_DOWNLOAD_SIZE = int(os.environ.get("MAX_SIZE", 2_147_483_648))
# MAX_VIDEO_LENGTH: Maximum allow video length in 
MAX_VIDEO_LENGTH = os.environ.get('MAX_LENGTH', '')
# MAX_SEARCH_AMOUNT: Maximum number of video search results.
MAX_SEARCH_AMOUNT = int(os.environ.get("MAX_SEARCH", 25))
# MAX_SEARCH_AMOUNT: Minimum number of video search results.
MIN_SEARCH_AMOUNT = int(os.environ.get("MAX_AMOUNT", 2))
# MAX_SEARCH_AMOUNT: Defualt number of video search results.
DEFUALT_SEARCH_AMOUNT = int(os.environ.get("DEFUALT_AMOUNT", 20))

# EXPIRATION_DELAY: Time (in seconds) before a resource expires. Defaults to 30 minutes (1800 seconds) if not set.
EXPIRATION_DELAY = int(os.environ.get("EXPIRATION", 1800))

# TEMP_DIR: Directory name for storing temporary files such as videos and audios.
TEMP_DIR = 'temp_files'
# AUTH_DIR: path to save auth file
AUTH_DIR = 'auth'
AUTH_FILE_NAME = 'temp.json'
# CODECS: List of supported codecs. Defaults to "avc1,acc" if not set, split into a tuple.
CODECS = tuple(os.environ.get("CODECS", "avc1,aac").split(","))
