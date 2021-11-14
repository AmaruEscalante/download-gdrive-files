from dotenv import load_dotenv
import os
from apiclient import discovery
import requests
import pathlib

load_dotenv()
API_KEY = os.getenv('DRIVE_KEY')

service = discovery.build('drive', 'v3', developerKey=API_KEY)


def download_file(filename, file_id, root):
    url = f"https://drive.google.com/uc?id={file_id}"
    file = requests.get(url, stream=True)

    with open(f"{root}/{filename}", "wb") as f:
        for chunk in file.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def download_folder(parent, folder_name):
    pathlib.Path(folder_name).mkdir(parents=True, exist_ok=True)
    param = {"q": "'" + parent + "' in parents"}
    result = service.files().list(**param).execute()
    files = result.get('files')
    for file in files:
        f_name = file.get('name')
        fid = file.get('id')

        if file.get('mimeType') != 'application/vnd.google-apps.folder':
            print(f"File {f_name}")
            download_file(f_name, fid, folder_name)
        else:
            print(f"FOLDERS {file.get('name')}")
            download_folder(fid, f"{folder_name}/{f_name}")


def main():
    # NOTE: folder must be publicly visible when using an API key.
    folder_id = input("Past the public GDrive folder ID to download...")
    folder_name = input("Insert the folder name")
    download_folder(folder_id, folder_name)


if __name__ == "__main__":
    main()
