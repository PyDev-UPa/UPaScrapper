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
    # urls = [x for x in urls if 'en/' in x or 'upce.cz' in x] #get rid of none upce urls
    for url in urls: # remove mailto: links
        if 'mailto' in url:
            urls.remove(url)
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

    results = crawl('https://www.upce.cz/en')
    results = selectUpce(results)
    for url in results: # add domain to addresses where it was missing
        if containsDomain(url) != True:
            results[results.index(url)] = addDomain(url, 'https://www.upce.cz')
    for url in results:
        print('Checking: {}'.format(url))
        print(requests.get(url).status_code)
        time.sleep(2)
