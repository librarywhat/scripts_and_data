import importlib
import pickle
import sys

import requests

module = importlib.import_module('GitlabCheckIniter')
GitlabCheck = module.GitlabCheck

with open('check.pickle', 'rb') as f:
    gc = pickle.load(f)


def check_protected_branch(project_id_, branch_name_, push_level, merge_level):
    response = requests.get(f'{gc.GITLAB_URL}/projects/devops_users_repos%2F{gc.USER_ID}%2F{project_id_}/protected_branches', headers=gc.HEADERS)
    branches = response.json()
    for branch in branches:
        if branch['name'] == branch_name_:
            if branch['push_access_levels'][0]['access_level'] == push_level and branch['merge_access_levels'][0][
                'access_level'] == merge_level:
                print(f'Branch {branch_name_} in project {project_id_} is correctly protected')
                return True
            else:
                print(f'Branch {branch_name_} in project {project_id_} is not correctly protected')
                return False
    print(f'Branch {branch_name_} in project {project_id_} is not protected')
    sys.exit(1)


branch_name = 'dev'
project_names = ['ci-project']
for project_name in project_names:
    project_id = gc.PROJECTS[project_name]
    check_protected_branch(project_name, branch_name, push_level=0, merge_level=30)
