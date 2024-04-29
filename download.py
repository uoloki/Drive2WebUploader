import os
import io
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Set up logging to overwrite previous logs each run
logging.basicConfig(level=logging.INFO, filename='drive_funcs.log', filemode='w',  # 'w' to overwrite
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Drive_Funcs:
    def __init__(self, credentials_file='credentials.json', token_file='token.json', scopes=None):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes if scopes else ['https://www.googleapis.com/auth/drive']
        self.creds = None
        self.downloaded_files = 'downloaded_files.txt'
        self.initialize_downloaded_files()
        logging.info("Drive_Funcs class instantiated")

    def initialize_downloaded_files(self):
        # Clear the downloaded files list at the start of each run
        with open(self.downloaded_files, 'w') as f:
            pass

    def authorization_drive(self):
        logging.info("Starting authorization process")
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            logging.info("Loaded credentials from token file")
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                logging.info("Refreshed credentials")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                self.creds = flow.run_local_server(port=0)
                logging.info("Obtained new credentials")
            with open(self.token_file, "w") as token:
                token.write(self.creds.to_json())
                logging.info("Saved new credentials to token file")

    def list_files_drive(self, folder_id):
        logging.info(f"Listing MP4 files in folder: {folder_id}")
        service = build("drive", "v3", credentials=self.creds)
        query = f"'{folder_id}' in parents and mimeType = 'video/mp4'"
        files = []
        page_token = None
        while True:
            try:
                response = service.files().list(
                    q=query,
                    pageSize=10,
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token
                ).execute()
                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            except HttpError as error:
                logging.error(f"An error occurred while listing files: {error}")
                break
        logging.info("Completed listing files")
        return files

    def download_file(self, file_id, file_name):
        if not file_name.lower().endswith('.mp4'):
            logging.warning(f"Skipped non-MP4 file: {file_name}")
            return
        logging.info(f"Starting download for {file_name}")
        service = build("drive", "v3", credentials=self.creds)
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        try:
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f"Download progress for {file_name}: {int(status.progress() * 100)}% complete")
            with open(file_name, 'wb') as f:
                fh.seek(0)
                f.write(fh.read())
                logging.info(f"Successfully downloaded {file_name}")
                with open(self.downloaded_files, 'a') as df:
                    df.write(f"{file_name}\n")
        except HttpError as error:
            logging.error(f"Failed to download {file_name}: {error}")

    def verify_and_delete_files(self, folder_id):
        logging.info("Verifying local files and preparing to delete from Drive")
        service = build("drive", "v3", credentials=self.creds)
        with open(self.downloaded_files, 'r') as file:
            files = file.readlines()
            files = [f.strip() for f in files]

        for file_name in files:
            if os.path.exists(file_name):
                logging.info(f"File {file_name} verified locally.")
                file_id = next((f['id'] for f in self.list_files_drive(folder_id) if f['name'] == file_name), None)
                if file_id:
                    try:
                        service.files().delete(fileId=file_id).execute()
                        logging.info(f"Deleted {file_name} from Google Drive.")
                    except HttpError as error:
                        logging.error(f"Error deleting {file_name}: {error}")
                else:
                    logging.warning(f"File ID not found for {file_name}.")
            else:
                logging.warning(f"File {file_name} not found locally.")

# Usage
if __name__ == '__main__':
    drive_funcs = Drive_Funcs()
    drive_funcs.authorization_drive()
    folder_id = '1DiH7JzF8v7YyKbiPngcN7qOfoyz70lG8'  # Replace with your specific folder ID
    files = drive_funcs.list_files_drive(folder_id)
    for file in files:
        drive_funcs.download_file(file['id'], file['name'])
    drive_funcs.verify_and_delete_files(folder_id)
