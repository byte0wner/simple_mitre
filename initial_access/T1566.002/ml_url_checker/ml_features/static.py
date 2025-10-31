import re
import utils
from urllib.parse import urlparse
import math
from collections import Counter


def check_domain_repeated_chars(url):
    domain = utils.extract_domain_with_subdomains(url)
    chars = []
    char = None
    char_counter = 0
    for letter in domain:
        if letter == char:
            char_counter += 1
        elif char_counter != 0:
            chars.append(char_counter)
            char_counter = 0
        char = letter

    if len(chars) == 0:
        if char_counter > 0:
            chars.append(char_counter)
        else:
            return len(chars), 0
    return len(chars), max(chars)

def domain_entropy(url):
    domain = utils.extract_domain_with_subdomains(url)
    char_counts = Counter(domain)
    total_chars = len(domain)
    
    entropy = 0.0
    
    # H = -Σ p(x)log2(p(x))
    for count in char_counts.values():
        probability = count / total_chars
        if probability > 0:
            entropy -= probability * math.log2(probability)
            
    return entropy

def how_much_subdomains(url):
    domain = utils.extract_domain_with_subdomains(url)
    return domain.count('.')

def hyphen_in_domain(url):
    domain = utils.extract_domain_with_subdomains(url)
    return domain.count('-')

def url_depth(url):
    path = utils.extract_path_from_domain(url)
    return(path.count('/'))

def digit_ratio_domain(url):
    domain = utils.extract_domain_with_subdomains(url)
    ratio = sum(c.isdigit() for c in domain) / len(domain)
    return ratio

def any_file_extensions(url):
    with_extension = False
    with_suspicious_extension = False
    parsed_url = urlparse(url)
    path = parsed_url.path

    # add here more extensions
    # https://github.com/michalzobec/Security-Blocked-File-Extensions-Attachments/blob/main/list-of-blocked-file-extensions.txt
    suspicious_extensions = [
        "exe", "dll", "ocx", "ps1",
        "ps1xml", "ps2", "ps2xml",
        "msh", "msh1", "msh2", "mshxml",
        "msh1xml", "msh2xml", "js", "jse",
        "vbs", "vb", "vbe", "cmd",
        "bat", "hta", "inf", "reg",
        "scr", "cpl", "msc", "chm",
        "jar", "rar", "z", "bz2",
        "cab", "gz", "tar", "ppkg",
        "tmp", "ost", "pst", "iso",
        "doc", "dot", "xls", "xlt",
        "xlm", "xla", "ppt", "pot",
        "pps", "xlsb", "ppam", "py"
    ]

    suspicious_extensions_pattern = r"\.(" + "|".join(suspicious_extensions) + r")(?:$|/)"

    if path.endswith('.html'):
        with_extension = False
    elif re.search(suspicious_extensions_pattern, path, flags = re.IGNORECASE):
        with_suspicious_extension = True
        with_extension = True
    elif re.search(r"\.[^/]+(?:$|/)", path, flags = re.IGNORECASE):
        with_extension = True
    
    return with_extension, with_suspicious_extension

def extract_static_features(url):
    number_of_repeated_chars, max_repeated_chars = check_domain_repeated_chars(url)
    entropy_of_domain = domain_entropy(url)
    subdomains_number = how_much_subdomains(url)
    hyphen_number = hyphen_in_domain(url)
    path_number = url_depth(url)
    digit_ratio = digit_ratio_domain(url)
    contains_extension, contains_suspicious_extension = any_file_extensions(url)

    features = {
        'number_of_repeated_chars': number_of_repeated_chars,
        'max_repeated_chars': max_repeated_chars,
        'entropy_of_domain': entropy_of_domain,
        'subdomains_number': subdomains_number,
        'hyphen_number': hyphen_number,
        'path_number': path_number,
        'digit_ratio': digit_ratio,
        'contains_extension': contains_extension,
        'contains_suspicious_extension': contains_suspicious_extension
    }

    return features