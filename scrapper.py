import urllib.request
from urllib.parse import urlparse
import re
from selenium import webdriver as driver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
from typing import Dict, List
import config


def scrapeSite(url: str, headers: Dict[str, str],
               socialPlatforms: List[config.SocialPlatform] = []):
    try:
        serverPageSrc = getServerSource(url, headers)
        socialLinks = parseHTML(serverPageSrc, socialPlatforms)
        # This can be a really expensive call
        # TODO: Figure out an efficient detection strategy to check if page
        # needs to be compiled by a browser's JS engine
        if(len(socialLinks) == 0):
            browserPageSrc = getBrowserSource(url)
            socialLinks = parseHTML(browserPageSrc, socialPlatforms)
        for social in socialLinks:
            print('\n' + social)
    except Exception as e:
        print(str(e))


def getServerSource(url: str, headers: Dict[str, str]):
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    resp.close()
    return respData.decode('utf-8')


def getBrowserSource(url: str):
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--disable-notifications")
    chromeOptions.add_argument("--disable-extensions")
    # Selenium chrome driver must be added to the path
    webDriver = driver.Chrome(options=chromeOptions)
    webDriver.get(url)
    pageSource = webDriver.page_source
    webDriver.close()
    return str(pageSource)


def parseHTML(pageSrc: str, socialPlatforms: List[config.SocialPlatform]):
    htmlSoup = soup(pageSrc, 'html.parser')
    unfilteredLinkTags = htmlSoup.findAll("a")
    filteredLinks = []
    for tag in unfilteredLinkTags:
        urlObject = urlparse(tag.get('href'))
        if(urlObject.hostname):
            hostFragments = {*urlObject.hostname.split(".")}
            commonHost = hostFragments.intersection(
                {*(platform.getHost() for platform in socialPlatforms)}
            )
            if(len(commonHost) > 0 and
                    urlObject.geturl() not in filteredLinks):
                filteredLinks.append(urlObject.geturl())
    return [link for link in filteredLinks]


if __name__ == "__main__":
    rawUrl = input('Enter a URL to scrape:\t')
    config.headers['User-Agent'] = config.userAgents["Google"]
    supportedPlatforms = []
    for platform in config.supportedPlatforms:
        supportedPlatforms.append(config.SocialPlatform
            (**config.supportedPlatforms[platform]))
    scrapeSite(rawUrl, config.headers, supportedPlatforms)
