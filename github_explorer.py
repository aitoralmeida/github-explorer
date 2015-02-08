# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:48:13 2014

@author: aitor
"""

from github import Github #pip install PyGithub 
import github
import networkx as nx

import json
import operator

token = '' # https://help.github.com/articles/creating-an-access-token-for-command-line-use/

seeds = []

CRAWL_PATH = './ongoing_crawl/'



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
    
def build_following_network(targets):
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
    
def build_collaboration_network(targets):
    G = nx.Graph()
    gh = Github(token, per_page=100)
    for target in targets:
        print 'Processing', target
        try:
            user = gh.get_user(target)
            for repo in user.get_repos():
                collaborators = [c.login for c in repo.get_contributors()]
                print 'Repo:', repo.name
                for i, c in enumerate(collaborators):
                    for j in range(i+1, len(collaborators)):
                        G.add_edge(c, collaborators[j])
        except:
            print 'User does not exists',target
            
    return G
    
def _save_status(collaborations, crawled_repos, crawled_users, queue):
    json.dump(collaborations, open(CRAWL_PATH + 'collaborations.json', 'w'))
    json.dump(crawled_repos, open(CRAWL_PATH + 'crawled_repos.json', 'w'))
    json.dump(crawled_users, open(CRAWL_PATH + 'crawled_users.json', 'w'))
    json.dump(queue, open(CRAWL_PATH + 'queue.json', 'w'))
    
def _load_status():
    collaborations = json.load(open(CRAWL_PATH + 'collaborations.json', 'r'))
    crawled_repos = json.load(open(CRAWL_PATH + 'crawled_repos.json', 'r'))
    crawled_users = json.load(open(CRAWL_PATH + 'crawled_users.json', 'r'))
    queue = json.load(open(CRAWL_PATH + 'queue.json', 'r'))
    
    return collaborations, crawled_repos, crawled_users, queue
    
    
       
def crawl_github(seeds):
    gh = Github(token, per_page=100)
    
    # Priority for the seed users
    INITIAL_PRIORITY = 10000
    # Minimun priority to continue mining
    MIN_PRIORITY = 3000
    
    # Discovered collaborations
    collaborations = []
    # Already processed repos
    crawled_repos = []
    # Already processed users
    crawled_users = []
    # User queue to be processed
    queue = {} #{'user': priority_value}
    
    #initialize queue
    for seed in seeds:
        queue[seed] = INITIAL_PRIORITY
        
    # total processed repos
    tot = 0

    # crawl github collaboration network
    while (True):
        print '- Queue length: %s' % len(queue)
        print '- Total collaborations: %s' % len(collaborations)
        # short queue and take the item with the highest priority
        sorted_queue = sorted(queue.items(), key=operator.itemgetter(1))
        priority = sorted_queue[-1][1]
        user_to_process = sorted_queue[-1][0]
        queue.pop(user_to_process)
        
        # If the priority is not high enough, stop the crawling
        if priority <= MIN_PRIORITY:
            break
        
        if user_to_process in crawled_users:
            continue
        else:
            crawled_users.append(user_to_process)
                        
        print '- Processing user %s with priority %s' % (user_to_process, priority)
            
        user = gh.get_user(user_to_process)
        for repo in user.get_repos():
            repo_name = repo.full_name
            if repo_name in crawled_repos:
                continue
            else:
                print '  - Processing repo %s' % repo_name
                crawled_repos.append(repo_name)
                
                # queue priority is updated using the repo stargazers number
                stargazers = [s for s in repo.get_stargazers()]
                total_stargazers = len(stargazers)
                
                try:
                    contributors = [c.login for c in repo.get_contributors()]
                    if len(contributors) > 1:
                        collaborations.append(contributors)
                        if total_stargazers > 0:
                            for contributor in contributors:
                                if not contributor in crawled_users:
                                    if contributor in queue:
                                        queue[contributor] += total_stargazers
                                    else:
                                        queue[contributor] = total_stargazers
                except github.GithubException as e:
                    print e
                except TypeError as e:
                    print e
                    
                            
        tot += 1
        if tot % 3 == 0:
            print 'Saving current crawl...'
            _save_status(collaborations, crawled_repos, crawled_users, queue)
            print 'saved'
                            
    return collaborations
                        
            
            
        
        

    
        
if __name__ == '__main__':
    token = get_token()    
    # target nodes to build morelab's reseach group networks
    morelab = ['aitoralmeida', 'porduna', 'OscarPDR', 'jonlazaro', 'juansixto', 
               'memaldi', 'unaguil', 'gomezgoiri', 'edlectrico', 'josubg', 'xPret', 
               'dipina', 'koldozabaleta', 'joruiz', 'dieguich', 'pcuriel', 'juanarmentia', 
               'zstars']
    
#    # build followers network    
#    G = build_following_network(morelab)
#    nx.write_gexf(G,'github-following.gexf')
#    
#    #build collaboration network
#    G = build_collaboration_network(morelab)
#    nx.write_gexf(G,'github-collaborators.gexf')
    
    # crawl github to build the collaboration network
    # The users of the projects with more than 9000 stars
    #https://github.com/search?p=1&q=stars%3A%3E9000&ref=searchresults&type=Repositories&utf8=%E2%9C%93
    crawl_seed = ['twbs', 'vhf', 'angular', 
                  'joyent', 'mbostock', 'jquery', 'FortAwesome', 'h5bp', 'rails', 
                  'bartaz', 'meteor', 'github', 'robbyrussell', 'Homebrew', 
                  'adobe', 'jashkenas', 'nwjs', 'moment', 'torvalds', 'zurb', 
                  'daneden', 'hakimel', 'docker', 'blueimp', 'jekyll', 'mrdoob', 
                  'strongloop', 'harvesthq', 'AFNetworking', 'facebook', 'necolas', 
                  'Automattic', 'resume', 'tiimgreen', 'gitlabhq', 'Semantic-Org', 
                  'laravel', 'Modernizr', 'TryGhost', 'h5bp', 'dypsilon', 'jashkenas', 
                  'google', 'driftyco', 'discourse', 'jakubroztocil', 'nnnick', 
                  'select2', 'ariya', 'django', 'emberjs', 'kennethreitz', 'mitsuhiko', 
                  'atom', 'airbnb', 'plataformatec', 'Prinzhorn', 'papers-we-love', 
                  'antirez', 'neovim', 'less', 'caolan', 'bower', 'gulpjs', 'tastejs', 
                  'defunkt', 'nvie', 'mathiasbynens', 'jashkenas', 'limetext', 
                  'yahoo', 'mozilla', 'bayandin', 'textmate', 'getify', 'prakhar1989', 
                  'hammerjs', 'elasticsearch', 'diaspora', 'octocat', 'iojs', 
                  'ajaxorg', 'Leaflet', 'symfony', 'vinta', 'interagent', 'ansible', 
                  'jquery', 't4t5', 'rust-lang', 'balderdashy', 'twitter', 'bcit-ci', 
                  'FezVrasta', 'designmodo', 'kenwheeler', 'gruntjs'] 
    collaborations = crawl_github(crawl_seed)
    json.dump(collaborations, open('collaborations.json','w'))
    
    
    print 'done'