import os
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


USERNAME: str = 'poldelossantos@gmail.com'
PASSWORD: str = 'CLWVPNn4HqjcxHcbmK5'
LOGIN_URL = 'https://jutge.org/'
URL: str = 'https://jutge.org/problems/accepted'

options = webdriver.EdgeOptions()
driver = webdriver.Edge(options=options)
#driver = webdriver.Chrome()  # or any otajpj

if not os.path.exists("jutge_problems"):
    os.makedirs("jutge_problems")

# driver EDGE login jutge
driver.get(LOGIN_URL)
# Find the username and password fields and fill them
driver.find_element("id", "email").send_keys(USERNAME)
# find password input field and insert password as well
driver.find_element("id", "password").send_keys(PASSWORD)
# click login button
driver.find_element("name", "submit").click()

cookies = driver.get_cookies()


#
# Creating a requests session
session = requests.Session()
# Adding cookies to the requests session
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# Now you can make requests using the session
jutge_problems = session.get(URL)
# You can parse the HTML response using BeautifulSoup
problems_list_soup = BeautifulSoup(jutge_problems.content, 'html.parser')

# Find all <a> tags that do not have 'pdf' in the href attribute
links_without_pdf = problems_list_soup.find_all('a', href=lambda href: href and 'pdf' not in href)
links = [link['href'] for link in links_without_pdf if re.match(r"/problems/[A-Z0-9]+_[a-z]{2}", link['href'])]

# Extract the href attribute from each link
for problem_link in links:
    link_submission = f"https://jutge.org{problem_link}/submissions"

    submission_response = session.get(link_submission)
    soup_submission = BeautifulSoup(submission_response.content, 'html.parser')

    table_rows = soup_submission.find('table', class_='table').find_all('tr')

    green_links = list()
    for row in table_rows:
        if not row.find('img', {'src': '/ico/green-bullet.png'}): continue
        hrefs = [l['href'] for l in row.find_all('a', href=True)]
        green_links += [f"https://jutge.org{href}/program" for href in hrefs if re.match(r'.*\/S\d{3}$', href)]


    if not os.path.exists(f"jutge_problems/{problem_link[10:]}"):
        os.makedirs(f"jutge_problems/{problem_link[10:]}")

    print(green_links)
    for code_link in green_links:
        code_response = session.get(code_link)

        soup = BeautifulSoup(code_response.content, 'html.parser')

        # Find the <pre> tag with class "pre-white no-border"
        pre_tag = soup.find('pre', class_='pre-white no-border')
        if pre_tag:
            code_txt = pre_tag.get_text()

            submission = f"jutge_problems/{problem_link[10:]}/{code_link[-12:-8]}.txt"
            with open(submission, 'w') as file:
                file.write(code_txt)

