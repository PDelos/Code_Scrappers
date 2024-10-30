import requests
import time
import random
import hashlib
import os
import json
from bs4 import BeautifulSoup
import pyperclip
from typing import Dict, Any, List, Optional

# DRIVER IMPORTS
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CodeforcesHandler:
    API_KEY: str = "apikey"
    API_SECRET: str = "apisecret"
    HANDLE: str = 'user_handle'
    PASSWORD: str = 'password'

    def __init__(self) -> None:
        self.driver: Optional[uc.Chrome] = self._setup_driver()
        self.submissions: List[Dict[str, str]] =  self.get_submissions(self.HANDLE)

    def _setup_driver(self) -> uc.Chrome:
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        options.add_argument('--lang=en-US')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Driver setup failed: {str(e)}")
            raise

    def _login(self) -> bool:
        login_url: str = "https://codeforces.com/enter"
        try:
            self.driver.get(login_url)
            wait = WebDriverWait(self.driver, 20)
            username_field = wait.until(EC.presence_of_element_located((By.ID, "handleOrEmail")))
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            username_field.send_keys(self.HANDLE)
            password_field.send_keys(self.PASSWORD)
            submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "submit")))
            submit_button.click()
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def _generate_signature(self, method: str, params: Dict[str, str]) -> tuple[str, str]:
        rand = str(random.randint(100000, 999999))
        sorted_params = sorted(params.items())
        param_strings = [f"{param}={value}" for param, value in sorted_params]
        signature_string = f"{rand}/{method}?" + "&".join(param_strings) + f"#{self.API_SECRET}"
        signature = hashlib.sha512(signature_string.encode()).hexdigest()
        return rand, signature

    def _get_api_url(self, method: str, params: Optional[Dict[str, str]] = None) -> str:
        base_api_url: str = "https://codeforces.com/api/"
        params = params or {}
        params['apiKey'] = self.API_KEY
        params['time'] = str(int(time.time()))
        rand, signature = self._generate_signature(method, params)
        params['apiSig'] = f"{rand}{signature}"
        param_strings = [f"{param}={value}" for param, value in params.items()]
        return f"{base_api_url}{method}?" + "&".join(param_strings)

    def make_request(self, method: str, params: Dict[str, str]) -> Dict[str, Any]:
        url = self._get_api_url(method, params)
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")

        data = response.json()
        if data['status'] != 'OK':
            raise Exception(f"API request failed: {data.get('comment', 'Unknown error')}")

        return data['result']
    
    def get_extension(self, language: str) -> str:
        """Returns the file extension for the given language or '.txt' if not found."""
        if "C++" in language or "GCC" in language: return ".cpp"
        if "C#" in language: return ".cs"
        if "Java" in language: return ".java"
        if "Python" in language or "PyPy" in language: return ".py"
        return ".txt"

    def get_submissions(self, handle: str) -> List[Dict[str, str]]:
        submissions = self.make_request('user.status', {'handle': handle})
        submission_details: Dict[str, str] = []

        with open('submissions.json', 'w') as file:
            json.dump(submissions, file, indent=4) 

        for sub in submissions:
            if 'contestId' in sub and 'id' in sub:
                contestType: str = "contest" if sub['contestId'] < 100000 else "gym" # gym are contests with id > 100000 starting at 100001
                details = {
                    'problem_name': f"{sub['problem']['contestId']}/{sub['problem']['index']}-{sub['problem']['name'].replace(" ", "_")}",
                    'language': sub.get('programmingLanguage', 'Unknown'),
                    'verdict': sub.get('verdict', 'Unknown'),
                    'submission_url': f"https://codeforces.com/{contestType}/{sub['contestId']}/submission/{sub['id']}" or f"https://codeforces.com/gym/{sub['contestId']}/submission/{sub['id']}"
                }
                submission_details.append(details)

        return submission_details


    def save_submission_code(self, submission: Dict[str, str]) -> bool:
        if not self.driver:
            raise Exception("You must login first")

        try:
            self.driver.get(submission['submission_url'])
            time.sleep(random.uniform(3, 5))  # Simple fixed wait

            # Get code directly from the element
            code_element = self.driver.find_element(By.CSS_SELECTOR, 'pre#program-source-text')
            code = code_element.text.strip()
            
            # Save the code
            filename = f"{submission['problem_name']}{self.get_extension(submission['language'])}"
            # Ensure the directory exists
            directory = os.path.dirname(filename)
            if directory:  # Only create if there is a directory component
                os.makedirs(directory, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(code)
                
            print(f"Code saved to {filename}")
            return True

        except Exception as e:
            print(f"Failed to save submission: {str(e)}")
            return False

    def save_all_submission_code(self) -> List[Dict[str, str]]:
        if not self._login():
            raise Exception("Login failed")

        for s in self.submissions:
            if s['verdict'] == 'OK':
                self.save_submission_code(s)
        

    def close(self) -> None:
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error while closing driver: {str(e)}")
        self.driver = None


if __name__ == "__main__":
    cf = CodeforcesHandler()
    
    try:
        cf.save_all_submission_code()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cf.close()
