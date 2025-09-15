// index.js
const express = require("express");
const bodyParser = require("body-parser");
const axios = require("axios");
require("dotenv").config();

const app = express();
app.use(bodyParser.json());

// Read tokens from environment variables
const VERIFY_TOKEN = process.env.VERIFY_TOKEN;
const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;
const PHONE_NUMBER_ID = process.env.PHONE_NUMBER_ID;

// ✅ Webhook verification
app.get("/webhook", (req, res) => {
  const mode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];

  if (mode && token) {
    if (mode === "subscribe" && token === VERIFY_TOKEN) {
      console.log("WEBHOOK_VERIFIED");
      res.status(200).send(challenge);
    } else {
      res.sendStatus(403);
    }
  }
});

// ✅ Handle incoming messages
app.post("/webhook", async (req, res) => {
  const body = req.body;
  console.log("Incoming message:", JSON.stringify(body, null, 2));

  if (body.object) {
    body.entry.forEach(entry => {
      entry.changes.forEach(async change => {
        const message = change.value.messages?.[0];
        if (message) {
          const from = message.from; // sender's number
          const text = message.text?.body || "";

          console.log(`From: ${from}, Message: ${text}`);

          // Send a reply
          try {
            await axios.post(
              `https://graph.facebook.com/v20.0/${PHONE_NUMBER_ID}/messages`,
              {
                messaging_product: "whatsapp",
                to: from,
                text: { body: `You said: ${text}` },
              },
              {
                headers: {
                  Authorization: `Bearer ${WHATSAPP_TOKEN}`,
                  "Content-Type": "application/json",
                },
              }
            );
            console.log("Reply sent successfully");
          } catch (error) {
            console.error("Error sending reply:", error.response?.data || error.message);
          }
        }
      });
    });

    res.sendStatus(200);
  } else {
    res.sendStatus(404);
  }
});

// ✅ Use Render-assigned port
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
