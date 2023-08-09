import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")

chrome_service = webdriver.chrome.service.Service(ChromeDriverManager().install())

wd = webdriver.Chrome(service=chrome_service, options=chrome_options)

url = "https://nclt.gov.in/party-name-wise"
wd.get(url)

def click_accept_button():
    accept_button = wd.find_element(By.ID, "btnAccept")
    accept_button.click()

def click_hide_button():
    hide_button = wd.find_element(By.ID, "btnHide")
    hide_button.click()

try:
    WebDriverWait(wd, 30).until(EC.element_to_be_clickable((By.ID, "btnAccept")))
    click_accept_button()
except Exception as e:
    print("Error while clicking the Accept button:", e)

try:
    WebDriverWait(wd, 30).until(EC.element_to_be_clickable((By.ID, "btnHide")))
    click_hide_button()
except Exception as e:
    print("Error while clicking the Hide button:", e)


def extract_data_from_page(soup):
    table = soup.find("table")
    csv_data = []
    for row in table.find_all("tr"):
        row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        csv_data.append(row_data)
    return csv_data

try:
    all_csv_data = [] 
    previous_data = None
    headers_added = False

    while True:
        table = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table")))

        soup = BeautifulSoup(wd.page_source, "html.parser")
        csv_data = extract_data_from_page(soup)

        if headers_added:
            csv_data = csv_data[1:]

        if csv_data == previous_data:
            break

        all_csv_data.extend(csv_data)
        previous_data = csv_data

        page_links = wd.find_elements(By.CSS_SELECTOR, "ul.pagination li a")
        next_page_link = None

        for link in page_links:
            text = link.text.strip()
            if text == "Next":
                next_page_link = link

        if not next_page_link or "disabled" in next_page_link.get_attribute("class"):
            break

        next_page_link.click()
        wd.implicitly_wait(10)
        
        if not headers_added:
            headers_added = True

    if all_csv_data:
        columns = all_csv_data[0]
        data_rows = all_csv_data[1:] 
        df = pd.DataFrame(data_rows, columns=columns)
        df.to_csv("results1.csv", index=False)

        print("Data saved to results1.csv")

    else:
        print("No data found for the provided search criteria.")


except requests.exceptions.ConnectionError as conn_error:
    print("Network connection error occurred:", conn_error)

except Exception as e:
    print("Exception occurred while parsing the data:", e)

finally:
    wd.quit()

