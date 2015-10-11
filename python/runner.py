#!/usr/bin/env python3

import argparse
import json
import gamificationengine
import redminereader

# Read configuration
parser = argparse.ArgumentParser(description='Gamification tool exporting Redmine rewards into JSON')
parser.add_argument('--url', help='URL of the redmine instance', required=True)
parser.add_argument('--user', help='User for authentication', required=True)
parser.add_argument('--password', help='Password for authentication', required=True)
parser.add_argument('--project', help='Project to be analyzed, can be determined, normally lowercase', required=True)
parser.add_argument('--days', help='How many days to analyze, 14 would be the last two weeks', type=int, default=14)
parser.add_argument('file', help="JSON file location")
args = parser.parse_args()

# Load data from redmine
reader = redminereader.RedmineReader(
    url=args.url,
    user=args.user,
    password=args.password,
    project_name=args.project,
    verify=False)

# Read redmine
entry_meta, watched_issues, user_names = reader.analyze_time_entries(days_backwards=args.days)
issue_meta = reader.analyze_issues(entry_meta, watched_issues)

# Assign points
engine = gamificationengine.GamificationEngine()
points = engine.calculate_points(entry_meta, issue_meta)

# Prepare JSON
output = {
    "user_names": user_names,
    "points": points
}

# Write result to JSON file
file_name = args.file
with open(file_name, "w") as file:
    json.dump(output, file, sort_keys=True)

