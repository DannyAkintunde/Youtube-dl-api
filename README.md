
# YouTube-dl-api: YouTube Content Downloader API 🎥

A Quart-based API for downloading YouTube videos and audio, retrieving video metadata, and handling captions. This API allows you to interact with YouTube content programmatically, leveraging background tasks to manage temporary files and provide efficient downloads.

## Features ✨

- **Download Videos and Audio:** Retrieve content with specified resolutions and bitrates.
- **Retrieve Video Metadata:** Get details such as title, views, and channel information.
- **Handle Captions:** Fetch and save captions in SRT format.
- **Check Storage:** Ensure sufficient storage space before downloading.

## Requirements 📋

- Python 3.7+
- FFmpeg
- `requirements.txt` dependencies

## Installation 🚀

1. **Clone the Repository**

   ```bash
   git clone https://github.com/DannyAkintunde/YouTube-dl-api
   cd Youtube-dl-api
   ```

2. **Run the Installation Script**

   Execute the `install.sh` script to install Python dependencies and system packages:

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   This script will:
   - Install Python dependencies listed in `requirements.txt`
   - Update the package list
   - Install FFmpeg
   - Verify the FFmpeg installation

## Configuration ⚙️

Adjust configuration settings in the `settings.py` file:

- `DEBUG`: Enable or disable debug mode (default: `True`).
- `AUTH`: Configure authentication (default: `False`).
- `MAX_DOWNLOAD_SIZE`: Maximum file size for downloads (default: 2 GiB).
- `EXPIRATION_DELAY`: Delay for expiring temporary files (default: 1800 seconds).
- `TEMP_DIR`: Directory for storing temporary files.
- `CODECS`: List of video and audio codecs to use (default: `avc1,mp4a`).

## API Endpoints 🌐

### Health Check

**GET** `/ping`

**Description:** Checks the API status.

**Response:**

```json
{
  "message": "pong"
}
```

- `200 OK`: `{"message": "pong"}`

### Search

**GET** `/search`

**Description:** Searches for YouTube videos based on a query.

**Query Parameters:**

- `q` or `query`: Search query.

**Example Request:**

```http
GET /search?q=python+tutorial
```

**Example Response:**

```json
{
  "search": "python tutorial",
  "search_suggestions": ["python tutorial 2024", "python programming for beginners"],
  "length": 10,
  "results": [
    {
      "title": "Python Tutorial for Beginners",
      "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
      "description": "Learn Python programming from scratch.",
      "views": "1,234,567",
      "channel": "ProgrammingBasics",
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg"
    }
  ]
}
```

- `200 OK`: Search results.
- `400 Bad Request`: Missing or invalid query parameter.
- `500 Internal Server Error`: Server-side error.

### Video Info

**GET** `/info`

**Description:** Retrieves metadata for a YouTube video.

**Query Parameters:**

- `url`: The URL of the YouTube video.

**Example Request:**

```http
GET /info?url=https://youtube.com/watch?v=dQw4w9WgXcQ
```

**Example Response:**

```json
{
  "title": "Python Tutorial for Beginners",
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "description": "Learn Python programming from scratch.",
  "views": "1,234,567",
  "channel": "ProgrammingBasics",
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg",
  "length": "15:30",
  "upload_date": "2024-01-01"
}
```

- `200 OK`: Video metadata.
- `400 Bad Request`: Invalid URL or missing parameter.
- `500 Internal Server Error`: Server-side error.

### Download Video

**POST** `/download`

**Description:** Downloads YouTube content with the highest available resolution.

**Request Body:**

```json
{
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "subtitle": {
    "burn": true,
    "lang": "en"
  },
  "link": false
}
```

**Example Response (File Download):**

- If `link` is `false`:

  The response will be a file download.

- If `link` is `true`:

```json
{
  "download_link": "http://example.com/temp_file/temp_Python_Tutorial_for_Beginners.mp4"
}
```

- `200 OK`: Download link or file.
- `400 Bad Request`: Invalid URL or parameters.
- `500 Internal Server Error`: Server-side error.

### Download by Resolution

**POST** `/download/<resolution>`

**Description:** Downloads YouTube content with a specified resolution.

**Request Body:**

```json
{
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "bitrate": "128kbps",
  "subtitle": {
    "burn": true,
    "lang": "en"
  },
  "link": false
}
```

**Example Response (File Download):**

- If `link` is `false`:

  The response will be a file download.

- If `link` is `true`:

```json
{
  "download_link": "http://example.com/temp_file/temp_Python_Tutorial_360p.mp4"
}
```

- `200 OK`: Download link or file.
- `400 Bad Request`: Invalid resolution, bitrate, or URL.
- `500 Internal Server Error`: Server-side error.

### Download Audio

**POST** `/download_audio`

**Description:** Downloads YouTube audio with the highest quality.

**Request Body:**

```json
{
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "link": false
}
```

**Example Response (File Download):**

- If `link` is `false`:

  The response will be a file download.

- If `link` is `true`:

```json
{
  "download_link": "http://example.com/temp_file/temp_Python_Tutorial.mp3"
}
```

- `200 OK`: Download link or file.
- `400 Bad Request`: Invalid URL.
- `500 Internal Server Error`: Server-side error.

### Download Audio by Bitrate

**POST** `/download_audio/<bitrate>`

**Description:** Downloads YouTube audio with a specified bitrate.

**Request Body:**

```json
{
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "link": false
}
```

**Example Response (File Download):**

- If `link` is `false`:

  The response will be a file download.

- If `link` is `true`:

```json
{
  "download_link": "http://example.com/temp_file/temp_Python_Tutorial_48kbps.mp3"
}
```

- `200 OK`: Download link or file.
- `400 Bad Request`: Invalid bitrate or URL.
- `500 Internal Server Error`: Server-side error.

### Get Captions

**GET** `/captions/<lang>`

**Description:** Retrieves captions for a YouTube video.

**Query Parameters:**

- `url`: The URL of the YouTube video.

**Example Request:**

```http
GET /captions/en?url=https://youtube.com/watch?v=dQw4w9WgXcQ
```

**Example Response:**

```json
{
  "lang": "en",
  "captions": [
    {
      "start": "00:00:01",
      "end": "00:00:05",
      "text": "Welcome to the Python tutorial!"
    }
  ],
  "path": "/path/to/captions/file.srt"
}
```

- `200 OK`: Captions data.
- `400 Bad Request`: Invalid URL or language code.
- `500 Internal Server Error`: Server-side error.

### Get Temporary File

**GET** `/temp_file/<filename>`

**Description:** Retrieves a temporary file.

**Parameters:**

- `filename`: The name of the file.

**Example Request:**

```http
GET /temp_file/temp_Python_Tutorial_for_Beginners.mp4
```

**Example Response:**

- If the file exists, the response will be the file download.

- If the file does not exist:

```json
{
  "error": "File not found"
}
```

- `200 OK`: File download.
- `404 Not Found`: File not found.

## Running the API 🏃‍♂️

To run the API, use:

```bash
python main.py
```

## Background Tasks 🕒

- **Clearing Temporary Files:** The application schedules a task to clear temporary files older than 24 hours.

## Troubleshooting 🛠️

- Check `app.log` for detailed error messages.
- Ensure the `TEMP_DIR` has appropriate permissions.
- Validate YouTube URLs and parameters in API requests.

## License

This project is licensed under the AGPL-3 License. See the [`LICENSE`](LICENSE) file for details.
