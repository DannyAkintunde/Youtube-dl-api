# YouTube Video Downloader API

## Overview

This Flask-based API provides functionality for searching YouTube videos, retrieving video information, downloading videos and audio, and fetching subtitles. It uses the `pytubefix` library for YouTube interactions and manages files in a temporary directory.

## Features

-   **Search for Videos:** Find YouTube videos based on a query.
-   **Retrieve Video Information:** Get details about a specific video.
-   **Download Videos:** Download videos in the highest resolution or a specific resolution.
-   **Download Audio:** Extract and download audio from a video.
-   **Get Subtitles:** Retrieve and download subtitles for a video in various languages.
-   **Manage Temporary Files:** Automatically deletes old temporary files to manage disk space.

## Endpoints

### 1. Search Videos

**Endpoint:** `/search`  
**Method:** `GET`  
**Description:** Searches for YouTube videos based on a query.

**Request Body:**

```json
{
    "q": "search query"
}
```

**Responses:**

-   `200 OK` - Successful search with results.
-   `400 Bad Request` - Missing or invalid query.
-   `500 Internal Server Error` - Error during the search process.

### 2. Get Video Info

**Endpoint:** `/video_info`  
**Method:** `GET`  
**Description:** Retrieves information about a YouTube video.

**Request Body:**

```json
{
    "url": "https://www.youtube.com/watch?v=example"
}
```

**Responses:**

-   `200 OK` - Video information retrieved successfully.
-   `400 Bad Request` - Missing or invalid URL.
-   `500 Internal Server Error` - Error retrieving video information.

### 3. Download Video (Highest Resolution)

**Endpoint:** `/download`  
**Method:** `POST`  
**Description:** Downloads the video in the highest available resolution.

**Request Body:**

```json
{
    "url": "https://www.youtube.com/watch?v=example",
    "link": true // Optional: If true, returns a download link instead of the file.
}
```

**Responses:**

-   `200 OK` - Video downloaded successfully or download link provided.
-   `400 Bad Request` - Missing or invalid URL.
-   `500 Internal Server Error` - Error during download.

### 4. Download Video by Resolution

**Endpoint:** `/download/<resolution>`  
**Method:** `POST`  
**Description:** Downloads the video in the specified resolution.

**Request Body:**

```json
{
    "url": "https://www.youtube.com/watch?v=example",
    "link": true // Optional: If true, returns a download link instead of the file.
}
```

**Responses:**

-   `200 OK` - Video downloaded successfully or download link provided.
-   `400 Bad Request` - Missing or invalid URL, or resolution not available.
-   `500 Internal Server Error` - Error during download.

### 5. Download Audio

**Endpoint:** `/download_audio`  
**Method:** `POST`  
**Description:** Downloads the audio track from a video.

**Request Body:**

```json
{
    "url": "https://www.youtube.com/watch?v=example",
    "link": true // Optional: If true, returns a download link instead of the file.
}
```

**Responses:**

-   `200 OK` - Audio downloaded successfully or download link provided.
-   `400 Bad Request` - Missing or invalid URL.
-   `500 Internal Server Error` - Error during download.

### 6. Get Subtitles

**Endpoint:** `/captions/<lang>`  
**Method:** `GET`  
**Description:** Retrieves subtitles for the video in the specified language.

**Request Body:**

```json
{
    "url": "https://www.youtube.com/watch?v=example"
}
```

**Responses:**

-   `200 OK` - Subtitles found and returned.
-   `400 Bad Request` - Missing or invalid URL, or no subtitles found.
-   `500 Internal Server Error` - Error retrieving subtitles.

### 7. Access Temporary Files

**Endpoint:** `/temp_file/<filename>`  
**Method:** `GET`  
**Description:** Allows downloading of temporary files such as videos and subtitles.

**Responses:**

-   `200 OK` - File found and successfully served.
-   `404 Not Found` - File does not exist.

## File Management

Temporary files are stored in the `temp_files` directory. Files are automatically deleted after 1 hour, and the directory is cleared of files older than 24 hours daily.

## Dependencies

-   Flask
-   pytubefix
-   apscheduler

## Running the Application

1. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

2. **Run the application:**
    ```sh
    python app.py
    ```

The application will start on `http://127.0.0.1:5000/` by default.

## License

This project is licensed under the MIT License.

## Author

DannyAkintunde
