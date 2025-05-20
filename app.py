from flask import Flask, request, jsonify
import os
import json
import requests

app = Flask(__name__)

VERIFY_TOKEN = "mysecret123"   # ये Facebook webhook verification token
PAGE_ACCESS_TOKEN = "EAAKIaXjho1IBO5Y7sfs2hJSrwQ4BNRGUFKQM96MyWSVZBZBdNOSK6K7tgQC92DLaqVM6K3MAHhHb27VDVLWXIPZApwCoXK4wBEqLKwufwTAegGvvgmLwZBCu2l5X4FlHAJNkA5aasqwfSeN4sv0J5hZAhQpNTZB8xdWLnY3iPZAResN9LBZAHP1ZAoxhi7N3wHbabhJZAEHS9AQFeJvBPlxQuUnKlaw84ZD"  # Facebook Page Access Token डालें यहाँ

LEAD_FILE = "leads.json"       # Leads save

def get_lead_details(leadgen_id):
    """Facebook Graph API से lead details fetch करें"""
    url = f"https://graph.facebook.com/v17.0/{leadgen_id}"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "field_data,created_time"  # ज़रूरी fields ले रहे हैं
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching lead details: {response.text}")
        return None

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        try:
            data = request.get_json()
            print("Received data:", json.dumps(data, indent=2))

            # पहले से existing leads पढ़ें या नया list बनाएं
            if os.path.exists(LEAD_FILE):
                with open(LEAD_FILE, "r") as f:
                    leads_list = json.load(f)
            else:
                leads_list = []

            # webhook payload में से leadgen events खोजें
            if data.get("object") == "page":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        if change.get("field") == "leadgen":
                            leadgen_id = change["value"].get("leadgen_id")
                            if leadgen_id:
                                # Graph API से lead detail लें
                                lead_details = get_lead_details(leadgen_id)
                                if lead_details:
                                    leads_list.append(lead_details)

            # updated leads को फाइल में save करें
            with open(LEAD_FILE, "w") as f:
                json.dump(leads_list, f, indent=2)

            return "Success", 200

        except Exception as e:
            print("Error processing lead:", str(e))
            return "Internal Server Error", 500

@app.route("/")
def home():
    return "Webhook is live!", 200

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
