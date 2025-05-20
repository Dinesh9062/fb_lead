from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

VERIFY_TOKEN = "mysecret123"  # Facebook webhook verify token
LEAD_FILE = "leads.json"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
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
            print("Received lead data:", json.dumps(data, indent=2))

            # Read existing leads from file or create new list
            if os.path.exists(LEAD_FILE):
                with open(LEAD_FILE, "r") as f:
                    leads_list = json.load(f)
            else:
                leads_list = []

            # Extract lead info and append to leads_list
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    lead_info = change.get("value", {})
                    leads_list.append(lead_info)

            # Save updated leads list back to file
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
