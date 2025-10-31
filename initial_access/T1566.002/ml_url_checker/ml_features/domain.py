import whois
import tldextract
import json
import dns.resolver
import utils
import requests
from datetime import datetime, timezone

def get_whois_info(domain):
    any_info = False
    any_whois_info = False
    num_nameservers = 0
    days_from_create_to_expire = 0
    days_from_create_to_now = 0

    try:
        whois_json_info = whois.whois(domain)
        any_whois_info = True
        name_servers = whois_json_info.name_servers
        if name_servers:
            num_nameservers = len(name_servers)
        else:
            num_nameservers = 0

        # we need to handle 2 situations:
        # 1 expiration_date / creation_date like: "2020-10-10 ..."
        # 2 expiration_date / creation_date like: ["2020-10-10 ..", "2020-10-11 ..."]
        creation_date = whois_json_info.creation_date
        expiration_date = whois_json_info.expiration_date

        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        days_from_create_to_expire = utils.get_days_diff_from_time(creation_date, expiration_date)
        days_from_create_to_now = utils.get_days_diff_from_time(creation_date)
        any_info = True
    except whois.WhoisError:
        # no whois info, try to rdap request
        print("empty whois output")
        rdap_endpoint = utils.find_rdap_endpoint(domain)
        if not rdap_endpoint:
            return None
        try:
            response = requests.get(f"{rdap_endpoint}{domain}")
            response.raise_for_status()
            rdap_data = response.json()
            # array with nameservers
            nameservers = rdap_data["nameservers"]
            num_nameservers = len(nameservers)

            # events contains dates
            events = rdap_data["events"]
            for event in events:
                if "expiration" in event["eventAction"]:
                    try:
                        expire_date = datetime.strptime(event["eventDate"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    except ValueError:
                        expire_date = datetime.strptime(event["eventDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                elif "registration" in event["eventAction"]:
                    try:
                        register_date = datetime.strptime(event["eventDate"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    except ValueError:
                        register_date = datetime.strptime(event["eventDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


            days_from_create_to_expire = utils.get_days_diff_from_time(register_date, expire_date)
            days_from_create_to_now = utils.get_days_diff_from_time(register_date)

            any_info = True

        except requests.exceptions.RequestException as e:
            print(f"Error making RDAP request: {e}")

    return any_info, any_whois_info, num_nameservers, \
        days_from_create_to_expire, days_from_create_to_now

def extract_domain_records(domain):
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"]
    all_records = {}

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            records_for_type = []
            for rdata in answers:
                records_for_type.append(rdata.to_text())
            all_records[record_type] = records_for_type
        except dns.resolver.NoAnswer:
            all_records[record_type] = None
        except dns.resolver.NXDOMAIN:
            return None
        except Exception as e:
            all_records[record_type] = f"Error fetching {record_type} records: {e}"

    return all_records
    
def extract_domain_features(url):
    is_txt_empty = False

    domain = utils.extract_domain_without_subdomains(url)

    domain_records = extract_domain_records(domain)
    if not domain_records['TXT']:
        is_txt_empty = True

    any_info, any_whois_info, num_nameservers, \
        days_from_create_to_expire, days_from_create_to_now = get_whois_info(domain)
    
    if not any_info:
        print("handle no info")

    features = {
        'any_whois_info': any_whois_info,
        'num_nameservers': num_nameservers,
        'days_from_create_to_expire': days_from_create_to_expire,
        'days_from_create_to_now': days_from_create_to_now,
        'is_txt_empty': is_txt_empty,
    }

    return features
