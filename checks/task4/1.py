import importlib
import pickle
import sys

import requests

module = importlib.import_module('GitlabCheckIniter')
GitlabCheck = module.GitlabCheck

with open('check.pickle', 'rb') as f:
    gc = pickle.load(f)


def download():
    project_id = None
    for project_path in gc.PROJECTS:
        if "ci-k8s" in project_path:
            project_id = gc.PROJECTS[project_path]

    if not project_id:
        sys.exit(1)
    REF = "master"
    file_url = (f"{gc.GITLAB_URL}/api/v4/projects/{project_id}/repository/files/"
                f".gitlab-ci.yml/raw?ref={REF}")

    file_name = ".gitlab-ci.yml"
    # Make the GET request to download the file
    file_response = requests.get(file_url, headers=gc.HEADERS)

    # Check if the request was successful
    if file_response.status_code == 200:
        # Save the file content to a local file
        with open(file_name, 'wb') as file:
            file.write(file_response.content)
        print('File downloaded successfully.')
    else:
        print(f'Failed to download file. Status code: {file_response.status_code}')
        print('Response:', file_response.json())


download()
