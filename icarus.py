from slackclient import SlackClient
from os import environ
from events import SlackEventAdapter

# Our app's Slack Event Adapter for receiving actions via the Events API
SLACK_VERIFICATION_TOKEN = environ["SLACK_VERIFICATION_TOKEN"]
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
SLACK_BOT_TOKEN = environ["SLACK_BOT_TOKEN"]
CLIENT = SlackClient(SLACK_BOT_TOKEN)

# For OAuth
client_id = environ["SLACK_CLIENT_ID"]
client_secret = environ["SLACK_CLIENT_SECRET"]

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        CLIENT.api_call("chat.postMessage", channel=channel, text=message)

@slack_events_adapter.on("user_change")
def handle_status_change(event_data):
    event = event_data["event"]
    user = event["user"]["name"]
    if ("icarus" in event["user"]["profile"]["status_text"].lower()) or ("icarus" in event["user"]["profile"]["status_emoji"].lower()):
        text = "%s is entering ICARUS time!" % user
        CLIENT.api_call("chat.postMessage", channel=environ["NOTIFICATION_CHANNEL"], text=text)

# Once we have our event listeners configured, we can start the Flask server with the
# default `/events` endpoint on port 3000
slack_events_adapter.start(port=environ["PORT"])
