import json
import os
import time
import boto3
from botocore.exceptions import ClientError

BASE_JSON = "sample_data.json"
USE_AWS = os.getenv("USE_AWS", "false").lower() == "true"

# ----- Local in-memory / JSON helpers -----
def read_local():
    try:
        with open(BASE_JSON, "r") as f:
            return json.load(f)
    except Exception:
        return []

def write_local(data):
    try:
        with open(BASE_JSON, "w") as f:
            json.dump(data, f, indent=2)
            return True
    except Exception as e:
        print("Write Local Error:", e)
        return False

# ----- DynamoDB helpers -----
def get_dynamo_table(name="ReliefGridResources"):
    ddb = boto3.resource("dynamodb")
    return ddb.Table(name)

# ----- Core functions -----
def get_resources():
    if USE_AWS:
        try:
            table = get_dynamo_table()
            resp = table.scan()
            items = resp.get("Items", [])
            # convert timestamps to int if needed
            return items
        except Exception as e:
            print("Dynamo read error:", e)
            return []
    else:
        return read_local()

def save_resource(item):
    if USE_AWS:
        try:
            table = get_dynamo_table()
            table.put_item(Item=item)
            return True
        except Exception as e:
            print("Dynamo save error:", e)
            return False
    else:
        data = read_local()
        data.append(item)
        return write_local(data)

def get_resource_by_id(resource_id):
    if USE_AWS:
        try:
            table = get_dynamo_table()
            resp = table.get_item(Key={"id": resource_id})
            return resp.get("Item")
        except Exception as e:
            print("Dynamo get error:", e)
            return None
    else:
        data = read_local()
        for it in data:
            if str(it.get("id")) == str(resource_id):
                return it
        return None

# Simple exchanges log (local)
EXCHANGES_FILE = "exchanges_log.json"
def record_exchange(payload):
    try:
        logs = []
        if os.path.exists(EXCHANGES_FILE):
            with open(EXCHANGES_FILE, "r") as f:
                logs = json.load(f)
        payload["timestamp"] = int(time.time())
        logs.append(payload)
        with open(EXCHANGES_FILE, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print("Record exchange error:", e)

# Alerts simple store (local)
ALERTS_FILE = "alerts.json"
def get_alerts():
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "r") as f:
                return json.load(f)
        else:
            return []
    except:
        return []

def resolve_alert(alert_id):
    try:
        alerts = get_alerts()
        alerts = [a for a in alerts if a.get("id") != alert_id]
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    except Exception as e:
        print("Resolve alert error:", e)

# Stats (simple)
def get_stats():
    try:
        # This can be expanded to query DynamoDB for counts
        exchanges = []
        if os.path.exists(EXCHANGES_FILE):
            with open(EXCHANGES_FILE, "r") as f:
                exchanges = json.load(f)
        return {
            "exchanges_completed": len(exchanges),
            "active_alerts": len(get_alerts())
        }
    except:
        return {"exchanges_completed": 0, "active_alerts": 0}

# ----- SNS notifications (mock + real) -----
def send_sns_notification(message, subject=None):
    if USE_AWS:
        try:
            sns_arn = os.getenv("SNS_TOPIC_ARN")
            if not sns_arn:
                print("SNS_TOPIC_ARN not set. Skipping.")
                return False
            client = boto3.client("sns")
            kwargs = {"TopicArn": sns_arn, "Message": message}
            if subject:
                kwargs["Subject"] = subject
            client.publish(**kwargs)
            return True
        except ClientError as e:
            print("SNS publish error:", e)
            return False
    else:
        # mock — print to console and append to alerts.json
        print("[SNS MOCK] ", message)
        try:
            alerts = get_alerts()
            alert = {
                "id": str(int(time.time() * 1000)),
                "title": "Mock Notification",
                "message": message,
                "timestamp": int(time.time())
            }
            alerts.append(alert)
            with open(ALERTS_FILE, "w") as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            print("Error writing mock alert:", e)
        return True
