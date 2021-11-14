from dotenv import load_dotenv
import os
from apiclient import discovery
import requests
import pathlib
from tqdm import tqdm
from bs4 import BeautifulSoup

load_dotenv()
API_KEY = os.getenv('DRIVE_KEY')

service = discovery.build('drive', 'v3', developerKey=API_KEY)


def write_file(filepath, file):
    total = int(file.headers.get('content-length', 0))
    with open(filepath, "wb") as f, tqdm(
            desc=filepath,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024) as bar:
        for chunk in file.iter_content(chunk_size=1024):
            if chunk:
                size = f.write(chunk)
                bar.update(size)


def download_file(filename, file_id, root):
    domain = "https://drive.google.com"
    url = f"{domain}/uc?id={file_id}"
    r = requests.Session()
    file = r.get(url, stream=True)
    cookies = file.cookies.items()
    if 'warning' not in cookies[0][0]:
        write_file(f"{root}/{filename}", file)

    else:
        soup = BeautifulSoup(file.content, 'html.parser')
        url = soup.find(id="uc-download-link")
        url = url.get('href')
        url = f"{domain}{url}"
        file = r.get(url, stream=True)
        write_file(f"{root}/{filename}", file)


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
    folder_id = input("Past the public GDrive folder ID to download...\n")
    folder_name = input("Insert the folder name\n")
    download_folder(folder_id, folder_name)


if __name__ == "__main__":
    main()
