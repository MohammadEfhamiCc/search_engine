# creator: A NOOB programmer
# Episode one of suffering
# MES
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import re
import sys
import os
import subprocess
import argparse

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', '-d', required=True)# keep in mind that every domine should look like this url https://www.sherlock-holm.es
    parser.parse_args()
    args = parser.parse_args()
    domain = args.domain
    output_file = "urls.txt"
    print("domain:", domain)
    print("output:", output_file)
    print("######################################################")
    url_extractor(domain, output_file)
    print("######################################################")

def initial_lists(domain):
    urls_unfinished = deque([domain])
    urls_finished = set()
    urls_internal = set()
    urls_external = set()
    urls_failed = set()
    return urls_unfinished,urls_finished,urls_internal,urls_external,urls_failed

def write_results(output_file, urls_internal):
    with open(output_file, 'w') as f:
        print("####################################################################", file=f)
        print("--------------------------------------------------------------------", file=f)
        print("####################################################################", file=f)
        print("internal urls:", file=f)
        for j in urls_internal:
            print(j, file=f)

def url_extractor(domain, output_file):
    exceptions=requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema
    try:
        list_structure=initial_lists(domain)
        while len(list_structure[0]):
            url = list_structure[0].popleft()
            list_structure[1].add(url)
            print(len(list_structure[0]))
            print("---------->> %s" % url)
            try:
                response = requests.head(url)
            except exceptions:
                list_structure[4].add(url)
                continue
            if 'content-type' in response.headers:
                content_type = response.headers['content-type']
                if not 'text/html' in content_type:
                    continue
            try:
                response = requests.get(url)
            except exceptions:

                list_structure[4].add(url)
                continue
            parts = urlsplit(url)
            print("schme is:"+parts.scheme)
            print("//////////////////////////////////////////////////////////")
            print("netloc is:"+parts.netloc)
            print("//////////////////////////////////////////////////////////")
            print("path is:"+parts.path)
            print("//////////////////////////////////////////////////////////")
            print("query is:"+parts.query)
            print("####################################################################################")
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url
            soup = BeautifulSoup(response.text, "lxml")
            for link in soup.find_all('a'):
                temp_base = link.attrs["href"] if "href" in link.attrs else ''
                if temp_base.startswith('/'):
                    local_link = base_url + temp_base
                    list_structure[2].add(local_link)
                elif strip_base in temp_base:
                    list_structure[2].add(temp_base)
                elif not temp_base.startswith('http'):
                    local_link = path + temp_base
                    list_structure[2].add(local_link)
                else:
                    list_structure[3].add(temp_base)

            for i in list_structure[2]:
                if not i in list_structure[0] and not i in list_structure[1]:
                    list_structure[0].append(i)
        return write_results(output_file,list_structure[2])       
    
    except KeyboardInterrupt:
        sys.exit()



if __name__ == "__main__":
    main(sys.argv)