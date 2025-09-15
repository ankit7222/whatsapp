from flask import Flask, request
import os
import requests

app = Flask(__name__)

# WhatsApp verification token
VERIFY_TOKEN = "my_secret_token_123"

# WhatsApp Cloud API credentials
WHATSAPP_TOKEN = "EAAgBl01FkkgBPTLsG5Olhwv29FlahNdKdQhA5RynDg0HSA4ytnQ1y6FVJqrrIo45Cizvj0cd7NoYNMuCIGcjPurWYQV14QUFoKwkttoMI6auzWRFTGZCIZBNk1EGf0ZBL5ZCuOEZCECBaDXqUssgpDUnTu5MDEpIeZCvcyQ2xZAvhwgcZAKU2IwSZCHCC5LfzZAwd6J6z8nVZA1WyL0mDgdoaktHtRvLRBcNMTZASvn6Ycj96wZDZD"
PHONE_NUMBER_ID = "787135234489060"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/787135234489060/messages"

# Multi-level menu with media support
MENU = {
    "main": {
        "text": "Welcome! Choose an option:",
        "buttons": [
            {"id": "services", "title": "Services"},
            {"id": "info", "title": "Info"}
        ]
    },
    "services": {
        "text": "Our services:",
        "buttons": [
            {"id": "service_1", "title": "Service 1"},
            {"id": "service_2", "title": "Service 2"},
            {"id": "back", "title": "Back"}
        ]
    },
    "service_1": {
        "text": "Service 1 details:\nVisit: https://example.com/service1",
        "buttons": [{"id": "back", "title": "Back"}],
        "media": None
    },
    "service_2": {
        "text": "Service 2 details:",
        "buttons": [{"id": "back", "title": "Back"}],
        "media": {
            "type": "image",
            "link": "https://www.example.com/sample-image.jpg",
            "caption": "Here is an image for Service 2"
        }
    },
    "info": {
        "text": "Information section:",
        "buttons": [
            {"id": "about", "title": "About Us"},
            {"id": "contact", "title": "Contact"},
            {"id": "back", "title": "Back"}
        ]
    },
    "about": {
        "text": "We are a company that specializes in amazing bots!",
        "buttons": [{"id": "back", "title": "Back"}]
    },
    "contact": {
        "text": "Contact us at: contact@example.com",
        "buttons": [{"id": "back", "title": "Back"}]
    }
}

# Track each user's current menu state
user_states = {}

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Forbidden", 403

    elif request.method == "POST":
        data = request.get_json()
        print("Incoming message:", data)

        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        value = change.get("value", {})
                        messages = value.get("messages")
                        if messages:
                            for msg in messages:
                                from_number = msg["from"]
                                current_state = user_states.get(from_number, "main")

                                # Handle button replies
                                if msg.get("type") == "interactive":
                                    interactive_type = msg["interactive"]["type"]
                                    if interactive_type == "button_reply":
                                        button_id = msg["interactive"]["button_reply"]["id"]
                                        if button_id == "back":
                                            user_states[from_number] = "main"
                                        else:
                                            user_states[from_number] = button_id
                                        send_menu(from_number, user_states[from_number])

                                # Handle normal text messages
                                elif msg.get("type") == "text":
                                    text_body = msg["text"]["body"].lower()
                                    if "hi" in text_body or "hello" in text_body:
                                        user_states[from_number] = "main"
                                        send_menu(from_number, "main")
                                    else:
                                        send_whatsapp_message(from_number, f"Echo: {text_body}")

        return "EVENT_RECEIVED", 200

def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("Sent text response:", response.json())

def send_menu(to, menu_key):
    menu = MENU.get(menu_key)
    if not menu:
        send_whatsapp_message(to, "Menu not found!")
        return

    # Send media first if exists
    if "media" in menu and menu["media"]:
        media = menu["media"]
        if media["type"] == "image":
            send_media_message(to, media["link"], media.get("caption", ""))

    # Send menu text with buttons
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    buttons_payload = [{"type": "reply", "reply": {"id": b["id"], "title": b["title"]}} for b in menu.get("buttons", [])]

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": menu["text"]},
            "action": {"buttons": buttons_payload}
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("Sent menu response:", response.json())

def send_media_message(to, media_link, caption=""):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": media_link, "caption": caption}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("Sent media response:", response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
