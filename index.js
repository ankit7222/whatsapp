const express = require("express");
const bodyParser = require("body-parser");
const app = express();

const VERIFY_TOKEN = process.env.VERIFY_TOKEN;   // from Render env vars
const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN; // from Render env vars

app.use(bodyParser.json());

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

// ✅ Incoming messages
app.post("/webhook", (req, res) => {
  let body = req.body;
  console.log("Incoming message:", JSON.stringify(body, null, 2));
  res.sendStatus(200);
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));