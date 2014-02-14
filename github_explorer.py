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
        
def get_repos_names(user):
    gh = Github(token, per_page=100)
    user = gh.get_user(user)
    repo_names = [repo.name for repo in user.get_repos()]
    return repo_names
    
def get_stargazers(user):
    gh = Github(token, per_page=100)
    user = gh.get_user(user)
    stargazers = set()
    for repo in user.get_repos():
      for s in repo.get_stargazers():
          stargazers.add(s)
      
    return stargazers
    

        

    
        
if __name__=='__main__':
    token = get_token()
#   print get_repos_names('aitoralmeida')
    print get_stargazers('aitoralmeida')