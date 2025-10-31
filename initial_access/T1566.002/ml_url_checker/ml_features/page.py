import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import utils
import os
import requests

from urllib.parse import urljoin, urlparse

def ssl_check(url):
    ssl_error = False
    try:
        response = requests.get(url, timeout=10, headers=utils.custom_headers, )
    except requests.exceptions.SSLError as e:
        ssl_error = True
    return ssl_error

def check_has_iframe(soup):
    has_iframe = False
    iframe = soup.find('iframe')

    if iframe:
        has_iframe = True

    return has_iframe

def hyperlink_ratio(soup, url):
    domain = urlparse(url).netloc

    a_tags = soup.find_all('a', href=True)
    total_links = len(a_tags)

    internal_links = 0
    external_links = 0

    if total_links == 0:
        no_hyperlink = 1
        internal_ratio = 0.0
        external_ratio = 0.0
    else:
        no_hyperlink = 0
        for tag in a_tags:
            href = tag['href']
            abs_url = urljoin(url, href)
            parsed_href = urlparse(abs_url)

            if parsed_href.scheme in ('http', 'https'):
                if parsed_href.netloc == domain:
                    internal_links += 1
                else:
                    external_links += 1

        internal_ratio = internal_links / total_links
        external_ratio = external_links / total_links

    return no_hyperlink, internal_ratio, external_ratio

def check_suspicious_js_patterns(scripts):
    return

def check_js_obfuscation(scripts):
    hex_obfuscation = False
    mangle_obfuscation = False
    bytes_obfuscation = False
    concat_obfuscation = False
    base64_obfuscation = False

    # var _0x37b8
    hexes_re = r"_0x\w+\b"
    
    # mangled: short identifier names like a, b, c
    mangle_re = r"\b[a-z]{1}\b"

    # unique set of 64 chars
    base64_re = r"(\batob\(|\bbtoa\(|(\"|').{64}(\"|'))"

    for script in scripts:
        print(":A")


    # "\x75\x73\x65\x20\x73\x74\x72\x69\x63\x74"
    # https://www.meshsecurity.io/blog/phishing-analysis-the-secrets-of-a-html-file

    # numbers to expressions
    # const foo=-0xd93+-0x10b4+0x41*0x67+0x84e*0x3+-0xff8;
    # 'ab' + 'cd' + 'ef' + 'g';

    # concat obfuscation

    # array buffers

    # large base64 strings

    # fromCharCode

def check_redirects(url):
    number_of_redirects = 0
    response = requests.get(url, verify=False, allow_redirects=True, headers=utils.custom_headers, timeout=10)
    if response.history:
        number_of_redirects = len(response.history)

    return number_of_redirects

def check_password_field(soup):
    has_password = False
    password_fields = soup.find_all('input', {'type': 'password'})

    if password_fields:
        has_password = True
    return has_password

def extract_page_features(url):
    response = requests.get(url, verify = False, headers = utils.custom_headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    ssl_error = ssl_check(url)
    iframe = check_has_iframe(soup)
    no_hyperlink, internal_ratio, external_ratio = hyperlink_ratio(soup, url)
    number_of_redirects = check_redirects(url)
    has_password = check_password_field(soup)

    features = {
        'ssl_error': ssl_error,
        'iframe': iframe,
        'no_hyperlink': no_hyperlink,
        'internal_ratio': internal_ratio,
        'external_ratio': external_ratio,
        'number_of_redirects': number_of_redirects,
        'has_password': has_password,
    }

    return features
