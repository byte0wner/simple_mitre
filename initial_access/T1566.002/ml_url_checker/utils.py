import tldextract
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

# https://github.com/PeterDaveHello/url-shorteners/blob/master/list
URL_SHORTENERS = set(line.strip() for line in open('url_shorteners.txt'))

custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    "Accept-Encoding": "*",
    "Connection": "keep-alive",
    'Content-Type': 'application/json',
    'accept': 'application/json',
}

benign_urls_path = "datasets/legit_urls.csv"
malicious_urls_path = "datasets/mal_urls.csv" 

SCREEN_PATH = "screenshots"

model_filename = "phishing_model.json"

target_urls_for_test = [
            "http://viacripto.com.cryptonexum.com/",
            "https://regex101.com/account/mine",
            "https://cocorost-556.jp/mail/GlobalSources/?email=3mail@a.b.c0",
            "https://toki-basvurum.xyz/",
            "https://passport.yandex.ru/auth",
            "https://en.wikipedia.org/wiki/Regular_expression",
            "https://attack.mitre.org/techniques/enterprise/",
            "https://www.imdb.com/list/ls4155868532/",
        ]

def get_days_diff_from_time(first_date, second_date = datetime.now(timezone.utc)):
    time_diff = second_date - first_date
    days_diff = time_diff.days
    return days_diff

def extract_path_from_domain(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path

def extract_suffix_from_domain(domain):
    extracted_domains = tldextract.extract(domain)
    return extracted_domains.suffix

def extract_domain_without_subdomains(url):
    extracted_domains = tldextract.extract(url)
    domain_without_subdomains = f"{extracted_domains.domain}.{extracted_domains.suffix}"
    return domain_without_subdomains
    
def extract_domain_with_subdomains(url):
    extracted_domains = tldextract.extract(url)
    domain_with_subdomains = f"{extracted_domains.subdomain}.{extracted_domains.domain}"
    if domain_with_subdomains.startswith("www."):
        domain_with_subdomains = domain_with_subdomains[4:]
    return domain_with_subdomains

def extract_domain_without_path(url):
    domains = tldextract.extract(url)
    full_domain = f"{domains.subdomain}.{domains.domain}.{domains.suffix}"
    if full_domain.startswith("www."):
        full_domain = full_domain[4:]
    return full_domain

def find_rdap_endpoint(domain_name):
    suffix = extract_suffix_from_domain(domain_name)
    print(suffix)
    with open("rdap_endpoints.json") as file:
        buffer = file.read()
        iana_database = json.loads(buffer)
        endpoints_list = iana_database["services"]
        for entry in endpoints_list:
            if suffix in entry[0]:
                rdap_endpoint = entry[1][0] + "domain/"
                return rdap_endpoint
    return None