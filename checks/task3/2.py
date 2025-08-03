import importlib
import pickle
import sys

import requests

module = importlib.import_module('GitlabCheckIniter')
GitlabCheck = module.GitlabCheck

with open('check.pickle', 'rb') as f:
    gcc = pickle.load(f)


def check_branch_exists(project_id_, branch_name_):
    response = requests.get(f'{gcc.GITLAB_URL}/projects/devops_users_repos%2F{gcc.USER_ID}%2F{project_id_}/repository/branches/{branch_name_}',
                            headers=gcc.HEADERS)
    if response.status_code == 200:
        print(f'Branch {branch_name_} exists in project {project_id_}')
        return True
    print(f'Branch {branch_name_} does not exist in project {project_id_}')
    sys.exit(1)


branch_name = 'dev'
project_names = ['ci-project']
for project_name in project_names:
    project_id = gcc.PROJECTS[project_name]
    check_branch_exists(project_name, branch_name)
