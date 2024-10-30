# Code_Scrappers

Welcome to the **Code_Scrappers** repository! This collection contains various scripts I’ve developed over the years for scraping code submissions from different platforms. These scripts leverage powerful libraries and techniques to automate the retrieval and organization of programming contest submissions.

## Overview

This repository includes:

1. **CodeforcesHandler**: A comprehensive script for logging into Codeforces, retrieving user submissions, and saving the code to local files.
2. **Proxy Filter**: A multithreaded proxy checker that filters out valid proxies from a provided list.
3. **Jutge Scraper**: An incomplete script designed to scrape submission codes from the Jutge.org platform, utilizing rotating proxies for rate-limiting management.

## Script Breakdown

### 1. CodeforcesHandler

This script automates the process of logging into Codeforces and retrieving user submission details.

**Key Features**:
- **Login Handling**: Automates the login process using Selenium.
- **API Interaction**: Retrieves user submissions via the Codeforces API, ensuring secure access with a generated signature.
- **Code Storage**: Saves the code for each successful submission in appropriately named files, categorized by problem and language.

**Usage**:
- Set your API key, secret, user handle, and password at the top of the script.
- Run the script, and it will log in and save your accepted submissions' code.

### 2. Proxy Filter

This script checks a list of proxies and filters out the valid ones using multithreading for efficiency.

**Key Features**:
- **Load and Save Proxies**: Loads proxies from a file, checks their validity, and saves the valid ones to a new file.
- **Multithreaded Checking**: Utilizes `ThreadPoolExecutor` for concurrent requests, speeding up the validation process.

**Usage**:
- Place your list of proxies in `proxy_list.txt`.
- Run the script to generate a list of valid proxies in `proxy_list_filtered.txt`.

### 3. Jutge Scraper

This script is designed to scrape programming submissions from Jutge.org. It effectively logs in, fetches problem links, and extracts submission codes, ensuring smooth operation even under rate limiting through the use of rotating proxies.

**Key Features**:
- **Session Management**: Maintains a session with cookies after logging in to ensure seamless access.
- **Code Extraction**: Identifies and downloads submission codes based on problem links.
- **Rotating Proxies**: Utilizes rotating proxies to avoid rate limiting and ensure consistent scraping performance.

**Usage**:
- Set your login credentials and configure the list of rotating proxies. Run the script to start scraping submissions without interruption.


## Important Disclaimer: Web Scraping

While this repository contains scripts for web scraping, it's essential to recognize the following points:

1. **Legal Considerations**: Always check the terms of service of the website you intend to scrape. Many sites explicitly prohibit scraping, and violating these terms may lead to legal consequences.

2. **Ethical Practices**: Scraping can put a load on a website's server. Please ensure that your scraping activities do not disrupt the normal functioning of the site. Use polite scraping practices like: limiting request rates, and respecting the site's bandwidth.

3. **Data Privacy**: Be mindful of the data you collect. Personal or sensitive information should be handled with care and in compliance with relevant data protection regulations.

4. **Rate Limiting**: To avoid being blocked or throttled, implement strategies such as rotating proxies and randomizing request intervals. Always be respectful of the site's usage limits.

By using the scripts in this repository, you acknowledge that you are responsible for ensuring compliance with applicable laws and ethical guidelines. Use these tools wisely and responsibly.


## Contributing

Feel free to contribute by submitting issues or pull requests. Your feedback and suggestions are always welcome!
