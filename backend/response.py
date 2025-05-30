from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')


# Predefined responses and NLP setup
responses = {
    "✅ System is online and functioning properly.": ["status", "are you online", "is the system working", "system health", "check system status"],
    "🕒 Uptime: 2 hours 37 minutes.": ["uptime", "how long have you been running", "when did you start", "how long have you been active"],
    "🛠️ Here are some useful tools to control your IoT device...": ["tools", "control my device", "platforms", "iot tools", "suggest some tools", "device control options"],

    "🤖 Need a hand? You can ask me things like...\n\n• help/sms – How to set up and test SMS alerts\n• help/email – How to set up email notifications\n•  help/datastream – How to stream and monitor sensor data\n• help/event – How event-based actions work\n• help/beam – Beem Africa API setup guide\n• help/firmware – Supported firmware and libraries\n\nTry typing any of these help commands to get specific guidance.": [
    "help", "what can you do", "i need help", "commands list", "how to use this chatbot",  "assist me with commands"
    ]
    ,

    "📩 SMS Setup Help:\n\nSMS alerts allow your IoT device to notify you via SMS through the chatbot, which uses the Beem Africa SMS gateway (https://login.beem.africa/#!/register?utm_source=website&utm_medium=web&utm_campaign=none).\n\nTo set up SMS alerts:\n• Create an account on Beem Africa: https://login.beem.africa/#!/register?utm_source=website&utm_medium=web&utm_campaign=none\n• Generate your API Key and API Secret.\n• In the chatbot, type `set sms` to enter your credentials, or type `help sms` for setup assistance.\n\nTo configure and test SMS:\n1. `set sms` --> Begin SMS setup\n2. `phone number: +2557xxxxxxx` --> Save your phone number\n3. `api key` --> Set your beam africa api key.\n 4. `secret key` --> add your api secret key\n 5. `sender name` --> add the sender name if configured but you can left by default use INFO   \n6.  `test sms` --> Send a test alert message\n\nMake sure your device is online and the API key is valid. These steps will also guide you once you start.": [
    "help/sms", "sms help","how to configure sms", "set up sms","sms configuration"
    ],

    "📧 Email Setup Help:\n\nTo configure sender email for alerts:\n1. set email → Start setup\n2. email: example@gmail.com → Enter sender email\n3. smtp: smtp.gmail.com → Set SMTP server\n4. port: 587 → Enter port (587 for TLS)\n5. password: your_app_password → Use your app password\n6. Then configure receiver email\nEnter receiver_email: receiver@gmail.com  \n\nYou can test it using:\ntest email → Sends a test email to the configured address.\n\nNote: It very important to  add sender (email that will be used for sending alert ) and recipient emails(email to receive alerts) here inorder to get alert and info through emails .": ["help/email", "email help", "how to configure email", "set up email", "email configuration", "how to use email", "email setup guide"],

    "📡 <b>Event/Trigger Setup Help:</b>\n\nEvents (also known as triggers) allow your device to automatically notify you when specific conditions are met. The chatbot can send alerts via SMS, email, or both.\n\n📍 Example use case:\nIf the temperature exceeds 30°C, the chatbot sends you a warning.\n\n⚙️ Configuration format:\n`event: name=temp_high,timer=3600, parameter=temperature, virtualPin=V1, condition=>30, alert=sms/email/both, message=Your alert message `\n\n🔸 name – A label for the event (no spaces)\n🔸 parameter – Data to monitor (e.g., temperature, humidity)\n🔸 virtualPin – The data source (e.g., V1)\n🔸 condition – When to trigger (e.g., >30, <=50)\n🔸 alert – Type of alert: `sms`, `email`, or `both`\n🔸 message – The message to send\n\n🔸 Timer – Set the time to sent alert \n\n✅ Make sure your virtual pin is active and your alert settings are configured correctly (use <code>set </code> <code>sms</code> and <code>set</code>  <code>email</code>).\n\n🗂 To list all events:\n`list events`\nDisplays all configured events.\n\n🗑 To delete an event:\n`delete event name=event_name`\nReplace `event_name` with the actual event name you want to remove.": ["help/event","event help","how to configure event","trigger help","trigger setup","event setup guide"],



    """
    📨 Beem Africa API Setup Help:<br><br>
    Beem Africa is the SMS gateway used by this chatbot to send real-time notifications directly to your phone. Follow these steps to configure it:<br><br>
    🔐 1. Create an Account<br>
    • Go to <a href="https://login.beem.africa/#!/register?utm_source=website&utm_medium=web&utm_campaign=none" target="_blank">Beem Africa Signup</a><br><br>
    🗝️ 2. Generate API Credentials<br>
    • After logging in, navigate to API Settings → Generate your API Key and API Secret.<br><br>
    🏷️ 3. Sender ID Setup<br>
    • Use the default sender ID provided by Beem<br>
    • OR apply for a custom sender ID under Messaging → Sender IDs (approval takes a few days)<br><br>
    💳 4. Purchase SMS Credits<br>
    • Go to Billing → Buy SMS → Choose package → Pay online<br><br>
    💸 5. SMS Pricing<br>
    • SMS to Tanzania typically costs ~33 TZS per message (may vary by volume & destination)<br>
    • You can view live rates in your Beem dashboard<br><br>
    🔧 6. How It Works in the Chatbot<br>
    • Type <code>set sms</code> to input your API key, secret, and phone number<br>
    • The chatbot will use Beem API to send alerts via SMS<br><br>
    📘 7. Official API Documentation<br>
    • View full API docs here: <a href="https://developer.beem.africa" target="_blank">https://developer.beem.africa</a><br><br>
    ⚠️ Make sure your API key and secret are correct and your account has enough credits. Test using <code>test sms</code> once setup is complete.
    """: [ "help/beam",  "beam africa",  "what is beam","beam sms", "beam api help", "beam configuration", "beam gateway" ],


    "❌ Invalid servo command. Use: servo <angle>": ["servo", "move servo", "rotate servo", "servo command"],
    "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands.": ["unknown", "i don't understand", "invalid command", "what did you say", "unknown command"],
    "👋 Hello! How can I assist you today?": ["hi", "hello", "hey", "hi there", "hello bot", "hey bot", "greetings"],
    "Okay, I’m here to help. What can I do for you?": ["okay", "all right", "fine", "understood"],
    "🤔 Would you like me to assist you with basic commands or guide you through how to use this system?": ["can you assist", "how to use this chatbot", "basic commands help", "need help with usage"],
    "🕰️ You can set a time schedule for your device to be active. For example, 'Activate at 7:00 AM' or 'Deactivate at 10:00 PM.'": ["time schedule", "create time schedule", "set device schedule", "schedule activation", "schedule deactivation"],
    "🔧 Servo Command Help:\nUse the format: servo <angle>\n\nExamples:\nservo 0 – Reset position\nservo 90 – Centered view\nservo 180 – Full right\n\nCommon angles:\nservo 45 – Left scan\nservo 135 – Right scan": ["help/servo", "servo help", "servo usage", "servo guide", "servo control instructions"],
    "Hey there! 👋 I'm your Smartfy IoT Chatbot, here to help you interact with your smart system easily 🧠💡\n\nHere are some basic commands you can try:\n\n🔧 To rotate the servo motor to a specific angle (between 0° and 180°):\nType: servo 90 – This moves the servo to 90 degrees 🔄\nType: servo 0 – This resets it to 0 degrees 🔁\nType: servo 180 – This turns it fully to 180 degrees ↩️\n\n🦾 Use different angles to perform different object detection tasks:\nservo 45 – Great for scanning left 👈\nservo 90 – Center view 🎯\nservo 135 – Scan right 👉\n\n🌡️ To check environmental readings:\nType: temp – Check current temperature 🌞\nType: humid – Check humidity level 💧\nType: rain – Check for rain detection 🌧️\nType: smoke – Check for smoke levels 🚬\n\n📢 Alerts and Notifications:\nType: alert sms – Get critical alerts via SMS 📲\nType: alert email – Receive alerts through email 📧\nType: alert status – Check which alert system is currently active ⚠️\n\n📦 More features coming soon! If you're not sure what to do, just ask for help at any time 😄\n\nReady when you are! 💬✨"
    : [
        "about", "who are you", "what is smartfy", "about the bot", "what this system is all about", "I don't know how to use this chatbot, can I get assistance on basic commands on how to use it?"
    ],
    "📅 Schedule Help:\nYou can set schedules like:\n- Activate at 7:00 AM\n- Deactivate at 10:00 PM\n\nMore advanced scheduling features coming soon!": ["help/schedule", "schedule help", "usage of schedule", "how to create schedule", "time schedule guide"],

    "Hello there!  Welcome to Smartfy IoT Chatbot . Here’s a quick guide on how to set up your chatbot 🛠️.\n\nThere are three phases in the device setup . Please select one by one to complete your device configuration :\n\n📌 You can begin by typing one of the following commands: [\"quick setup\", \"alert config\", \"datastream config\"\n\n🚀 1. Quick Setup:\n- Provide your device name 📱 and receiver email 📧.\n- This helps the chatbot identify and communicate with your device.\n\n📡 2. Alert Setup:\n- Uses default SMS configuration via Beam Africa API 📲 (charges may apply 💵).\n- You can customize your SMS settings and use your own sender email ✉️.\n\n📊 3. Datastream Configuration:\n- Define how data flows between your device and the chatbot 🔄.\n- For example:\n  🌡️ Temperature → v1\n  💧 Humidity → v2\n  📈 ...and so on\n\n🔐 After finishing configuration, the chatbot will generate:\n- Your User ID 🆔\n- An Authentication Token 🛡️\n\n📎 You’ll also receive a GitHub link 🔗 to download the library and get started coding 💻.\n\nLet’s build something smart! 💡": [
    "start", "device configuration", "device config", "config", "how to start", "how to create schedule", "time schedule guide"
  ],
    "📊 Datastream Configuration Guide\n\nHello there! Let's configure your Datastreams for your device. Datastreams define the data your IoT device will send or receive, such as temperature, humidity, or other sensor data.\n\n🚀 Example Command:\n`datastream: parameter=temperature, type=float, virtualPin=V1`\n\n🔧 Parameters Explained:\n- parameter: The name of your data (e.g., temperature, humidity).\n- type: Data type (e.g., float, int, string).\n- virtualPin: Virtual pin or identifier used by your platform (e.g., V1, V2).\n\n💡 You can add multiple datastreams by sending the command again with different parameters.\n\n✅ Once all datastreams are added, type `start device` to complete your setup.\n\n📎 Example Commands:\n- `datastream: parameter=humidity, type=float, virtualPin=V2`\n- `datastream: parameter=motion, type=bool, virtualPin=V3`\n\n🧹 Managing Datastreams:\n- To review and wipe existing datastreams, type `datastream wipe`.\n- You will see a list of your current datastreams.\n- Then you can:\n  • Type `wipe all` to delete all datastreams.\n  • Type `wipe parameter_name` to delete a specific one (e.g., `wipe temperature`).\n\nLet's make your device smart, connected, and easy to manage! 🤖✨"
    :[
        "datastream", "help datastream", "what is datastream", "datastream config"
    ]

    


}


phrase_embeddings = []
reply_keys = []
for reply, phrases in responses.items():
    for phrase in phrases:
        phrase_embeddings.append(model.encode(phrase))
        reply_keys.append(reply)
phrase_embeddings = np.array(phrase_embeddings)