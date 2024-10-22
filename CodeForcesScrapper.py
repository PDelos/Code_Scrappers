import os
import re
import requests
from bs4 import BeautifulSoup


USERNAME: str = 'Dlos'
URL: str = 'https://codeforces.com/api/user.status?'


def get_json():
    response = requests.get(URL, params={'handle': USERNAME})
    if response.status_code != 200:
        return 'Error:', response.status_code
    response_json = response.json()
    return response_json['result']


def get_submission_url(s)->tuple[str, str, str]:
    problem = s["problem"]
    problem_name = problem["index"] + '_' + problem["name"]
    programming_language = s["programmingLanguage"]

    # Extracting submission information
    contest_id = s["contestId"]
    submission_id = s["id"]
    verdict = s["verdict"]

    # Creating filename for solution
    filename = f"{contest_id}_{problem_name}_({programming_language})"

    # Submission verdict is Accepted
    codeforces_submission_url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"
    codeforces_problem_url = f"https://codeforces.com/contest/{contest_id}/problem/{problem["index"]}"
    if verdict != "OK": codeforces_submission_url = "NOT OK"
    return filename, codeforces_problem_url, codeforces_submission_url


def extract_and_save_submissions(user_submissions: list[dict]) -> None:
    folder_path = USERNAME+'_CodeForces'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for i, submission_info in enumerate(user_submissions):
        filename, problem_url, submission_url = get_submission_url(submission_info)
        if submission_url == "NOT OK": continue

        submission_response = requests.get(submission_url, allow_redirects=False)
        problem_response = requests.get(problem_url, allow_redirects=False)

        print(submission_url)
        print(problem_url)

        if submission_response.status_code != 200 or problem_response.status_code != 200: continue
        print('Requests where successful')

        soup_submission = BeautifulSoup(submission_response.content, 'html.parser')
        soup_problem = BeautifulSoup(problem_response.content, 'html.parser')
        problem_statement = soup_problem.find("div", class_="problem-statement")
        problem_statement_formatted = ""
        for tag in problem_statement.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']):
            problem_statement_formatted += tag.get_text(separator='\n') + '\n\n'  # Add line breaks after each tag


        # remove comments from cc and python and then add problem statement as code comment
        if filename.split('_')[-1][1:3] == 'C+':
            code_snippet = soup_submission.find("pre", class_="prettyprint lang-cpp linenums program-source").get_text()
            code_snippet_uncomment = re.sub(r'\/\*[\s\S]*?\*\/|\/\/.*', '', code_snippet)
            file_content = '/* \n' + problem_statement_formatted + ' */ \n \n \n \n \n' + code_snippet_uncomment
            file_content_filter = re.sub(r'[^\x00-\x7F]', '', file_content)
            with open(os.path.join(folder_path, filename+'.cc'), "w") as f:
                f.write(file_content_filter)

        if filename.split('_')[-1][1:3] == 'Py':
            code_snippet = soup_submission.find("pre", class_="prettyprint lang-py linenums program-source").get_text()
            code_snippet_uncomment = re.sub(r'# .*|(\'\'\'[\s\S]*?\'\'\'|"""[\s\S]*?""")', '', code_snippet)
            file_content = '\"\"\" \n' + problem_statement_formatted + ' \"\"\" \n \n \n \n \n' + code_snippet_uncomment
            file_content_filter = re.sub(r'[^\x00-\x7F]', '', file_content)
            with open(os.path.join(folder_path,filename+'.py'), "w") as f:
                f.write(file_content_filter)





data = get_json()
extract_and_save_submissions(data)

