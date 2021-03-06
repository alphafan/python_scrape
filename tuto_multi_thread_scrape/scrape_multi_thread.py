# Multi Treading Scraping

import multiprocessing as mp
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://www.youtube.com'


def crawl(url):
    """ Crawl website content from url

    Args:
        url: (str) -- Link to the page

    Returns:
        html: Page content
    """
    print('Crawling page', url, '...')
    resp = urlopen(url)
    time.sleep(.1)
    return resp.read().decode('utf-8')


def parse(html):
    """ From fetched website content extract information

    Args:
        html: Website content

    Returns:
        title: Video title
        url: Link of current page
        page_urls: List of links that will link to another video
    """
    soup = BeautifulSoup(html, features='lxml')

    # Get info of current page
    title = soup.find('h1', {'class': 'watch-title-container'}).get_text().strip()
    url = soup.find('meta', {'property': 'og:url'})['content']
    print('Parsing page', title, '...')

    # Get all links to other pages
    links = soup.find_all('a', {'href': re.compile('^/watch\?.*$'), 'title': re.compile('^.+$')})
    sub_urls = set([BASE_URL+link.get('href', '') for link in links])

    return title, url, sub_urls


def scrape_multi_thread(max_crawl=30):
    """ Scraping the YouTube website from 《奔跑吧兄弟1》第1期

    Args:
        max_crawl: Maximum crawl page number
    """
    # Start From this page to scraping data
    # 《奔跑吧兄弟1》第1期 完整版：邓超李晨PK战神金钟国 RunningManS1 20141010 【浙江卫视官方超清1080P】
    page = 'https://www.youtube.com/watch?v=qqzVIqsy_KY'

    # Flag telling if we have visited or not visited this page
    not_visited = {page, }
    visited = set()

    # Start scraping
    count = 1
    pool = mp.Pool(4)
    while len(not_visited) != 0:
        # Stop crawling if reach maximum
        if count >= max_crawl:
            break

        print('\n==> Parallel Crawling...')
        crawl_jobs = [pool.apply_async(crawl, (url, )) for url in not_visited]
        htmls = [job.get() for job in crawl_jobs]

        print('\n==> Parallel Parsing...')
        parse_jobs = [pool.apply_async(parse, (html, )) for html in htmls]
        results = [job.get() for job in parse_jobs]

        print('\n==> Simple Analysing...')
        visited.update(not_visited)
        not_visited.clear()

        for title, url, sub_urls in results:
            print(url, title)
            count += 1
            not_visited.update(sub_urls - visited)


if __name__ == '__main__':
    start = time.time()
    scrape_multi_thread()
    end = time.time()
    elapsed_time = end-start
    print('Total Time:', elapsed_time)
