#!usr/bin/python

'''scrapFEV.py dowloands webpage https://www.upce.cz/en/foreign-education-verification
and creates a list containing countries and groups from the html code for further processing'''

import requests, bs4

fevUrl = 'https://www.upce.cz/en/foreign-education-verification'

sourcePage = requests.get(fevUrl)
sourceSoup = bs4.BeautifulSoup(sourcePage.text, 'html.parser')
allLines = sourceSoup.select('option')

#TODO get rid of none country items in the list
