
# YouTube-dl-api: YouTube Content Downloader API 🎥
! note readme is yet to be updated ⚠️

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
  
- `PROXY`: Configure proxies in the format of http_proxy,https_proxy.

- `AUTH`: Configure authentication (default: `False`).

- `ACCESS_TOKEN`: Token for accessing protected resources (required if `AUTH` is `True`).

- `REFRESH_TOKEN`: Token for refreshing access (required if `AUTH` is `True`).

- `EXPIRES`: Expiration time for the access token (required if `AUTH` is `True`).

- `VISITOR_DATA`: Data for visitor tracking (required if `AUTH` is `True`).

- `PO_TOKEN`: Token for purchase orders (required if `AUTH` is `True`).

- `MAX_DOWNLOAD_SIZE`: Maximum file size for downloads (default: `2 GiB`).

- `MAX_SEARCH_AMOUNT`: Maximum number of video search results (default: `25`).

- `MIN_SEARCH_AMOUNT`: Minimum number of video search results (default: `2`).

- `DEFAULT_SEARCH_AMOUNT`: Default number of video search results (default: `20`).

- `EXPIRATION_DELAY`: Delay for expiring temporary files (default: `1800 seconds`).

- `TEMP_DIR`: Directory for storing temporary files (default: `'temp_files'`).

- `AUTH_DIR`: Path to save authentication file (default: `'auth'`).

- `AUTH_FILE_NAME`: Name of the authentication file (default: `'temp.json'`).

