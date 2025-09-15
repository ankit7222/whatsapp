from flask import Flask, request
import requests

app = Flask(__name__)

# 🔑 Replace with your values
VERIFY_TOKEN = "my_token_1234"  
ACCESS_TOKEN = "EAAgBl01FkkgBPWxppdS44BZAZAvIDPI3vAUhjBCfZCLlLIpQe2iUf07Wa9bVZABZBw7qZBgWF5uHoVsgeVuF4nUqe2IbY35dsVxEjU5ytUo4ZALaZCaBXoRXXp21HxxMB00Xj9mT730SgCcF2TPF1GGYBZBsN9QrC1SOeHoQMbcXBMOSwZAZBHG0R5goc3Esp9vNZBeNvx76FYSnHZCeiCU59Ppvn2RLpXQiVVlZCNBbSXZBySu0wZDZD"
PHONE_NUMBER_ID = "787135234489060"

# ✅ Verify webhook
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Error", 403

# ✅ Handle messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        print("📩 Received:", text)

        # Reply back
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        payload = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "type": "text",
            "text": {"body": f"🤖 You said: {text}"}
        }
        requests.post(url, headers=headers, json=payload)

    except Exception as e:
        print("⚠️ Error:", e)

    return "ok", 200
