from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = "mysecret123"  # Use same token on Facebook Webhook setup

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
        data = request.json
        print("Received lead data: ", data)

        # Example: Send lead to Odoo (update below URL and token)
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                lead_info = change.get("value", {})
                name = lead_info.get("full_name", "No Name")
                phone = lead_info.get("phone_number", "No Number")

                # Send to Odoo (update this part as per your Odoo setup)
                odoo_url = "https://your-odoo-domain.com/jsonrpc"
                headers = {"Content-Type": "application/json"}

                payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [
                            "your-db-name",  # database
                            1,               # user ID
                            "your-password", # password
                            "crm.lead",      # model
                            "create",        # method
                            [{
                                "name": name,
                                "contact_name": name,
                                "phone": phone,
                                "description": "Lead from Facebook",
                            }]
                        ]
                    },
                    "id": 1
                }

                requests.post(odoo_url, json=payload, headers=headers)

        return "Success", 200
