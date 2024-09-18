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
        "accepted_sol": [],
        "parent_post": [], 
    }

    for i, url in enumerate(urls):
        # if i == 3: break
        print(f"Parsing url number : {i+1}")
        driver = setup()
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-title"))
            )
        except:
            print("A pinned post (from announcements).")
            continue

        try:
            # Title and User Details
            title = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text
            user_name = driver.find_element(By.CSS_SELECTOR, "a.lia-user-name-link")
            user_title = driver.find_element(By.CSS_SELECTOR, ".lia-message-author-rank").text.strip()
            user_posts = driver.find_element(By.CSS_SELECTOR, ".lia-message-author-posts-count").text
            solution_by_user = driver.find_element(By.CSS_SELECTOR, ".lia-message-author-solutions-count").text.strip()
            user_kudos = driver.find_element(By.CSS_SELECTOR, ".lia-message-author-kudos-count").text.strip()

            # Post Details
            publish_date = driver.find_element(By.CSS_SELECTOR, ".DateTime > meta").get_attribute("content")
            post_content = driver.find_element(By.CSS_SELECTOR, ".lia-message-body-content").text
            solved = "Y" if driver.find_elements(By.CSS_SELECTOR, ".lia-panel-feedback-banner-safe") else "N"
            # accepted_sol = " ".join([elem.text for elem in driver.find_elements(By.CSS_SELECTOR, ".lia-message-body-content")[1:]]) if solved == "Y" else ""
            accepted_sol = ""

            labels = [label.text.strip() for label in driver.find_elements(By.CSS_SELECTOR, ".label")]
            views = driver.find_element(By.CSS_SELECTOR, ".lia-message-stats-count").text.strip() if driver.find_elements(By.CSS_SELECTOR, ".lia-message-stats-count") else "0"
            likes = driver.find_element(By.CSS_SELECTOR, ".MessageKudosCount").text.strip()

            # Store parent post data
            data["url"].append(url)
            data["title"].append(title)
            data["user_name"].append(user_name.text)
            data["user_profile_link"].append(user_name.get_attribute("href"))
            data["user_title"].append(user_title)
            data["number_of_posts_by_user"].append(user_posts)
            data["number_of_kudos_by_user"].append(user_kudos)
            data["number_of_solutions_by_user"].append(solution_by_user)
            data["timestamp"].append(publish_date)
            data["post_content"].append(post_content)
            data["solved"].append(solved)
            data["accepted_sol"].append(accepted_sol)
            data["labels_list"].append(labels)
            data["number_of_likes"].append(likes)
            data["number_of_views"].append(views)
            data["parent_post"].append("Y")

            try:
                replies_container=driver.find_element(By.ID, "threadeddetailmessagelist")
                replies = replies_container.find_elements(By.CSS_SELECTOR, "div.lia-threaded-detail-display-message-view")
                
                for reply in replies:
                    try:
                        reply_user_name = reply.find_element(By.CSS_SELECTOR, "a.lia-user-name-link").text
                        reply_content = reply.find_element(By.CSS_SELECTOR, "div.lia-message-body").text
                        reply_timestamp = reply.find_element(By.CSS_SELECTOR, ".DateTime > meta").get_attribute("content")                        
                        reply_user_profile_link = reply.find_element(By.CSS_SELECTOR, "a.lia-user-name-link").get_attribute("href")
                        reply_user_title = reply.find_element(By.CSS_SELECTOR,"div.lia-message-author-rank").text
                        reply_user_posts = reply.find_element(By.CSS_SELECTOR,"span.lia-message-author-posts-count").text
                        reply_user_kudos_count = reply.find_element(By.CSS_SELECTOR,"span.lia-message-author-kudos-count").text
                        reply_user_sol_count = reply.find_element(By.CSS_SELECTOR,"span.lia-message-author-solutions-count").text
                        reply_user_sol_likes = reply.find_element(By.CSS_SELECTOR,"span.lia-component-kudos-widget-message-kudos-count").text
                        accepted_reply_or_not = "Y" if reply.find_elements(By.CSS_SELECTOR, "p.accepted-solution-text") else "N"
                        
                        # store each reply data
                        data["url"].append(url)
                        data["title"].append(f"Reply to {title}")
                        data["user_name"].append(reply_user_name)
                        data["user_profile_link"].append(reply_user_profile_link)  
                        data["user_title"].append(reply_user_title)
                        data["number_of_posts_by_user"].append(reply_user_posts)
                        data["number_of_kudos_by_user"].append(reply_user_kudos_count)
                        data["number_of_solutions_by_user"].append(reply_user_sol_count)
                        data["timestamp"].append(reply_timestamp)
                        data["post_content"].append(reply_content)
                        data["solved"].append("")
                        data["labels_list"].append("")
                        data["number_of_likes"].append(reply_user_sol_likes)
                        data["number_of_views"].append("")
                        data["parent_post"].append("N")
                        data["accepted_sol"].append(accepted_reply_or_not)
                    except Exception as e:
                        print("Error extracting reply details:", e)
            except:
                print("No replies found for this post")

        except Exception as e:
            print(f"Error while parsing {url}: {e}")
            continue

        finally:
            driver.quit()

    return pd.DataFrame(data)


if __name__ == "__main__":

    df = parse_urls(urls)
    df.to_csv("shopify_discussion_data.csv", index=False)
    print("Parsing Successful")
    print(f"Total items in dataset: {len(df)}")
