from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import os
import pandas as pd


def setup():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=chrome_options)


def save_data_to_file(data, filename):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{filename}", "w", encoding="utf-8") as file:
        file.write(data)


# Scrape Discussion URLs
def get_discussion_urls():
    driver = setup()
    driver.get(
        "https://community.shopify.com/c/shopify-discussion/ct-p/shopify-discussion"
    )

    while True:
        try:
            load_more_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.more-boards"))
            )
            load_more_btn.click()
        except:
            break

    # Extract the discussion URLs except anouncements
    discussions_urls = [
        url.get_attribute("href")
        for url in driver.find_elements(By.CSS_SELECTOR, ".tiled-navigation-boards>a")[
            :-1
        ]
    ]
    return discussions_urls


# Scrape Posts_urls from each Discussion form
def scrape_post_urls_from_discussion(url):
    driver = setup()
    driver.get(url)
    post_urls = []

    page_no = 1
    while True:
        print(f"Processing page {page_no} from : {url.split('/')[-1]}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.res-data"))
        )

        links = driver.find_elements(By.CSS_SELECTOR, "div.res-subject > a")

        for link in links:
            post_urls.append(link.get_attribute("href"))

        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@class='pagination-div']/a[@class='page' and text()='Next']",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", next_button)
            page_no += 1

        except (TimeoutException, NoSuchElementException):
            print(f"Reached last page for url: {url}")
            break

        except Exception as e:
            print(f"error : {e}")

    print(f"Total url from {url} are : {len(post_urls)}")
    return post_urls


def save_post_urls_to_csv(post_urls, filename="post_urls.csv"):
    df = pd.DataFrame(post_urls)
    df.to_csv(filename, index=False)


if __name__ == "__main__":

    discussion_urls = get_discussion_urls()  # Scraping discussion URLs.

    post_urls = []
    for url in discussion_urls: # Scrape posts for each discussion url
        section_urls = scrape_post_urls_from_discussion(
            url
        )  
        post_urls.extend(section_urls)
    print(f"Total url's : {len(post_urls)}")
    save_post_urls_to_csv(post_urls)
