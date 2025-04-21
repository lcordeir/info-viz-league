import json
import os

def load_data():
    path = os.path.join("data", "match_data.json")
    with open(path, "r") as f:
        return json.load(f)

def filter_data(data, time_range, teams):
    start, end = time_range
    return [
        event for event in data
        if start <= event["timestamp"] <= end and event["team"] in teams
    ]

