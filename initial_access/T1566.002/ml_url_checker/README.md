Dumb ML phishing url checker 3000
(I don't know if this thing even works)

This thing is not finished yet and is still in development (probably)

# How to start this uberprogram:

idk

# Model:

xgboost

```
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
```

- saved model: `phishing_model.json`

# Datasets:

- datasets/legit_urls.csv: 5k benign urls (without features)
- datasets/mal_urls.csv: 5k malicious urls (without features)

- datasets/output_legit.csv: 3420 malicious urls (with features)
- datasets/output_malware.csv: 2882 malicious urls (with features)

# Features:
    - static_features:
        - number_of_repeated_chars
        - max_repeated_chars
        - entropy_of_domain
        - subdomains_number
        - hyphen_number
        - path_number
        - digit_ratio
        - contains_extension
        - contains_suspicious_extension
    - page_features:
        - ssl_error
        - iframe
        - no_hyperlink
        - internal_ratio
        - external_ratio
        - number_of_redirects
        - has_password
    - domain_features
        - any_whois_info
        - num_nameservers
        - days_from_create_to_expire
        - days_from_create_to_now
        - is_txt_empty

# About modules:

## preprocess: 

this module trying to set verdict without ML

## rdap_endpoints.json: 

if we dont get `whois` info we are trying to get info from `RDAP` request
just google it bro

# Links:

- mal_urls: https://www.phishtank.com/
- legit_urls: https://data.mendeley.com/
- url_shorteners: https://github.com/PeterDaveHello/url-shorteners/blob/master/list