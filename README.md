Google Drive MP4 Downloader

This Python script downloads MP4 files from a specified directory in your Google Drive and deletes them after successful download.

Requirements:

Python 3

Google Drive API credentials

Installation:

1. Create a project in the Google Cloud Platform Console (https://console.cloud.google.com/) and enable the Google Drive API.
2. Follow the instructions to download the credentials file (JSON format). Place this file in your project directory and name it credentials.json.
3. Install required libraries using pip:

```bash
pip install google-auth google-auth-oauthlib googleapiclient
```

Usage:

1. Replace FOLDER_ID_FIN in the script with the ID of the Google Drive folder containing your MP4 files. You can find the folder ID in the URL of the folder when viewed in your browser.
2. Run the script:

```bash
python drive_dw.py
```

Explanation:

The script performs the following actions:

Authenticates with the Google Drive API using the provided credentials file.
Lists all MP4 files in the specified folder.
Downloads each MP4 file to your local machine.
Verifies the downloaded files and deletes them from Google Drive.
