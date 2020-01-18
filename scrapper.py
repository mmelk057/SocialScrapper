from urllib.request import Request
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import ParseResult
from selenium import webdriver as driver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
from typing import Dict, List
from queue_manager import QueueManager
from copy import deepcopy
import config


class Scrapper:

    def __init__(self, baseUrl: ParseResult):
        self.baseUrl = baseUrl
        self.queueManager = QueueManager(baseUrl.geturl())
        self.reqHeaders = deepcopy(config.headers)
        self.reqHeaders['User-Agent'] = config.userAgents["Google"]
        self.supportedPlatforms = []
        for platform in config.supportedPlatforms:
            self.supportedPlatforms.append(
                config.SocialPlatform(
                    **config.supportedPlatforms[platform]
                )
            )

    def recursiveScrape(self, url: str = None):
        if(url is None):
            url = self.baseUrl.geturl()
        pathList: List[str] = self.normalScrape(url)
        for path in pathList:
            self.queueManager.addToSearch(path, self.recursiveScrape)

    def normalScrape(self, url: str = None):
        if(url is None):
            url = self.baseUrl.geturl()
        try:
            serverPageSrc = self.getServerSource(url)
            pathsToSearch = self.parseHTMLPaths(serverPageSrc)
            socialLinks = self.parseHTML(serverPageSrc)
            # This can be a really expensive call
            # TODO: Figure out an efficient detection strategy to check if page
            # needs to be compiled by a browser's JS engine
            if(len(socialLinks) == 0 and len(pathsToSearch) == 0):
                browserPageSrc = self.getBrowserSource(url)
                pathsToSearch = self.parseHTMLPaths(browserPageSrc)
                socialLinks = self.parseHTML(browserPageSrc)

            for socialLink in socialLinks:
                print("\nSocial Link: {} \nFrom path {}".format(
                    socialLink, url
                )
                )
            return pathsToSearch

        except Exception as e:
            print("URL {} unable to be scrapped...".format(url))

    def getServerSource(self, url: str):
        req = Request(url, headers=self.reqHeaders)
        resp = urlopen(req)
        respData = resp.read()
        resp.close()
        return respData.decode('utf-8')

    def getBrowserSource(self, url: str):
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

    def parseHTMLPaths(self, pageSrc: str):
        htmlSoup = soup(pageSrc, 'html.parser')
        unfilteredLinkTags = htmlSoup.findAll("a")
        paths = []
        for tag in unfilteredLinkTags:
            try:
                href = tag.get('href')
                if(href):
                    tagUrl = urlparse(href)
                    if((not tagUrl.hostname or
                        tagUrl.hostname == self.baseUrl.hostname)
                            and (tagUrl.path != '')
                            and tagUrl.path != '/'
                            and ('.' not in tagUrl.path)
                            and ('@' not in tagUrl.path)):
                        tagUrl = tagUrl._replace(netloc=self.baseUrl.netloc,
                                                 scheme=self.baseUrl.scheme)
                        paths.append(tagUrl.geturl())
            except Exception as e:
                print(
                    'Unable to parse through HTML paths because of {}'.format(
                        e
                    )
                )
                continue
        return paths

    def parseHTML(self, pageSrc: str):
        htmlSoup = soup(pageSrc, 'html.parser')
        unfilteredLinkTags = htmlSoup.findAll("a")
        filteredLinks = []
        for tag in unfilteredLinkTags:
            urlObject = urlparse(tag.get('href'))
            if(urlObject.hostname):
                hostFragments = {*urlObject.hostname.split(".")}
                commonHost = hostFragments.intersection(
                    {*(platform.getHost() for platform in
                       self.supportedPlatforms)}
                )
                if(len(commonHost) > 0 and
                        urlObject.geturl() not in filteredLinks):
                    filteredLinks.append(urlObject.geturl())
        return [link for link in filteredLinks]


if __name__ == "__main__":
    rawUrl = urlparse(input('Enter a URL to scrape:\t'))
    useRecursiveSearch = None
    while(useRecursiveSearch is None):
        try:
            useRecursiveSearch = str(input(
                '\nWould you like to use a recursive search (Y/N):\t'))
        except ValueError:
            print('\nPlease use a valid value and try again')

    # When a URL doesn't have a scheme, default to https, and swap
    # 'path' with 'netloc'
    if(not rawUrl.scheme):
        rawUrl = rawUrl._replace(scheme="https")
    if(not rawUrl.netloc):
        host = rawUrl.path.split('/')[0]
        newPath = rawUrl.path.replace(host, '')
        if('.' in host):
            rawUrl = rawUrl._replace(netloc=host,
                                     path=newPath)

    # We want to append a forward slash at the end of the path
    if((len(rawUrl.path) < 2 and rawUrl.path != '/')
            or rawUrl.path[:len(rawUrl.path)-2:-1] != '/'):
        rawUrl = rawUrl._replace(path=rawUrl.path + '/')

    scrapperInstance = Scrapper(rawUrl)
    print('Base Url: {}'.format(rawUrl.geturl()))
    if (useRecursiveSearch == 'Y' or useRecursiveSearch == 'y'):
        scrapperInstance.recursiveScrape()
    else:
        scrapperInstance.normalScrape()
