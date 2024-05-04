Google Drive PNG Downloader

This Python script downloads PNG files from a specified directory in your Google Drive, deletes them after successful download, uploads them on a website and sends
an email with logs.

Requirements:

Python 3.10+

Google Drive API credentials

Installation:

1. Create a project in the Google Cloud Platform Console (https://console.cloud.google.com/) and enable the Google Drive API.
2. Follow the instructions to download the credentials file (JSON format). Place this file in your project directory and name it credentials.json.
3. Refactor the code to suit for your specific needs and website.
4. Set up SMTP server. (https://www.gmass.co/blog/gmail-smtp/)
5. Install required libraries using pip:

```bash
pip install google-auth google-auth-oauthlib googleapiclient selenium 
```

Usage:

1. Replace FOLDER_ID_FIN in the script with the ID of the Google Drive folder containing your PNG files. You can find the folder ID in the URL of the folder when viewed in your browser.
2. Specify credentials and CSS selectors in a json file and set-up SMTP server.
3. Run the script:

```bash
python subprocesses.py
```

Explanation:

The script performs the following actions:

Authenticates with the Google Drive API using the provided credentials file.
Lists all PNG files in the specified folder.
Downloads each PNG file to your local machine.
Verifies the downloaded files and deletes them from Google Drive.
Performs a website log-in, uploads the files and deletes them from a current directory.
Sends an email with logs to a chosen email address using gmail SMTP.
