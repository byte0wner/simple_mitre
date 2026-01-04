from tinydb import TinyDB, Query
import utils

db = TinyDB('db.json')


class Event:
    def __init__(self, json_event):
        self.workstation_name = json_event["workstation_name"]
        self.username = json_event["target_username"]
        self.logon_type = json_event["logon_type"]
        self.ip_addr = json_event["ip_addr"]

        self.date, self.time = utils.parse_time(json_event["creation_time"])
        self.weekday = utils.extract_weekday(self.date)

def fill_statistics(event):
    doc = db.all()
    if not doc:
        db.insert({})
        doc = db.all()

    main_doc = doc[0]

    if event.workstation_name not in main_doc:
        main_doc[event.workstation_name] = {}
        print(f"new workstation! : {event.workstation_name}")

    if event.username not in main_doc[event.workstation_name]:
        main_doc[event.workstation_name][event.username] = utils.statistics_template
        print(f"new user '{event.username}' in workstation '{event.workstation_name}'")

    main_doc[event.workstation_name][event.username]["total_logons"] += 1
    main_doc[event.workstation_name][event.username]["logon_types"][event.logon_type] += 1
    main_doc[event.workstation_name][event.username]["week_days"][event.weekday] += 1

    dates = main_doc[event.workstation_name][event.username].get("dates", [])
    if event.date not in dates:
        dates.append(event.date)
        main_doc[event.workstation_name][event.username]["dates"] = dates

    if event.ip_addr not in main_doc[event.workstation_name][event.username]["ip_addrs"]:
        main_doc[event.workstation_name][event.username]["ip_addrs"][event.ip_addr] = 1
        print(f"new ip '{event.ip_addr}' from '{event.username}' in workstation '{event.workstation_name}'")
    else:
        main_doc[event.workstation_name][event.username]["ip_addrs"][event.ip_addr] += 1

    # check for rare logon by type, day, and user

    if event.username in utils.sens_users_on_all_hosts:
        print(f"sensitive logon from '{event.username}' on '{event.workstation_name}'")

    rare_logon_type = utils.is_rare_logon(event.logon_type, main_doc[event.workstation_name][event.username]["logon_types"])
    if rare_logon_type:
        print(f"rare logon type '{event.logon_type}' from '{event.username}' on '{event.workstation_name}'")

    rare_logon_day = utils.is_rare_logon(event.weekday, main_doc[event.workstation_name][event.username]["week_days"])
    if rare_logon_day:
        print(f"rare logon day '{event.weekday}' from '{event.username}' on '{event.workstation_name}'")

    users_logons = {}
    for user in main_doc[event.workstation_name]:
        users_logons[user] = main_doc[event.workstation_name][user]["total_logons"]
    
    rare_logon_user = utils.is_rare_logon(event.username, users_logons)
    if rare_logon_user:
        print(f"rare logon user: '{event.username}' on '{event.workstation_name}'")

    db.update(lambda d: d.update(main_doc))
    print(db.all())