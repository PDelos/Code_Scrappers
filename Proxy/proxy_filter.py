import requests
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import logging


INPUT_FILE: str = "proxy_list.txt"
OUTPUT_FILE: str = "proxy_list_filtered.txt"


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_proxies(filename: str) -> list[str]:
    """Load a list of proxies from a file."""
    with open(filename, "r") as f:
        return f.read().splitlines()

def check_proxy(proxy: str) -> str | None:
    """Check if a proxy is valid by making a request to ipinfo.io."""
    try:
        response = requests.get("https://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            logging.info(f"Valid proxy found: {proxy}")
            return proxy
    except requests.RequestException:
        logging.debug(f"Invalid proxy: {proxy}")
    return None

def filter_proxies(proxy_list: list[str], max_workers:int=10) -> list[str]:
    """Filter a list of proxies using multiple threads."""
    valid_proxies: list[str] = list()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(check_proxy, proxy_list)
        valid_proxies = [proxy for proxy in results if proxy]
    return valid_proxies

def save_proxies(filename, proxies):
    """Save a list of proxies to a file."""
    with open(filename, "w") as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def main():
    """Main function."""
    proxies: list[str] = load_proxies(INPUT_FILE)
    valid_proxies = filter_proxies(proxies)
    save_proxies(OUTPUT_FILE, valid_proxies)

if __name__ == "__main__":
    main()