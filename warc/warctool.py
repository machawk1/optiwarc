"""
warctool
~~~~~~~~

Command-line utility to work with WARC files.

:copyright: (c) 2012 by Anand Chitipothu.
"""

import sys
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

import requests
from requests import async
import warc

logger = logging.getLogger("warctool")

headers = {
    "User-Agent": "warctool/0.1 python-requests/%s (admin-contact: anandology at gmail.com)" % (requests.__version__),
#    'Accept-Encoding': 'gzip, deflate, compress, identity'
    'Accept-Encoding': 'identity'
}

def get(urls):
    session = requests.session(headers=headers)
    for url in urls:
        download(session, url)

def get_async(urls):
    reqs = (async.get(url) for url in urls)
    for response in async.map(reqs, size=2):
        logger.info("downloaded %s", response.request.full_url.encode('utf-8'))
        record = warc.WARCRecord.from_response(response)
        sys.stdout.write(str(record))
        sys.stdout.flush()

def download(session, url):
    for i in range(5):
        logger.info("downloading %s", url)
        response = requests.get(url)
        record = warc.WARCRecord.from_response(response)

        # flipkart returns empty response sometimes. Retry in that case.
        if False and not response.text:
            logger.info("record size %s %s", record["content-length"], len(response.content))
            logger.warning("empty response, retrying...")
            continue

        sys.stdout.write(str(record))
        sys.stdout.flush()

        print "size", len(response.content)
        return

    logger.error("failed to download %s", url)
 

def main():
    urls = open(sys.argv[1]).read().split()
    get(urls)
     
if __name__ == "__main__":
    main()
