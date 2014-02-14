# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:48:13 2014

@author: aitor
"""

from github import Github #pip install PyGithub 
import networkx as nx

token = ''

def get_token():
    with open('token.txt', 'r') as tokenfile:
        return tokenfile.readline()
        
def get_repos(user):
    gh = Github(token, per_page=100)
    repo_names = []
    user = gh.get_user(user)
    for repo in user.get_repos():
        repo_names.append(repo.name)
    
    return repo_names
    
        
if __name__=='__main__':
    token = get_token()
    print get_repos('aitoralmeida')