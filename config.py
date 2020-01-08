from typing import List

userAgents = {
    'Mozilla': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) \
                Gecko/20100101 Firefox/71.0',
    'Google': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 \
            Mobile Safari/537.36'}

headers = {'Accept': 'text/html'}

supportedPlatforms = {
    "instagram": {
        "scheme": "https",
        "subdomains": ["www"],
        "host": "instagram",
        "tld": "com"
    },
    "twitter": {
        "scheme": "https",
        "subdomains": ["www"],
        "host": "twitter",
        "tld": "com"
    },
    "github": {
        "scheme": "https",
        "subdomains": ["www"],
        "host": "github",
        "tld": "com"
    },
    "linkedin": {
        "scheme": "https",
        "subdomains": ["www"],
        "host": "linkedin",
        "tld": "com"
    }
}


class SocialPlatform:
    __scheme: str
    __subdomains: List[str]
    __host: str
    __tld: str

    def __init__(self, scheme: str, subdomains: List[str],
            host: str, tld: str):
        self.__scheme = scheme
        self.__subdomains = subdomains
        self.__host = host
        self.__tld = tld

    def getScheme(self) -> str:
        return self.__scheme
    
    def getSubdomains(self) -> List[str]:
        return self.__subdomains

    def getHost(self) -> str:
        return self.__host

    def getTLD(self) -> str:
        return self.__tld
