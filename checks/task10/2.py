import importlib
import pickle
import sys
import requests

module = importlib.import_module('GitlabCheckIniter')
GitlabCheck = module.GitlabCheck

with open('check.pickle', 'rb') as f:
    gcc = pickle.load(f)

project_names = ['qa-project']

def download():
    project_id = None
    for project_path in gcc.PROJECTS:
        if "qa-project" in project_path:
            project_id = gcc.PROJECTS[project_path]

    if not project_id:
        sys.exit(1)
    REF = "dev"
    file_url = (f"{gcc.GITLAB_URL}/api/v4/projects/{project_id}/repository/files/"
                f".gitlab-ci.yml/raw?ref={REF}")

    file_name = ".gitlab-ci.yml"
    file_response = requests.get(file_url, headers=gcc.HEADERS)

    # Check if the request was successful
    if file_response.status_code == 200:
        # Save the file content to a local file
        contents=["test","build","lint","allure"]
        for i in contents:
            if i not in file_response.text:
                sys.exit(1)
    else:
        sys.exit(1)


download()
