import argparse
import openpyxl
import sys
import glob
import os
from pathlib import Path
from proknow import ProKnow
from tqdm import tqdm


########################################
# Command Line Arguments

# Define arguments
parser = argparse.ArgumentParser(description="Synchronize ProKnow renaming rules.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--url", required=True,
    help="the base URL to use when making request to the ProKnow API")
parser.add_argument("-c", "--credentials", required=True,
    help='path to ProKnow API credentials file')
parser.add_argument("file",
    help="path to Excel workbook containing desired renaming rules")

# Parse arguments
args = parser.parse_args()


########################################
# Logging

def beep(): sys.stdout.write("\a")

def print_blue(skk): print("\033[94m{}\033[00m".format(skk))

def print_cyan(skk): print("\033[96m{}\033[00m".format(skk))

def print_green(skk): print("\033[92m{}\033[00m".format(skk))

def print_magenta(skk): print("\033[95m{}\033[00m".format(skk))

def print_red(skk): print("\033[91m{}\033[00m".format(skk))

def print_yellow(skk): print("\033[93m{}\033[00m".format(skk))

def fail(skk, msg=None):
    print_red(skk)
    if msg:
        print_yellow(msg)
    beep()
    sys.exit(1)


########################################
# Utilities

def find_synonym_rule(items, value):
    for item in items:
        rule = item["rule"]
        if rule["value"] == value and rule["type"] == "synonyms":
            return item
    return None

def is_rule_equal(a, b):
    if a["type"] != b["type"]:
        return False
    elif a["value"] != b["value"]:
        return False
    elif len(a["criteria"]) != len(b["criteria"]):
        return False
    else:
        a["criteria"].sort()
        b["criteria"].sort()
        for index, value in enumerate(a["criteria"]):
            if b["criteria"][index] != value:
                return False
    return True

def confirm(question, default="yes"):
    valid = { "yes": True, "y": True, "ye": True, "no": False, "n": False }
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")



########################################
# ProKnow Client

pk = ProKnow(args.url, credentials_file=args.credentials)


########################################
# Parse Rules

print_magenta("Parsing Rules from Workbook...")

# Load workspaces workbook and get active sheet
wb = openpyxl.load_workbook(Path(args.file))
ws = wb.active

# Parse rules
lookup = {}
rules = {}
for column in ws.iter_cols(values_only=True):
    rule = None
    for index, value in enumerate(column):
        if type(value) is str and len(value) > 0:

            # Ensure all values are unique
            if value in lookup:
                fail("Failed to read rules in '{0}' workbook".format(Path(args.file)), (
                    "Found duplicate value '" + value + "'; already used by '" + lookup[value] + "'"
                ))

            # Create rule or add criteria
            if index == 0:
                if value in rules:
                    fail("Failed to read rules in '{0}' workbook".format(Path(args.file)), (
                        "Mutiple columns detected with desired structure name '" + value + "'"
                    ))
                else:
                    rules[value] = rule = {
                        "type": "synonyms",
                        "criteria": [],
                        "value": value
                    }
            elif value != rule["value"] and value not in rule["criteria"]:
                rule["criteria"].append(value)

    # Add unique values to lookup
    if rule != None:
        lookup[rule["value"]] = rule["value"]
        for value in rule["criteria"]:
            lookup[value] = rule["value"]


########################################
# Query Existing Rules

print_magenta("Querying Rules from ProKnow...")

# Query existing rules
_, items = pk.requestor.get('/renaming/rules')
desired_items = []
for rule in items:
    desired_items.append({
        "rule": {
            "id": rule["id"],
            "type": rule["type"],
            "criteria": rule["criteria"],
            "value": rule["value"]
        },
        "state": "unknown"
    })

# Determine new and updated rules
for value in rules:
    rule = rules[value]
    found = find_synonym_rule(desired_items, value)
    if found is None:
        desired_items.append({
            "rule": rule,
            "state": "created"
        })
    elif not is_rule_equal(rule, found["rule"]):
        found["rule"]["criteria"] = rule["criteria"]
        found["state"] = "updated"
    else:
        found["state"] = "unchanged"


########################################
# Determine Desired Rules

print_magenta("Synchronizing Renaming Rules...")

# Construct body and identify state of rules
body = []
created = 0
updated = 0
unknown = []
for item in desired_items:
    body.append(item["rule"])
    if item["state"] == "created":
        created += 1
    elif item["state"] == "updated":
        updated += 1
    elif item["state"] == "unknown":
        unknown.append(item["rule"])

# Confirm creation and updating of rules
if created > 0 or updated > 0:
    print_yellow(" Rules have changed ({0} created, {1} updated)".format(created, updated))
    if not confirm("Are you sure you wish to synchronize renaming rules?"):
        fail("Synchronization aborted")
    _, res = pk.requestor.put('/renaming/rules', json=body)
    print_green(" Renaming rules successfully synchronized")
else:
    print_green(" All rules exist and are up to date")


########################################
# Reporting

if len(unknown) > 0:
    print_magenta("Identifying Unknown Renaming Rules...")
    if len(unknown) > 0:
        print_yellow(" Found {0} renaming rule(s) not defined in workbook:".format(len(unknown)))
        for item in unknown:
            print("  rename to '{0}' ({1})".format(item["value"], item["type"]))
