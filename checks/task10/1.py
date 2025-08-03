import importlib
import pickle
import sys

module = importlib.import_module('GitlabCheckIniter')
GitlabCheck = module.GitlabCheck

with open('check.pickle', 'rb') as f:
    gcc = pickle.load(f)

project_names = ['qa-project']
for project_name in project_names:
    if project_name not in gcc.PROJECTS:
        sys.exit(1)
