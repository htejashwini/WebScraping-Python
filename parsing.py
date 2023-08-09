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

url = "https://efiling.nclt.gov.in/nclt/public/case_status.php"
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


try:
    table = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table")))
    soup = BeautifulSoup(wd.page_source, "html.parser")
    table = soup.find("table")

    csv_data = []
    for row in table.find_all("tr"):
      row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
      csv_data.append(row_data)

    if csv_data:
        columns = csv_data[0] 
        data_rows = csv_data[1:]
        df = pd.DataFrame(data_rows, columns=columns)
        df.to_csv("results.csv", index=False)

        print("Data saved to results.csv")

    else:
        print("No data found for the provided search criteria.")

except requests.exceptions.ConnectionError as conn_error:
    print("Network connection error occurred:", conn_error)

except Exception as e:
    print("Exception occurred while parsing the data:", e)

wd.quit()
