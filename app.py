from flask import Flask, request
import os
import json

app = Flask(__name__)

VERIFY_TOKEN = "mysecret123"  # Use the same token as in your Facebook app webhook
LEAD_FILE = "leads.txt"

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

            with open(LEAD_FILE, "a") as f:
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        lead_info = change.get("value", {})
                        name = lead_info.get("full_name", "No Name")
                        phone = lead_info.get("phone_number", "No Number")

                        f.write(f"Name: {name}, Phone: {phone}\n")

            return "Success", 200

        except Exception as e:
            print("Error processing lead:", str(e))
            return "Internal Server Error", 500

# Optional root route to check if server is running
@app.route("/")
def home():
    return "Webhook is live!", 200

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
