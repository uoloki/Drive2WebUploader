"""
This script utilizes google drive api to download files from a chosen directory
and deletes them after effective download
"""
# pylint: disable=no-member

import os
import io
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


# Set up logging to overwrite previous logs each run
logging.basicConfig(level=logging.INFO, filename='drive_funcs.log', filemode='w',  #'w' to overwrite
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DriveFuncs:
    """
    Class containing functions related to actions with google drive API.
    """
    def __init__(self, credentials_file='credentials.json', token_file='token.json', scopes=None):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes if scopes else ['https://www.googleapis.com/auth/drive']
        self.creds = None
        self.downloaded_files = 'downloaded_files.txt'
        self.initialize_downloaded_files()
        logging.info("Drive_Funcs class instantiated")

    def initialize_downloaded_files(self):
        """
        Clear the downloaded files list at the start of each run
        """
        with open(self.downloaded_files, 'w', encoding='utf-8') as _:
            pass

    def authorization_drive(self):
        """
        Checking if there's an existing authorisation token and initiating
        sign-in if not
        """
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
            with open(self.token_file, "w", encoding="utf-8") as token:
                token.write(self.creds.to_json())
                logging.info("Saved new credentials to token file")

    def list_files_drive(self, folder_id):
        """
        Creating a list of files from the chosen drive folder
        """
        logging.info("Listing PNG files in folder: %s", folder_id)
        service = build("drive", "v3", credentials=self.creds)
        query = f"'{folder_id}' in parents and mimeType = 'image/png'"
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
                logging.error("An error occurred while listing files: %s", error)
                break
        logging.info("Completed listing files")
        return files

    def download_file(self, file_id, file_name):
        """
        Downloading the created list of files, skipping all non-png files
        """
        if not file_name.lower().endswith('.png'):
            logging.warning("Skipped non-PNG file: %s", file_name)
            return
        logging.info("Starting download for %s", file_name)
        service = build("drive", "v3", credentials=self.creds)
        request = service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        try:
            while not done:
                status, done = downloader.next_chunk()
                logging.info(
                    "Download progress for %s: %s complete",
                    file_name, int(status.progress() * 100)
                    )
            with open(file_name, 'wb') as file:
                file_handle.seek(0)
                file.write(file_handle.read())
                logging.info("Successfully downloaded %s", file_name)
                with open(self.downloaded_files, 'a', encoding='utf-8') as data_file:
                    data_file.write(f"{file_name}\n")
        except HttpError as error:
            logging.error("Failed to download %s: %s", file_name, error)

    def verify_and_delete_files(self, folder_id):
        """
        Checking if the files were saved properly and deleting them from drive if so
        """
        logging.info("Verifying local files and preparing to delete from Drive")
        service = build("drive", "v3", credentials=self.creds)
        with open(self.downloaded_files, 'r', encoding='utf-8') as file:
            files = file.readlines()
            files = [f.strip() for f in files]

        for file_name in files:
            if os.path.exists(file_name):
                logging.info("File %s verified locally.", file_name)
                file_id = next(
                    (f['id'] for f in self.list_files_drive(folder_id) if f['name'] == file_name),
                    None
                    )
                if file_id:
                    try:
                        service.files().delete(fileId=file_id).execute()
                        logging.info("Deleted %s from Google Drive.", file_name)
                    except HttpError as error:
                        logging.error("Error deleting %s: %s", file_name, error)
                else:
                    logging.warning("File ID not found for %s.", file_name)
            else:
                logging.warning("File %s not found locally.", file_name)

# Usage
if __name__ == '__main__':
    drive_funcs = DriveFuncs()
    drive_funcs.authorization_drive()
    FOLDER_ID_FIN = "##############################"  # Replace with your specific folder ID
    files_to_dw = drive_funcs.list_files_drive(FOLDER_ID_FIN)
    for file_t in files_to_dw:
        drive_funcs.download_file(file_t['id'], file_t['name'])
    drive_funcs.verify_and_delete_files(FOLDER_ID_FIN)
