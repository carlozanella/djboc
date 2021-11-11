import time
import os
import shutil
import pathlib
import json
import pandas as pd
import argparse
import tempfile

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def load_credentials(fn):
    with open(fn,"r") as f:
        j = json.loads(f.read())
    return j["email"],j["password"]

EMAIL,PASSWORD = load_credentials("creds.json")


def rename_wait(src,dst,timeout=15):
    start = time.time()
    while True:
        try:
            shutil.move(src,dst)
            return
        except FileNotFoundError:
            if time.time() - start < timeout-1:
                time.sleep(1)
            else:
                raise

def parse_results():
    r = []
    try:
        main = driver.find_element(By.ID,"table_1")
        rows = main.find_elements(By.TAG_NAME,"tr");
    except NoSuchElementException:
        return r

    for row in rows:
        # Parse rows
        cells = row.find_elements(By.TAG_NAME,"td");
        rowtext = ([cell.text for cell in cells])
        for i in range(4):
            img = cells[i].find_element(By.TAG_NAME,"img")
            if not "blank" in img.get_attribute("src"):
                rowtext[i] = img.get_attribute("src").split("/")[-1].split("_")[0].upper()
        link = cells[4].find_element(By.TAG_NAME,"a")
        parsed_call = link.get_attribute("onmouseover")[31:-1].replace('"',"").split(",")

        # Create dict
        data = {}
        data["type"] = "Person" if rowtext[0] != "" else "Entity"
        if data["type"] == "Person": data["person"] = rowtext[0]
        if data["type"] == "Entity": data["entity"] = rowtext[1]
        if rowtext[2] != "": data["AM"] = rowtext[2]
        if rowtext[3] != "": data[rowtext[3]] = rowtext[3]

        data["name"] = rowtext[4]
        data["country"] = rowtext[5]
        data["title"] = rowtext[6]
        data["subsidiary"] = rowtext[7]
        data["match"] = rowtext[8]

        data["profile_id"] = parsed_call[0]
        data["matched_name"] = parsed_call[1]
        if parsed_call[2] != "": data["gender"] = parsed_call[2]
        if parsed_call[3] != "": data["birthdate"] = parsed_call[3]
        data["match_type"] = parsed_call[4]
        if parsed_call[5] != "": data["variation"] = parsed_call[5]
        #parsed_call[6]="1" unknown! ignored

        data["link"] = link.get_attribute("href")

        r.append(data)
    return r

# TODOS:
#1. Add pagination and handle >=500 case for PDF download.

def downloadEntityPDF(profile_id,name):
    driver.execute_script("popupfunction();")
    time.sleep(0.1)
    driver.find_element(By.ID,"btn_export").click()
    time.sleep(1)
    rename_wait(f"{dldir}/Dow_Jones_Risk_And_Compliance_{profile_id}_Profile_Details.pdf",f"pdf/{name}")


parser = argparse.ArgumentParser()
parser.add_argument("name",nargs='+',help="name to run the risk assessment on")
parser.add_argument("--threshold",type=int,default=95,help="match threshold above which record details should be downloaded")
args = parser.parse_args()
NAMES = args.name
THRESHOLD = args.threshold

print("SETUP")
op = webdriver.ChromeOptions()
pdf_dir = pathlib.Path(__file__).parent / "pdf"
tempdir = tempfile.TemporaryDirectory()
dldir = tempdir.name
p = {"download.default_directory": dldir, "safebrowsing.enabled":"false"}
print(p)
op.add_experimental_option("prefs", p)
driver = webdriver.Chrome('./chromedriver',chrome_options=op)

print("LOGIN")
driver.get("https://djlogin.dowjones.com/login.asp?productname=rnc")
time.sleep(4)
email = driver.find_element(By.ID,"email")
email.send_keys(EMAIL)
pw = driver.find_element(By.ID,"password")
pw.send_keys(PASSWORD)

driver.find_element(By.CSS_SELECTOR,".solid-button.basic-login-submit").click()

time.sleep(8)


for NAME in NAMES:
    try:
        driver.find_element(By.ID,"btn10031").click()
        time.sleep(4)
    except NoSuchElementException:
        pass

    print("SEARCH: " + NAME)

    soc = driver.find_element(By.ID,"chkAC")
    am = driver.find_element(By.ID,"chkAM")
    if not soc.is_selected(): soc.click()
    if not am.is_selected(): driver.execute_script("arguments[0].click();", am)

    name = driver.find_element(By.ID,"txtName")
    name.send_keys(NAME)

    driver.find_element(By.NAME,"btn10012").click()

    time.sleep(5)
    print("GET PDF")
    driver.find_element(By.ID,"Image14").click()
    time.sleep(1)
    rename_wait(f"{dldir}/Dow_Jones_Risk_And_Compliance_Search_Details.pdf",f"pdf/{NAME}.pdf")


    print("PARSING RESULTS")
    results = parse_results()
    print(json.dumps(results,indent=1))
    df = pd.DataFrame(results)
    df.to_csv(f"pdf/{NAME}.csv",index=False)

    for item in results:
        if int(item["match"]) < THRESHOLD:
            break
        driver.get(item["link"])
        time.sleep(1)
        name = f"{NAME}_{item['match']}{item['match_type'][0]}_{item['profile_id']}.pdf"
        downloadEntityPDF(item["profile_id"],name)

driver.quit()
