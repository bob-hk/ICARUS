from slackclient import SlackClient
from os import environ
from pyee import EventEmitter
from slackeventsapi import SlackServer

class SlackEventAdapter(EventEmitter):
    # Initialize the Slack event server
    # If no endpoint is provided, default to listening on '/slack/events'
    def __init__(self, verification_token, endpoint="/slack/events"):
        EventEmitter.__init__(self)
        self.verification_token = verification_token
        self.server = SlackServer(verification_token, endpoint, self)

    def start(self, host='0.0.0.0', port=None, debug=False):
        self.server.run(host=host, port=port, debug=debug)

# Our app's Slack Event Adapter for receiving actions via the Events API
SLACK_VERIFICATION_TOKEN = environ["SLACK_VERIFICATION_TOKEN"]
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
SLACK_BOT_TOKEN = environ["SLACK_BOT_TOKEN"]
CLIENT = SlackClient(SLACK_BOT_TOKEN)

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        CLIENT.api_call("chat.postMessage", channel=channel, text=message)

# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    CLIENT.api_call("chat.postMessage", channel=channel, text=text)

@slack_events_adapter.on("user_change")
def handle_status_change(event_data):
    event = event_data["event"]
    user = event["user"]
    print(event)
    #if "icarus" in event["user"]["status_text"] or "icarus" in event["user"]["status_emoji"]:
    #    CLIENT.api_call("users.setPresence", user=user, presence=away)

# Once we have our event listeners configured, we can start the Flask server with the
# default `/events` endpoint on port 3000
slack_events_adapter.start(port=environ["PORT"])