- `CODECS`: List of video and audio codecs to use (default: `'avc1,aac'`).

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
  {
  "lenght": 20,
  "results": [
    {
      "accessibility": {
        "duration": "6 hours, 14 minutes, 7 seconds",
        "title": "Python Tutorial - Python Full Course for Beginners by Programming with Mosh 41,059,791 views 5 years ago 6 hours, 14 minutes"
      },
      "channel": {
        "id": "UCWv7vMbMWH4-V0ZXdmDpPBA",
        "link": "https://www.youtube.com/channel/UCWv7vMbMWH4-V0ZXdmDpPBA",
        "name": "Programming with Mosh",
        "thumbnails": [
          {
            "height": 68,
            "url": "https://yt3.ggpht.com/lCeCb47hCbXWFa0I4gi8uWDHzWSs7sjK4FDmk7lFEUMRNp6QRzIQOkwaKhwv7eNKZacRI2uR=s68-c-k-c0x00ffffff-no-rj",
            "width": 68
          }
        ]
      },
      "descriptionSnippet": [
        {
          "text": "Become a "
        },
        {
          "bold": true,
          "text": "Python"
        },
        {
          "text": " pro! This comprehensive "
        },
        {
          "bold": true,
          "text": "tutorial"
        },
        {
          "text": " takes you from beginner to hero, covering the basics, machine learning, and ..."
        }
      ],
      "duration": "6:14:07",
      "id": "_uQrJ0TkZlc",
      "link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
      "publishedTime": "5 years ago",
      "richThumbnail": {
        "height": 180,
        "url": "https://i.ytimg.com/an_webp/_uQrJ0TkZlc/mqdefault_6s.webp?du=3000&sqp=CLf547cG&rs=AOn4CLCAcnB5okiLttIEMkLM9bb-3w28AQ",
        "width": 320
      },
      "shelfTitle": null,
      "thumbnails": [
        {
          "height": 202,
          "url": "https://i.ytimg.com/vi/_uQrJ0TkZlc/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCQfkbApoaN-_QBOuiyHzWJOiziEA",
          "width": 360
        },
        {
          "height": 404,
          "url": "https://i.ytimg.com/vi/_uQrJ0TkZlc/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCpUFKfUMVNbg8mqTcZ8UdSUjpilw",
          "width": 720
        }
      ],
      "title": "Python Tutorial - Python Full Course for Beginners",
      "type": "video",
      "viewCount": {
        "short": "41M views",
        "text": "41,059,791 views"
      }
    }
    //...more results here
  ],
  "search": "python tutorial",
  "search_id": "00b5a31c-30d7-4d96-92e5-42b871062bca",
  "search_suggestions": [
    "python tutorial",
    "python tutorial for beginners",
    "python tutorial 2024"
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
  "author": "Rick Astley",
  "bitrates": [
    "160kbps",
    "128kbps",
    "70kbps",
    "50kbps"
  ],
  "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "channel_url": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
  "description": "The official video for “Never Gonna Give You Up” by Rick Astley. \n\nThe new album 'Are We There Yet?' is out now: Download here: https://RickAstley.lnk.to/AreWeThereYetFA/itunes\n\n“Never Gonna Give You Up” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick’s native UK and the US Billboard Hot 100.  It also won the Brit Award for Best single in 1988. Stock Aitken and Waterman wrote and produced the track which was the lead-off single and lead track from Rick’s debut LP “Whenever You Need Somebody”.  The album was itself a UK number one and would go on to sell over 15 million copies worldwide.\n\nThe legendary video was directed by Simon West – who later went on to make Hollywood blockbusters such as Con Air, Lara Croft – Tomb Raider and The Expendables 2.  The video passed the 1bn YouTube views milestone on 28 July 2021.\n\nSubscribe to the official Rick Astley YouTube channel: https://RickAstley.lnk.to/YTSubID\n\nFollow Rick Astley:\nFacebook: https://RickAstley.lnk.to/FBFollowID \nTwitter: https://RickAstley.lnk.to/TwitterID \nInstagram: https://RickAstley.lnk.to/InstagramID \nWebsite: https://RickAstley.lnk.to/storeID \nTikTok: https://RickAstley.lnk.to/TikTokID\n\nListen to Rick Astley:\nSpotify: https://RickAstley.lnk.to/SpotifyID \nApple Music: https://RickAstley.lnk.to/AppleMusicID \nAmazon Music: https://RickAstley.lnk.to/AmazonMusicID \nDeezer: https://RickAstley.lnk.to/DeezerID \n\nLyrics:\nWe’re no strangers to love\nYou know the rules and so do I\nA full commitment’s what I’m thinking of\nYou wouldn’t get this from any other guy\n\nI just wanna tell you how I’m feeling\nGotta make you understand\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\nWe’ve known each other for so long\nYour heart’s been aching but you’re too shy to say it\nInside we both know what’s been going on\nWe know the game and we’re gonna play it\n\nAnd if you ask me how I’m feeling\nDon’t tell me you’re too blind to see\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\n#RickAstley #NeverGonnaGiveYouUp #WheneverYouNeedSomebody #OfficialMusicVideo",
  "id": "dQw4w9WgXcQ",
  "keywords": [
    "rick astley",
    "Never Gonna Give You Up",
    "nggyu",
    "never gonna give you up lyrics",
    "rick rolled",
    "Rick Roll",
    "rick astley official",
    "rickrolled",
    "Fortnite song",
    "Fortnite event",
    "Fortnite dance",
    "fortnite never gonna give you up",
    "rick roll",
    "rickrolling",
    "rick rolling",
    "never gonna give you up",
    "80s music",
    "rick astley new",
    "animated video",
    "rickroll",
    "meme songs",
    "never gonna give u up lyrics",
    "Rick Astley 2022",
    "never gonna let you down",
    "animated",
    "rick rolls 2022",
    "never gonna give you up karaoke"
  ],
  "length": 212,
  "publish_date": null,
  "resolutions": [
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p"
  ],
  "subtitles": [],
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "url": {
    "audio": {
      "128kbps": "https://rr2---sn-nx5s7n76.googlevideo.com/videoplayback?expire=1727620629&ei=tBH5ZuXtPK32sfIPmpfRaA&ip=34.213.214.55&id=o-AFciugVQSUntvlu-EtzrcBd4W06EaI8LnUezpJahzv8S&itag=140&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=7c&mm=31%2C29&mn=sn-nx5s7n76%2Csn-nx57ynsk&ms=au%2Crdu&mv=m&mvi=2&pl=17&initcwndbps=906250&siu=1&bui=AXLXGFTLtpYeBi-WkfbOrD6x11PgTTzzR3XccdPZFtz4stuPKtFQJJZUbJtbt6KJJdElaNlI6w&spc=54MbxZ-8cHiojJiaToWtUNunjsdmNSRVaZsp33b3yJk5hWz-XyvPBPMvqlmBFtXq-StOzuzECw&vprv=1&svpuc=1&mime=audio%2Fmp4&ns=LcPciQPCIlyTAh4bUR1Ry3oQ&rqh=1&gir=yes&clen=3433605&dur=212.091&lmt=1717047821006373&mt=1727598776&fvip=4&keepalive=yes&fexp=51299152%2C51300760&c=WEB&sefc=1&txp=4532434&n=PBkHSDz29n0qdg&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Csiu%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=ABPmVW0wRQIhAL4XTegKBWTyhPvlGwVYx5b6wKFXGaJnWz5hPoyu2V1jAiBX3ZHpSl-MMXhVWpt3O5ds3INf0Wlr-pbzhcj9KywORA%3D%3D&pot=MnRLRTG8kBazMEt9RGwvFceBv40KENnpHtlDrguGDKni7A-azrTC0L_GYy7Pz-fH6mqHFsS7CmHJ3c3g9Y6z-RqqRsbYhMeXWbiXmyTXLpKRXOkQFbgSjNeRohf9afkINW7suFEVcBe0OedclwPPNYTqkcXvKA%3D%3D&sig=AJfQdSswRQIhALzVUs_1ZBhAU4vl4-_gWy8D_IuAVQZJzFanrawDMKOsAiAGBw-Q385K5JzdWj80j9eKH3yKDR0xsKxZTyKPU2Ubkg%3D%3D",
      "160kbps": "https://rr2---sn-nx5s7n76.googlevideo.com/videoplayback?expire=1727620629&ei=tBH5ZuXtPK32sfIPmpfRaA&ip=34.213.214.55&id=o-AFciugVQSUntvlu-EtzrcBd4W06EaI8LnUezpJahzv8S&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=7c&mm=31%2C29&mn=sn-nx5s7n76%2Csn-nx57ynsk&ms=au%2Crdu&mv=m&mvi=2&pl=17&initcwndbps=906250&siu=1&bui=AXLXGFTLtpYeBi-WkfbOrD6x11PgTTzzR3XccdPZFtz4stuPKtFQJJZUbJtbt6KJJdElaNlI6w&spc=54MbxZ-8cHiojJiaToWtUNunjsdmNSRVaZsp33b3yJk5hWz-XyvPBPMvqlmBFtXq-StOzuzECw&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=LcPciQPCIlyTAh4bUR1Ry3oQ&rqh=1&gir=yes&clen=3437753&dur=212.061&lmt=1717047822556748&mt=1727598776&fvip=4&keepalive=yes&fexp=51299152%2C51300760&c=WEB&sefc=1&txp=4532434&n=PBkHSDz29n0qdg&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Csiu%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=ABPmVW0wRQIhAL4XTegKBWTyhPvlGwVYx5b6wKFXGaJnWz5hPoyu2V1jAiBX3ZHpSl-MMXhVWpt3O5ds3INf0Wlr-pbzhcj9KywORA%3D%3D&pot=MnRLRTG8kBazMEt9RGwvFceBv40KENnpHtlDrguGDKni7A-azrTC0L_GYy7Pz-fH6mqHFsS7CmHJ3c3g9Y6z-RqqRsbYhMeXWbiXmyTXLpKRXOkQFbgSjNeRohf9afkINW7suFEVcBe0OedclwPPNYTqkcXvKA%3D%3D&sig=AJfQdSswRAIgRgmVXNz6GXZTa8wFsnP1g7VTKkAinxQ2MeL4L7_PpUUCIHgo1DpARUjGV3QpFS06_Q9xdzrUmYnQWyWm0VhX-HFS",
      "50kbps": "https://rr2---sn-nx5s7n76.googlevideo.com/videoplayback?expire=1727620629&ei=tBH5ZuXtPK32sfIPmpfRaA&ip=34.213.214.55&id=o-AFciugVQSUntvlu-EtzrcBd4W06EaI8LnUezpJahzv8S&itag=249&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=7c&mm=31%2C29&mn=sn-nx5s7n76%2Csn-nx57ynsk&ms=au%2Crdu&mv=m&mvi=2&pl=17&initcwndbps=906250&siu=1&bui=AXLXGFTLtpYeBi-WkfbOrD6x11PgTTzzR3XccdPZFtz4stuPKtFQJJZUbJtbt6KJJdElaNlI6w&spc=54MbxZ-8cHiojJiaToWtUNunjsdmNSRVaZsp33b3yJk5hWz-XyvPBPMvqlmBFtXq-StOzuzECw&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=LcPciQPCIlyTAh4bUR1Ry3oQ&rqh=1&gir=yes&clen=1232413&dur=212.061&lmt=1717047819209140&mt=1727598776&fvip=4&keepalive=yes&fexp=51299152%2C51300760&c=WEB&sefc=1&txp=4532434&n=PBkHSDz29n0qdg&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Csiu%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=ABPmVW0wRQIhAL4XTegKBWTyhPvlGwVYx5b6wKFXGaJnWz5hPoyu2V1jAiBX3ZHpSl-MMXhVWpt3O5ds3INf0Wlr-pbzhcj9KywORA%3D%3D&pot=MnRLRTG8kBazMEt9RGwvFceBv40KENnpHtlDrguGDKni7A-azrTC0L_GYy7Pz-fH6mqHFsS7CmHJ3c3g9Y6z-RqqRsbYhMeXWbiXmyTXLpKRXOkQFbgSjNeRohf9afkINW7suFEVcBe0OedclwPPNYTqkcXvKA%3D%3D&sig=AJfQdSswRgIhANYw5Elp9cly-pk9fZtviQxozUwSbmeyiPSX7xxOHywGAiEAoHiFDUhUA-S4m-WjPNnlnSXp65opUramacG4gcucmFg%3D",
      "70kbps": "https://rr2---sn-nx5s7n76.googlevideo.com/videoplayback?expire=1727620629&ei=tBH5ZuXtPK32sfIPmpfRaA&ip=34.213.214.55&id=o-AFciugVQSUntvlu-EtzrcBd4W06EaI8LnUezpJahzv8S&itag=250&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=7c&mm=31%2C29&mn=sn-nx5s7n76%2Csn-nx57ynsk&ms=au%2Crdu&mv=m&mvi=2&pl=17&initcwndbps=906250&siu=1&bui=AXLXGFTLtpYeBi-WkfbOrD6x11PgTTzzR3XccdPZFtz4stuPKtFQJJZUbJtbt6KJJdElaNlI6w&spc=54MbxZ-8cHiojJiaToWtUNunjsdmNSRVaZsp33b3yJk5hWz-XyvPBPMvqlmBFtXq-StOzuzECw&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=LcPciQPCIlyTAh4bUR1Ry3oQ&rqh=1&gir=yes&clen=1630086&dur=212.061&lmt=1717047822840442&mt=1727598776&fvip=4&keepalive=yes&fexp=51299152%2C51300760&c=WEB&sefc=1&txp=4532434&n=PBkHSDz29n0qdg&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Csiu%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=ABPmVW0wRQIhAL4XTegKBWTyhPvlGwVYx5b6wKFXGaJnWz5hPoyu2V1jAiBX3ZHpSl-MMXhVWpt3O5ds3INf0Wlr-pbzhcj9KywORA%3D%3D&pot=MnRLRTG8kBazMEt9RGwvFceBv40KENnpHtlDrguGDKni7A-azrTC0L_GYy7Pz-fH6mqHFsS7CmHJ3c3g9Y6z-RqqRsbYhMeXWbiXmyTXLpKRXOkQFbgSjNeRohf9afkINW7suFEVcBe0OedclwPPNYTqkcXvKA%3D%3D&sig=AJfQdSswRAIgcZBnQIuSU46Et4rVk1EP96LN12X6zEturr49Dt3IdtgCICaL6e5X_7qoN782XgA94aCWl9APN7sqdpZDfnSQ3n4a"
    },
    "video": {
      "360p": "https://rr2---sn-nx5s7n76.googlevideo.com/videoplayback?expire=1727620629&ei=tBH5ZuXtPK32sfIPmpfRaA&ip=34.213.214.55&id=o-AFciugVQSUntvlu-EtzrcBd4W06EaI8LnUezpJahzv8S&itag=18&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=7c&mm=31%2C29&mn=sn-nx5s7n76%2Csn-nx57ynsk&ms=au%2Crdu&mv=m&mvi=2&pl=17&initcwndbps=906250&siu=1&bui=AXLXGFRb9LWg32JPSnGMKJTLm8K3ulHeoFqy6jW98J3ow17XhWM6hHiFPFeuDi2q4X9h4FbCSw&spc=54MbxZ-_cHiojJiaToWtUNunjsdmNSRVaZsp33b3yJk5hWz-XyvPBPMvqlmBFtXq-StOzuz0DmJD&vprv=1&svpuc=1&mime=video%2Fmp4&ns=8KIxDqAhSq857Jj0EsIv_rAQ&rqh=1&cnr=14&ratebypass=yes&dur=212.091&lmt=1717051812678016&mt=1727598776&fvip=4&fexp=51299152%2C51300760&c=WEB&sefc=1&txp=4538434&n=5BzkN_PgDUfS4g&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Csiu%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Ccnr%2Cratebypass%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=ABPmVW0wRQIhAL4XTegKBWTyhPvlGwVYx5b6wKFXGaJnWz5hPoyu2V1jAiBX3ZHpSl-MMXhVWpt3O5ds3INf0Wlr-pbzhcj9KywORA%3D%3D&pot=MnRLRTG8kBazMEt9RGwvFceBv40KENnpHtlDrguGDKni7A-azrTC0L_GYy7Pz-fH6mqHFsS7CmHJ3c3g9Y6z-RqqRsbYhMeXWbiXmyTXLpKRXOkQFbgSjNeRohf9afkINW7suFEVcBe0OedclwPPNYTqkcXvKA%3D%3D&sig=AJfQdSswRAIgfjB7dIm2WxtJENp3UQMt-R6AOxAG42tSR_R8AY1VOjQCIHZTT43adN0Wy7XAicHL3yPavg78sous0M4orEjRw98v"
    }
  },
  "views": 1576357050,
  "watch_url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
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
