import os

# DEBUG mode: Determines if debugging is enabled. Defaults to True if not set.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# AUTH: Determines if authentication is required. Defaults to False if not set.
AUTH = os.environ.get("AUTH", "False") == "True"

#fill if auth is true
ACCESS_TOKEN =  os.environ.get("ACCESS_TOKEN", "ya29.a0AcM612zOF-QP8C-mhPX6MfdeauIkYXo3VHT80yzTN0O2350n_8pSrgZdGV4q6XlQYOJNbrz-xN4NgllBTeMhvT47LICkXIGR8Z_9Bzb3lWEbXZWZvmUp5Ue40sfpgUT9Cay0L84nQfGRG39uWKMdmlQgx4bMoUSKK0xAlMiexgzJF9K6GmGoaCgYKAS8SARMSFQHGX2Mi3_po5jSxzMN3YncC3dsSbg0187")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN", "1//03q0cSea2PlBDCgYIARAAGAMSNwF-L9IrHHrwFHn9Qav0AWDpJvdFZ8R5-mNc_GE0tNn3l6hDEQ2i4ictQXUwqDQ9-Ki0xjCvlLA")
EXPIRES = os.environ.get("EXPIRES", 1726619036)
VISITOR_DATA = os.environ.get("VISITOR_DATA", "CgtuZVAzWVIzX2R5WSiJ4qO3BjIKCgJORxIEGgAgJw%3D%3D")
PO_TOKEN = os.environ.get("PO_TOKEN", "MnRLRTG8kBazMEt9RGwvFceBv40KENnpHtlDrguGDKni7A-azrTC0L_GYy7Pz-fH6mqHFsS7CmHJ3c3g9Y6z-RqqRsbYhMeXWbiXmyTXLpKRXOkQFbgSjNeRohf9afkINW7suFEVcBe0OedclwPPNYTqkcXvKA==")

# MAX_DOWNLOAD_SIZE: Maximum size (in bytes) allowed for downloads. Defaults to 2 GB if not set.
MAX_DOWNLOAD_SIZE = int(os.environ.get("MAX_SIZE", 2_147_483_648))

# EXPIRATION_DELAY: Time (in seconds) before a resource expires. Defaults to 30 minutes (1800 seconds) if not set.
EXPIRATION_DELAY = int(os.environ.get("EXPIRATION", 1800))

# TEMP_DIR: Directory name for storing temporary files such as videos and audios.
TEMP_DIR = 'temp_files'
# AUTH_DIR: path to save auth file
AUTH_DIR = 'auth'
AUTH_FILE_NAME = 'temp.json'
# CODECS: List of supported codecs. Defaults to "avc1,acc" if not set, split into a tuple.
CODECS = tuple(os.environ.get("CODECS", "avc1,aac").split(","))
