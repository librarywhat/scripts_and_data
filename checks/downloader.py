import sys

import requests

from storage import Storage


class Downloader:
    BASE_URL = 'https://gitlab.rebrainme.com'
    REF = "master"
    file_path: str

    def __init__(self, key, file_path):
        self.storage = Storage(key).choose_method()
        self.file_path = file_path

    def download(self):
        file_name = self.file_path.rsplit('/')[-1]
        project_id_url = f"{self.BASE_URL}/api/v4/projects/{self.storage.PROJECT_PATH.replace('/', '%2F')}"
        headers = {
            'PRIVATE-TOKEN': self.storage.PRIVATE_TOKEN
        }

        project_response = requests.get(project_id_url, headers=headers)

        if project_response.status_code == 200:
            PROJECT_ID = project_response.json()['id']
        else:
            print(f'Failed to get project ID. Status code: {project_response.status_code}')
            print('Response:', project_response.json())
            exit(1)

        # Construct the API URL to download the file
        file_url = (f"{self.BASE_URL}/api/v4/projects/{PROJECT_ID}/repository/files/"
                    f"{FILE_PATH.replace('/', '%2F')}/raw?ref={self.REF}")

        # Make the GET request to download the file
        file_response = requests.get(file_url, headers=headers)

        # Check if the request was successful
        if file_response.status_code == 200:
            # Save the file content to a local file
            with open(file_name, 'wb') as file:
                file.write(file_response.content)
            print('File downloaded successfully.')
        else:
            print(f'Failed to download file. Status code: {file_response.status_code}')
            print('Response:', file_response.json())


if __name__ == '__main__':
    KEY = sys.argv[1]
    FILE_PATH = sys.argv[2]
    Downloader(KEY, FILE_PATH).download()
