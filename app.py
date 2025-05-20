from flask import Flask, request
import os
import json
import requests

app = Flask(__name__)

# Your Facebook tokens
VERIFY_TOKEN = "mysecret123"
PAGE_ACCESS_TOKEN = "EAAKIaXjho1IBOyVeZA1OYYM5dXdFgl0VErf1QAKCdyeCnqBDHnuXTJJQOcb9IOTwYvGTFWZBkC7psTD6YQvyUhEtVwYZBCDyBLZCYgNAb28S4WwwcAG5SjRoPdZAuvm8NXwHqjFY8DddvFvyvrpZAUyHRhS6GCmrlSOa95asjgMaOfNWXiCKF4X6VATBniGPJf4BQ7WXEzrKIH0eeECymIaqzwjgDYQegV"

# Get lead details using leadgen_id
def get_lead_details(leadgen_id):
    url = f"https://graph.facebook.com/v17.0/{leadgen_id}"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "field_data,created_time"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Error fetching lead details:")
        print(response.text)
        return None

# Webhook Endpoint
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Webhook verification failed.")
            return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("📩 Received webhook data:")
        print(json.dumps(data, indent=2))

        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "leadgen":
                        print("🔔 Leadgen event detected")
                        leadgen_id = change["value"].get("leadgen_id")
                        print(f"📌 Leadgen ID: {leadgen_id}")
                        if leadgen_id:
                            lead_details = get_lead_details(leadgen_id)
                            if lead_details:
                                print("✅ Lead Data Received:")
                                for field in lead_details.get("field_data", []):
                                    print(f"{field['name']}: {', '.join(field['values'])}")
                            else:
                                print("⚠️ No lead details found.")
        return "EVENT_RECEIVED", 200

@app.route("/")
def home():
    return "✅ Webhook is live!", 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
