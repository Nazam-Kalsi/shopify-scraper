from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd


df = pd.read_csv('post_urls.csv')
urls = df["0"].tolist()

print(len(urls))

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
        "url": [], "title": [], "timestamp": [], "user_name": [], "user_title": [], "user_profile_link": [], 
        "number_of_posts_by_user": [], "number_of_solutions_by_user": [], "number_of_kudos_by_user": [], 
         "post_content": [], "solved": [], "labels_list": [], 
        "number_of_views": [], "number_of_likes": [], "replies": [], "accepted_sol": []
    }

    for i,url in enumerate(urls):
        driver = setup()
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-title")))       
        except:
            print("A pinned post.(from anouncements)")
            continue
         

        # Add URL to the data
        data["url"].append(url)

        # Title
        title = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text
        data["title"].append(title)

        # User Details
        user_name = driver.find_element(By.CSS_SELECTOR, "a.lia-user-name-link")
        data["user_name"].append(user_name.text)
        
        data["user_profile_link"].append(user_name.get_attribute("href"))

        user_title = driver.find_element(By.CSS_SELECTOR, ".lia-message-author-rank").text.strip()
        data["user_title"].append(user_title)

        # User Stats
        data["number_of_posts_by_user"].append(driver.find_element(By.CSS_SELECTOR, ".lia-message-author-posts-count").text)
        data["number_of_solutions_by_user"].append(driver.find_element(By.CSS_SELECTOR, ".lia-message-author-solutions-count").text.strip())
        data["number_of_kudos_by_user"].append(driver.find_element(By.CSS_SELECTOR, ".lia-message-author-kudos-count").text.strip())

        # Timestamps,Post Content, Solved Status and accepted solution if solved
        publish_date = driver.find_element(By.CSS_SELECTOR, ".DateTime > meta").get_attribute("content")
        data["timestamp"].append(publish_date)

        post_content = driver.find_elements(By.CSS_SELECTOR, ".lia-message-body-content")[0]
        data["post_content"].append(post_content.text)

        solved = "Y" if driver.find_elements(By.CSS_SELECTOR, ".lia-panel-feedback-banner-safe") else "N"
        data["solved"].append(solved)

        accepted_sol = ' '.join([elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".lia-message-body-content")[1:]]) if solved == "Y" else "NaN"
        data["accepted_sol"].append(accepted_sol)

        # Labels, Views, Likes, and Replies
        labels = [label.text.strip() for label in driver.find_elements(By.CSS_SELECTOR, ".label")]
        data["labels_list"].append(labels)

        views = driver.find_element(By.CSS_SELECTOR, ".lia-message-stats-count")
        data["number_of_views"].append(views.text.strip() if views else "0")

        likes = driver.find_element(By.CSS_SELECTOR, ".MessageKudosCount")
        data["number_of_likes"].append(likes.text.strip())

        replies = driver.find_elements(By.CSS_SELECTOR, ".lia-threaded-detail-display-message-view")
        reply_texts = []
        for reply in replies:                
                try:
                    reply_content = reply.find_element(By.CSS_SELECTOR, "div.lia-message-body")
                    reply_texts.append(reply_content.text)
                except:
                    print("Nested div not found in one of the replies.")
        
        data["replies"].append(reply_texts)


    return pd.DataFrame(data)


if __name__ == "__main__":

    df = parse_urls(urls)
    df.to_csv("shopify_discussion_data.csv")
