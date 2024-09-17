import os

# DEBUG mode: Determines if debugging is enabled. Defaults to True if not set.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# AUTH: Determines if authentication is required. Defaults to False if not set.
AUTH = os.environ.get("AUTH", "False") == "True"

# MAX_DOWNLOAD_SIZE: Maximum size (in bytes) allowed for downloads. Defaults to 2 GB if not set.
MAX_DOWNLOAD_SIZE = int(os.environ.get("MAX_SIZE", 2_147_483_648))

# EXPIRATION_DELAY: Time (in seconds) before a resource expires. Defaults to 30 minutes (1800 seconds) if not set.
EXPIRATION_DELAY = int(os.environ.get("EXPIRATION", 1800))

# TEMP_DIR: Directory name for storing temporary files such as videos and audios.
TEMP_DIR = 'temp_files'

# CODECS: List of supported codecs. Defaults to "avc1,acc" if not set, split into a tuple.
CODECS = tuple(os.environ.get("CODECS", "avc1,acc").split(","))
