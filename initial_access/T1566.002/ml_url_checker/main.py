import ml_features.domain as d_features
import ml_features.static as s_features
import ml_features.page as p_features
import utils
from preprocess import preprocess

import warnings
from urllib3.exceptions import InsecureRequestWarning

from tqdm import tqdm
import sys
import pandas as pd
import numpy as np
import tldextract
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from math import log2
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import whois
import xgboost as xgb
import re
import argparse

features = []

def prepare_dataset(in_file, out_file):
    print(f"[+] preparing {out_file} ...")
    df = pd.read_csv(in_file)
    for url in tqdm(df['url'], desc = "Extracting malicious features"):
        try:
            response = requests.head(url, verify =False, allow_redirects=True, timeout=5, headers=utils.custom_headers)
            extract_features(url)
        except requests.exceptions.ConnectionError as e:
            continue
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.RequestException as e:
            continue
        except TypeError:
            continue
        except whois.exceptions.WhoisDomainNotFoundError:
            continue

    df = pd.DataFrame(features)
    df.to_csv(out_file, index=False, encoding='utf-8')
    print(f"[+] done: {out_file} !")

def train_model():
    phish_df = pd.read_csv('datasets/output_malware.csv')
    legit_df = pd.read_csv('datasets/output_legit.csv')

    phish_df['label'] = 1
    legit_df['label'] = 0

    data = pd.concat([phish_df, legit_df], ignore_index = True)

    if 'url' in data.columns:
        data.drop('url', axis=1, inplace=True)

    bool_columns = data.select_dtypes(include=['bool']).columns
    data[bool_columns] = data[bool_columns].astype(int)

    data.dropna(inplace=True)

    data.drop_duplicates(inplace=True)

    X = data.drop('label', axis=1)
    y = data['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    scale_pos_weight = sum(y == 0) / sum(y == 1)

    model = xgb.XGBClassifier(
        objective='binary:logistic',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        eval_metric='auc',
        early_stopping_rounds=10,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=True
    )

    y_pred = model.predict(X_test)
    print(f"Пиздатость модели:{accuracy_score(y_test, y_pred)} (внатуре чоткая)")
    print(classification_report(y_test, y_pred))

    model.save_model(utils.model_filename)

def check_verdict(url):
    verdict, descriptions = preprocess(url)
    if verdict:
        print(descriptions)
        return
    try:
        model = xgb.XGBClassifier()
        model.load_model('phishing_model.json')
        response = requests.head(url, verify =False, allow_redirects=True, timeout=5, headers=utils.custom_headers)
        domain_features = d_features.extract_domain_features(url)
        static_features = s_features.extract_static_features(url)
        page_features = p_features.extract_page_features(url)
        all_features = {**domain_features, **static_features, **page_features}

        features_df = pd.DataFrame([all_features])
        bool_columns = features_df.select_dtypes(include=['bool']).columns
        features_df[bool_columns] = features_df[bool_columns].astype(int)
        features_df.dropna(inplace=True)

        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0, 1]
        result = {
            'url': url,
            'prediction': "phishing" if int(prediction) == 1 else "not phishing",
            'probability':  float(probability)
        }
        print(result)

    except requests.exceptions.ConnectionError as e:
        print("connection error")
        return
    except requests.exceptions.Timeout:
        print("timeout")
        return
    except requests.exceptions.RequestException as e:
        print("request exception")
        return
    except TypeError:
        print("type error")
        return
    except whois.exceptions.WhoisDomainNotFoundError:
        print("whois_domain_not_found")
        return

def extract_features(url):
    domain_features = d_features.extract_domain_features(url)
    static_features = s_features.extract_static_features(url)
    page_features = p_features.extract_page_features(url)
    all_features = {**domain_features, **static_features, **page_features}
    all_features['url'] = url
    features.append(all_features)

def main():
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)

    parser = argparse.ArgumentParser(description='url phishing checker')

    parser.add_argument('-train', action='store_true', help='train model on malicious/benign datasets with features')
    parser.add_argument('-batch', action='store_true', help='check batch of urls. specify targets in "target_urls_for_test" inside utils.py ')
    parser.add_argument('-extract', action='store_true', help='extract features from malicious/benign urls')
    parser.add_argument('-check', type=str, help='check url')

    args = parser.parse_args()

    options = [args.train, args.extract, args.check, args.batch]
    if sum(bool(option) for option in options) != 1:
        parser.error('you can use only one option: -train, -extract or -check <url>')

    if args.train:
        train_model()
    elif args.extract:
        prepare_dataset(utils.benign_urls_path, "output_legit.csv")
        prepare_dataset(utils.malicious_urls_path, "output_malware.csv")
    elif args.check:
        print(f"[+] checking url: {args.check}")
        check_verdict(args.check)
    elif args.batch:
        for url in utils.target_urls_for_test:
            check_verdict(url)

if __name__ == "__main__":
    main()
