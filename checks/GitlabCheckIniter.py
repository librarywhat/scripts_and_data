import pickle
import sys

import requests


class GitlabCheck:
    TOKEN: str
    GITLAB_URL = 'https://gitlab.rebrainme.com/api/v4'
    HEADERS: dict
    USER_ID: int
    PROJECTS: dict

    def __init__(self):
        with open('/home/user/token.txt', 'r', encoding='utf-8') as file:
            self.TOKEN = file.read().strip().replace('\n', '')
        self.HEADERS = {
            'PRIVATE-TOKEN': self.TOKEN,
            'Content-Type': 'application/json'
        }
        self.USER_ID = self.__get_id()
        self.PROJECTS = self.__get_projects()

    def __get_username(self):
        response = requests.get(f'{self.GITLAB_URL}/user', headers=self.HEADERS)
        return response.json()['username']

    def __get_id(self):
        response = requests.get(f'{self.GITLAB_URL}/user', headers=self.HEADERS)
        return response.json()['id']

    def __get_projects(self):
        projects_dct = {}
        url=f"{self.GITLAB_URL}/groups/devops_users_repos%2F{self.USER_ID}/projects"
        response = requests.get(url, headers=self.HEADERS)
        projects = response.json()
        for project in projects:
            projects_dct[project['path']] = project['id']
        return projects_dct



if __name__ == '__main__':
    with open('check.pickle', 'wb') as f:
        pickle.dump(GitlabCheck(), f)
