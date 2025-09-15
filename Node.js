const express = require("express");
const bodyParser = require("body-parser");
const app = express();
require("dotenv").config();

const VERIFY_TOKEN = process.env.VERIFY_TOKEN;

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

// ✅ Handling messages
app.post("/webhook", (req, res) => {
  let body = req.body;
  console.log("Incoming message:", JSON.stringify(body, null, 2));

  if (body.object) {
    if (
      body.entry &&
      body.entry[0].changes &&
      body.entry[0].changes[0].value.messages
    ) {
      let phone_number_id = body.entry[0].changes[0].value.metadata.phone_number_id;
      let from = body.entry[0].changes[0].value.messages[0].from;
      let msg_body = body.entry[0].changes[0].value.messages[0].text.body;

      console.log(`From: ${from}, Message: ${msg_body}`);
    }
    res.sendStatus(200);
  } else {
    res.sendStatus(404);
  }
});

// ✅ Use Render-assigned PORT
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));