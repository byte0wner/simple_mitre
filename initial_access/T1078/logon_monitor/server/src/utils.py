import datetime

sens_users_on_all_hosts = [
    "Guest",
    "administrator_domena",
    "Administrator"
]

statistics_template = {
    "week_days": {
        "Mon": 0,
        "Tue": 0,
        "Wed": 0,
        "Thu": 0,
        "Fri": 0,
        "Sat": 0,
        "Sun": 0
    },
    "logon_types": {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
        "13": 0
    },
    "total_logons": 0,
    "dates": [],
    "ip_addrs": {}
}


# extract weekday from date like
# date = 2025-11-20 
# weekday = Tue
def extract_weekday(date_string):
    datetime_object = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    abbreviated_day_name = datetime_object.strftime("%a")
    return abbreviated_day_name

# get time and date from timestamp like
# 2025-11-20T02:46:07.0747283Z ->
# date = 2025-11-20
# time = 02:46:07
def parse_time(time_str):
    time_str = time_str.rstrip('Z')
    date_part, time_part = time_str.split('T')
    if '.' in time_part:
        main_time, _ = time_part.split('.', 1)
    else:
        main_time = time_part
    date_obj = datetime.date.fromisoformat(date_part)
    time_obj = datetime.time.fromisoformat(main_time)
    return date_obj.strftime("%Y-%m-%d"), time_obj.strftime("%H:%M:%S")

def is_rare_logon(field, logons_info):
    values = list(logons_info.values())
    total = 0
    for value in values:
        total += value

    srednee = total / len(values)
    return logons_info[field] < srednee