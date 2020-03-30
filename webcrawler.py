#!/usr/bin/python3

'''
webcrawler.py - searches for all webpages on a site and creates their list
INPUT: URL of the homepage
OUTPUT: list of URLs
'''

import requests, time
from bs4 import BeautifulSoup

def crawl(url):
    '''
    finds all links on a page and inputs them in a list
    INPUT: url
    OUTPUT: list of links
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features='html.parser')
    hrefs = soup.find_all('a', href=True)
    urls = [x.get('href') for x in hrefs] # get only URLs

    for url in urls: # remove mailto: links
        if 'mailto' in url:
            urls.remove(url)

    helper = list() # remove duplicates
    for url in urls:
        if url not in helper:
            helper.append(url)
    urls = helper
    del helper

    return urls

def containsDomain(url):
    '''
    checks whether url is whole or just a subdirectory
    '''
    if url[:4] == 'http':
        return True

def addDomain(subdirectory, domain): # adds domain to subdirectory to create full url
    '''
    adds given domain to url without any
    '''
    url = domain + subdirectory
    return url

def selectUpce(urlList):
    'selects only upce.cz webpages'
    urls = [x for x in urlList if 'en' in x[:3] or 'upce.cz' in x] # select only upce webpages
    return urls


if __name__ == '__main__':

    visited = dict()
    toVisit = list()

    toVisit = crawl('https://www.upce.cz/en')
    toVisit = selectUpce(toVisit)
    for url in toVisit: # add domain to addresses where it was missing
        if containsDomain(url) != True:
            toVisit[toVisit.index(url)] = addDomain(url, 'https://www.upce.cz')
    for url in toVisit:
        if url not in visited.keys():
            print('Checking: {}'.format(url))
            visited.setdefault(url, {'statusCode': requests.get(url).status_code})
            print(visited[url]['statusCode'])
            time.sleep(2)
