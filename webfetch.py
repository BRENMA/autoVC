from urllib.parse import urlparse, urljoin
import requests
from lxml import html

foundUrls = []

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def queryWeb(item):
    url = str(item)
    
    domain_name = urlparse(url).netloc + urlparse(url).path

    urls = []
    try:
        web_response = requests.get(url)
        status = web_response.status_code

        if status == 200:
            byte_string = web_response.content
            source_code = html.fromstring(byte_string)
            tree = source_code.xpath('//a/@href')

            for href in tree:
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

                if href == "" or href is None:
                    continue

                if domain_name not in parsed_href.netloc + parsed_href.path:
                    continue

                if '.png' in href:
                    continue

                if '.jpg' in href:
                    continue

                if '.pdf' in href:
                    continue

                if '.svg' in href:
                    continue

                if '.ts' in href:
                    continue

                if '.py' in href:
                    continue

                if '.sol' in href:
                    continue
                
                if '.html' in href:
                    continue
                
                if '.js' in href:
                    continue
                
                if '.xml' in href:
                    continue

                if '.txt' in href:
                    continue

                if '.csv' in href:
                    continue

                if '.yaml' in href:
                    continue

                if not is_valid(href):
                    continue

                test_set = {str(parsed_href.path)}
                overlapAlreadyInner = set.intersection(set(urls) & test_set)
                if(len(overlapAlreadyInner) > 0):
                    continue   

                urls.append(href)
    except:
        print("fail")

    return urls

def addIf(urlP):
    for url in urlP:
        if url not in foundUrls: foundUrls.append(url)

def loop(url):
    domain_name = urlparse(url)
    webpageUrlMaster = (domain_name.scheme + "://" + domain_name.hostname + domain_name.path)

    print(f'\n {webpageUrlMaster} \n')

    foundUrls.append(webpageUrlMaster)

    urlGroupInit = queryWeb(webpageUrlMaster)
    addIf(urlGroupInit)

    for url in foundUrls:
        urlGroup = queryWeb(url)
        addIf(urlGroup)
        print(f'\n {foundUrls}')

    data = ','.join([str(i) for i in foundUrls])
    with open('urls.csv', 'w',  encoding="utf-8", newline='') as file:
        file.write(data)  
