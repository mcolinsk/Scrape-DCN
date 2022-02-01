import time
import subprocess
import os
import sys
import config as s
from datetime import date, datetime


def main(headless=True, options={}):
    # Use Selenium
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.action_chains import ActionChains
    import pandas as pd

    # Handle input tasks
    task = options.get("task", False)

    # Input parameters
    # Get path to downloads folder
    homeFolder = os.path.expanduser('~')
    downloadsFolder = os.path.join(homeFolder, 'Downloads')
    downloadsFolder_new = os.path.join(downloadsFolder, 'temp_dcn_downloads')
    wait_page_load = 0.100  # 100 milliseconds

    # Set chrome options src: https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196
    # List of chromedriver options: https://stackoverflow.com/questions/38335671/where-can-i-find-a-list-of-all-available-chromeoption-arguments
    chrome_options = webdriver.ChromeOptions()
    if(headless):
        # comment this out to disable headless mode and see the automation in real time.
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("-window-position=0,0")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--verbose')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": downloadsFolder_new,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })

    # Start Session. Try to start, else allow safari automation
    try:
        print("Starting session.")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options)
        print("Driver started successfully.")
    except:
        print("Session could not be started....\ntrying again")
        print(f"{bcolors.WARNING}If issues persist, see this stackoverflow page for help: https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome/62127806.{bcolors.ENDC}")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options)
        print("Driver started successfully.")

    print(f'Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # function to handle setting up headless download
    enable_download_headless(driver, downloadsFolder_new)
    query_url=f'{s.site_url}?phrase='
    if hasattr(s,'location'):
        query_url += f'&location={s.location}'
    if hasattr(s,'company_name'):
        query_url += f'&company_name={s.company_name}'
    driver.get(query_url)

    # Get query information
    elem_search_total = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'search-results__total')))
    search_title = elem_search_total.get_attribute("innerText")  # 346 found
    num_results = int(search_title.split(" ", 1)[0])
    if num_results==0:
        # print(f"{bcolors.HEADER}DCN data output saved to file:{bcolors.ENDC} {path}")
        print(f'{bcolors.UNDERLINE}{bcolors.FAIL}No results found for query:{bcolors.ENDC} {query_url}')
        print(f'{bcolors.OKGREEN}Drive closing{bcolors.ENDC}')
        return
        
    # Get pages
    elem_pages = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'pagination-pages')))
    ele_pages_list = elem_pages.find_elements(By.CSS_SELECTOR, "li")
    num_pages = 1
    if len(ele_pages_list) >0:
        num_pages = int(
            ele_pages_list[len(ele_pages_list)-1].get_attribute("innerText"))
    print(f"{bcolors.OKGREEN}{num_results} results found on a total of {num_pages} pages for the company query: {bcolors.ENDC}{s.company_name}")

    data = []
    # Loop through each page
    for i in range(1, num_pages+1):
    # for i in range(1, 3):
        print(f"Parsing page {i} of {num_pages}")
        req_url = f'{query_url}&ccpage={i}'
        driver.get(req_url)
        elem_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cards')))
        elem_card_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'cards-item')))
        # Build list of item urls
        item_urls = []
        for j in elem_card_items:
            elem_card_item = j
            elem_card_item_a = elem_card_item.find_element(
                By.CSS_SELECTOR, ".cards-title a")
            item_urls.append(elem_card_item_a.get_attribute('href'))

        # Go to each URL
        for j in item_urls:
            # j = item_urls[0]
            driver.get(j)
            skip_sections = [1]  # 1=certificate
            elem_content = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.content-left .content')))
            # elem_content_sect=elem_content[9]
            # highlight(elem_content[9])
            obj_k_v_pairs={}
            obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':'url','val':j}
            for count, elem_content_sect in enumerate(elem_content):
                if count in skip_sections:
                    continue
                key=""
                val=""
                if(count == 0):
                    try:
                        key = elem_content_sect.find_element(By.CLASS_NAME,"content-title").get_attribute('innerText')
                        val = elem_content_sect.find_element(By.TAG_NAME,"time").get_attribute('innerText')
                        obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                    except Exception as err:
                        print(err)
                elif (count == 2):
                    key = "Region"
                    try:
                        val = elem_content_sect.find_element(By.CLASS_NAME,"datalist").get_attribute('innerText').strip()
                        obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                    except Exception as err:
                        print(err)
                elif(count==3):
                    key = "Hwy"
                    try:
                        val = elem_content_sect.find_element(By.CLASS_NAME,"datalist").get_attribute('innerText').strip()
                        obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                    except Exception as err:
                        print(err)
                else:
                    try:
                        ele_keys = elem_content_sect.find_elements(By.TAG_NAME,"dt")
                        ele_vals = elem_content_sect.find_elements(By.TAG_NAME,"dd")
                        for k, ele_key in enumerate(ele_keys):
                            key=ele_key.get_attribute('innerText')
                            val=ele_vals[k].get_attribute('innerText')
                            # print(f'{key} - {val}')
                            obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                    except Exception as err:
                        print(err)
                    
                # match count:
                #     case 0:
                #         # print(f"Section {count}")
                #         key = elem_content_sect.find_element(By.CLASS_NAME,"content-title").get_attribute('innerText')
                #         val = elem_content_sect.find_element(By.TAG_NAME,"time").get_attribute('innerText')
                #         obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                #     case 2:
                #         # print(f"Section {count}")
                #         key = "Region"
                #         val = elem_content_sect.find_element(By.CLASS_NAME,"datalist").get_attribute('innerText').strip()
                #         obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                #     case 3:
                #         # print(f"Section {count}")
                #         key = "Hwy"
                #         val = elem_content_sect.find_element(By.CLASS_NAME,"datalist").get_attribute('innerText').strip()
                #         obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
                #     case _:
                #         # print(f"Default section {count}")        
                #         ele_keys = elem_content_sect.find_elements(By.TAG_NAME,"dt")
                #         ele_vals = elem_content_sect.find_elements(By.TAG_NAME,"dd")
                #         for k, ele_key in enumerate(ele_keys):
                #             key=ele_key.get_attribute('innerText')
                #             val=ele_vals[k].get_attribute('innerText')
                #             # print(f'{key} - {val}')
                #             obj_k_v_pairs[len(obj_k_v_pairs)] = {'key':key,'val':val}
            
            # save columns to object as array row 
            build_obj={}
            for o in obj_k_v_pairs:
                col = obj_k_v_pairs[o]
                build_obj[col['key']] = col['val']
            # data[len(data)] = build_obj
            data.append(build_obj)
            
    # Save data to csv file
    df = pd.json_normalize(data)
    filename = 'DCN_data'
    homeFolder = os.path.expanduser('~')
    downloadsFolder = os.path.join(os.path.expanduser('~'), 'Downloads')
    path = os.path.join(downloadsFolder, f'{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    df.to_csv (path, index = None)
    print(f"{bcolors.HEADER}DCN data output saved to file:{bcolors.ENDC} {path}")
    return


# Initialize requirement modules. Install all if not installed.
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

# import settings from settings module

# Run main function
# Check flags first src:https://kkiesling.github.io/python-novice-gapminder-custom/32a-flags/
global f
global log_file_path
log_file_path=""
# default variables
debug = False
headless = True
options = {

}

from functions import *

# check for -a flag in arguments
if "-logoutput" in sys.argv:
    # log output to file
    disable_bcolors = True
    homeFolder = os.path.expanduser('~')
    downloadsFolder = os.path.join(os.path.expanduser('~'), 'Downloads')
    log_file_path = os.path.join(
        downloadsFolder, f'eCompliance_scrape_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    print(f"{bcolors.HEADER}Logging output to file:{bcolors.ENDC} {log_file_path}")
    sys.stdout = Logger()

if "-head" in sys.argv or "-debug" in sys.argv:
    # run headless
    print("Starting head/debug mode")
    headless = False
    debug = True
else:
    # run headless
    print("Starting headless")

start = time.time()

main(headless, options)
end = time.time()
print(f"{bcolors.OKGREEN}Runtime of the program = {end - start:.2f}s{bcolors.ENDC}")
print(f'{bcolors.OKBLUE}Code ended.{bcolors.ENDC}')

exit()
