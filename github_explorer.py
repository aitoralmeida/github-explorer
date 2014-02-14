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
        
def get_repos_names(user_login):
    gh = Github(token, per_page=100)
    user = gh.get_user(user_login)
    repo_names = [repo.name for repo in user.get_repos()]
    return repo_names
    
def get_stargazers(user_login):
    gh = Github(token, per_page=100)
    user = gh.get_user(user_login)
    stargazers = set()
    for repo in user.get_repos():
      for s in repo.get_stargazers():
          stargazers.add(s)
      
    return stargazers
    
def build_followers_network(targets):
    G = nx.DiGraph()
    gh = Github(token, per_page=100)
    for target in targets:
        print 'Processing', target
        try:
            user = gh.get_user(target)
            for follower in user.get_followers():
                G.add_edge(follower.login, user.login)
            for followee in user.get_following():
                G.add_edge(user.login, followee.login)
        except:
            print 'User does not exists',target
            
    return G
        

    
        
if __name__=='__main__':
    token = get_token()
    G = build_followers_network(['aitoralmeida', 'porduna', 'OscarPDR', 'jonlazaro', 'juansixto', 'memaldi', 'unaguil', 'gomezgoiri', 'edlectrico', 'josubg'])
    print len(G.nodes())
    print len(G.edges())
    nx.write_gexf(G,'github.gexf')
    print 'done'