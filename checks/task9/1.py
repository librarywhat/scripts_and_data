import importlib
import pickle
import sys

import requests

module = importlib.import_module('GitlabCheckIniter')
GitlabCheck = module.GitlabCheck

with open('check.pickle', 'rb') as f:
    gc = pickle.load(f)


def check_branch_exists(project_id_, branch_name_):
    response = requests.get(f'{gc.GITLAB_URL}/projects/devops_users_repos%2F{gc.USER_ID}%2F{project_id_}/repository/branches/{branch_name_}',
                            headers=gc.HEADERS)
    if response.status_code == 200:
        print(f'Branch {branch_name_} exists in project {project_id_}')
        return True
    print(f'Branch {branch_name_} does not exist in project {project_id_}')
    sys.exit(1)


project_names = ['cd-modern']
for project_name in project_names:
    project_id = gc.PROJECTS[project_name]
    check_branch_exists(project_name, "main")
    check_branch_exists(project_name, "test")
