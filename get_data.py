from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd


df = pd.read_csv("post_urls.csv")
urls = df["0"].tolist()

print(f"Number of url's : {len(urls)}")


def setup():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


def parse_urls(urls):
    data = {
        "url": [],
        "title": [],
        "timestamp": [],
        "user_name": [],
        "user_title": [],
        "user_profile_link": [],
        "number_of_posts_by_user": [],
        "number_of_solutions_by_user": [],
        "number_of_kudos_by_user": [],
        "post_content": [],
        "solved": [],
        "labels_list": [],
        "number_of_views": [],
        "number_of_likes": [],
        "replies": [],
        "accepted_sol": [],
    }

    for i, url in enumerate(urls):
        print(f"Parsing url number : {i+1}")
        driver = setup()
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-title"))
            )
        except:
            print("A pinned post.(from anouncements)")
            continue

        try:
            # Title
            title = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text

            # User Details
            user_name = driver.find_element(By.CSS_SELECTOR, "a.lia-user-name-link")

            user_title = driver.find_element(
                By.CSS_SELECTOR, ".lia-message-author-rank"
            ).text.strip()

            # User Stats
            user_posts = driver.find_element(
                By.CSS_SELECTOR, ".lia-message-author-posts-count"
            ).text

            solution_by_user = driver.find_element(
                By.CSS_SELECTOR, ".lia-message-author-solutions-count"
            ).text.strip()
            user_kudos = driver.find_element(
                By.CSS_SELECTOR, ".lia-message-author-kudos-count"
            ).text.strip()

            # Timestamps,Post Content, Solved Status and accepted solution if solved
            publish_date = driver.find_element(
                By.CSS_SELECTOR, ".DateTime > meta"
            ).get_attribute("content")

            post_content = driver.find_elements(
                By.CSS_SELECTOR, ".lia-message-body-content"
            )[0]

            solved = (
                "Y"
                if driver.find_elements(
                    By.CSS_SELECTOR, ".lia-panel-feedback-banner-safe"
                )
                else "N"
            )

            accepted_sol = (
                " ".join(
                    [
                        elem.text
                        for elem in driver.find_elements(
                            By.CSS_SELECTOR, ".lia-message-body-content"
                        )[1:]
                    ]
                )
                if solved == "Y"
                else "NaN"
            )

            # Labels, Views, Likes, and Replies
            labels = [
                label.text.strip()
                for label in driver.find_elements(By.CSS_SELECTOR, ".label")
            ]

            views = driver.find_element(By.CSS_SELECTOR, ".lia-message-stats-count")

            likes = driver.find_element(By.CSS_SELECTOR, ".MessageKudosCount")

            replies = driver.find_elements(
                By.CSS_SELECTOR, ".lia-threaded-detail-display-message-view"
            )
            reply_texts = []
            for reply in replies:
                try:
                    reply_content = reply.find_element(
                        By.CSS_SELECTOR, "div.lia-message-body"
                    )
                    reply_texts.append(reply_content.text)
                except:
                    print("Nested div not found in one of the replies.")

            data["url"].append(url)
            data["title"].append(title)
            data["user_name"].append(user_name.text)
            data["user_profile_link"].append(user_name.get_attribute("href"))
            data["user_title"].append(user_title)
            data["number_of_posts_by_user"].append(user_posts)
            data["number_of_kudos_by_user"].append(user_kudos)
            data["number_of_solutions_by_user"].append(solution_by_user)
            data["timestamp"].append(publish_date)
            data["post_content"].append(post_content.text)
            data["solved"].append(solved)
            data["accepted_sol"].append(accepted_sol)
            data["labels_list"].append(labels)
            data["number_of_likes"].append(likes.text.strip())
            data["number_of_views"].append(views.text.strip() if views else "0")
            data["replies"].append(reply_texts)

        except Exception as e:
            print(f"error while parsing {url}")
            continue
    driver.quit()
    return pd.DataFrame(data)


if __name__ == "__main__":

    df = parse_urls(urls)
    df.to_csv("shopify_discussion_data.csv")
