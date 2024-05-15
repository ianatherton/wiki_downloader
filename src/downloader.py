import os
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

def is_valid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme) and bool(parsed_url.netloc)

def download_page(url, base_dir, driver):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.find('title').text.strip()
        filename = re.sub(r'[<>:"/\\|?*]', '_', title) + ".html"
        filepath = os.path.join(base_dir, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(page_source)
        logging.info(f"Downloaded and saved: {filename}")
        print(f"Downloaded: {filename}")
        return True
    except (NoSuchElementException, TimeoutException):
        logging.error(f"Failed to download: {url}. Page not found (404 error).")
        print(f"Failed to download: {url}. Page not found (404 error).")
        return False
    except WebDriverException as e:
        logging.error(f"Failed to download: {url}. Error: {str(e)}")
        print(f"Failed to download: {url}. Error: {str(e)}")
        return False

def extract_links(url, base_url, driver):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        valid_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            logging.debug(f"Found link: {href}")
            absolute_url = urljoin(base_url, href)
            absolute_url = absolute_url.split('#')[0]
            if (is_valid_url(absolute_url) and
                absolute_url.startswith(base_url) and
                not absolute_url.startswith(base_url + '/Special:')):
                valid_links.append(absolute_url)
        logging.info(f"Found {len(valid_links)} valid links on page: {url}")
        return list(set(valid_links))
    except Exception as e:
        logging.error(f"Failed to retrieve links from page: {url}. Error: {str(e)}")
        return []

def load_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, 'rb') as file:
            progress = pickle.load(file)
        logging.info(f"Loaded progress from {progress_file}")
        return progress
    else:
        return set(), [], 0

def save_progress(visited_pages, pages_to_visit, total_pages, progress_file):
    progress = (visited_pages, pages_to_visit, total_pages)
    with open(progress_file, 'wb') as file:
        pickle.dump(progress, file)
    logging.info(f"Saved progress to {progress_file}")

def download_wiki(base_url, base_dir, progress_file):
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    driver = webdriver.Chrome(options=chrome_options)
    visited_pages, pages_to_visit, total_pages = load_progress(progress_file)
    if not pages_to_visit:
        pages_to_visit.append(base_url)
    while pages_to_visit:
        url = pages_to_visit.pop(0)
        if url in visited_pages:
            logging.debug(f"Skipping already visited page: {url}")
            continue
        logging.info(f"Downloading: {url}")
        print(f"Downloading: {url}")
        success = download_page(url, base_dir, driver)
        if success:
            visited_pages.add(url)
            links = extract_links(url, base_url, driver)
            logging.info(f"Extracted {len(links)} unique links from page: {url}")
            for link in links:
                if link not in visited_pages:
                    pages_to_visit.append(link)
                    logging.debug(f"Added new page to visit: {link}")
                else:
                    logging.debug(f"Skipping already visited link: {link}")
            total_pages += 1
            logging.info(f"Progress: Downloaded {total_pages} pages.")
            print(f"Progress: Downloaded {total_pages} pages.")
            save_progress(visited_pages, pages_to_visit, total_pages, progress_file)
        else:
            logging.warning(f"Retrying download after a delay...")
            print(f"Retrying download of {url} after a delay...")
            time.sleep(5)
            pages_to_visit.append(url)
    driver.quit()
    logging.info("Wiki download completed.")
    print("Wiki download completed.")