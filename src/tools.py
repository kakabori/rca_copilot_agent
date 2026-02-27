# tools.py
import json
import os

def get_recent_timeseries(asset_id):
    # ダミー
    return {
        "vibration": "spike after 13:00",
        "pressure": "gradual increase"
    }

def get_maintenance_history(asset_id):
    try:
        with open("data/maintenance.json") as f:
            return json.load(f)
    except:
        return []

def search_documents(query):
    docs = []
    doc_path = "data/documents"
    for fname in os.listdir(doc_path):
        with open(os.path.join(doc_path, fname)) as f:
            if query.split()[0].lower() in f.read().lower():
                docs.append(fname)
    return docs