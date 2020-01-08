import urllib.request
import re
from bs4 import BeautifulSoup as soup
from typing import Dict

userAgents = {'Mozilla': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'Google': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36'}
headers = { 'Accept': 'text/html'}

def scrapeSite(url : str, headers : Dict[str,str]):
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)
        respData = resp.read()
        resp.close()
        respSoup = soup(str(respData), 'html.parser')
        linkTags = respSoup.findAll("a")
        for tag in linkTags:
            print(re.findall('href="(.*?)"', str(tag)))
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    #Sanitize the user input URL
    rawUrl = input('Enter a URL to scrape:\t')
    headers['User-Agent'] = userAgents['Mozilla']
    scrapeSite(rawUrl, headers)