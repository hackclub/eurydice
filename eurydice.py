from dataclasses import dataclass
from os import environ
import random
import re
from textwrap import dedent
from typing import List, Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=environ["SLACK_XOXB_TOKEN"])


@dataclass
class Button:
    text: str
    action_id: str
    style: Optional[str] = None


@dataclass
class Blocks:
    text: str
    buttons: List[Button]
    user_id: str

    def render(self):
        text_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": self.text},
        }

        if self.buttons:
            return [
                text_section,
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": button.text},
                            "action_id": button.action_id,
                            "style": button.style,
                        }
                        if button.style
                        else {
                            "type": "button",
                            "text": {"type": "plain_text", "text": button.text},
                            "action_id": button.action_id,
                        }
                        for button in self.buttons
                    ],
                    "block_id": self.user_id,
                },
            ]
        else:
            return [text_section]


def random_response():
    bodies = [
        "exactly",
        "fascinating",
        "good point",
        "hi",
        "hmmm",
        "i agree",
        "i believe in you",
        "lmao",
        "okay",
        "ooh",
        "rawr",
        "so true",
        "sure sure",
        "wonderful",
        "_considers what you've said_",
        "_prances around_",
        "hey is that a snake",
        "i'm a simple chatbot incapable of thought or emotion",
    ]
    suffixes = [
        "!",
        "!!",
        "..",
        " :3",
        " :D",
        " :0",
        " :P",
        " :>",
        " :tw_sparkles:",
        " :tw_sparkling_heart:",
        " :tw_relieved:",
        " :tw_sunglasses:",
        " :orpheus:",
        " :orpheus-pop:",
        " :aww:",
        " :blob_hype:",
        " :hyperbongocat:",
        " :thincc:",
        " :ultrafastparrot:",
    ]

    return random.choice(bodies) + random.choice(suffixes)


@app.message(re.compile(".*"))
def on_message(ack, payload, client):
    ack()

    client.chat_postMessage(
        channel=payload["user"],
        text=random_response(),
        thread_ts=payload["ts"],
    )


@app.event("app_mention")
def on_mention(payload, client):
    client.chat_postMessage(
        channel=payload["channel"],
        text=random_response(),
        thread_ts=payload["ts"],
    )


@app.command("/eurydice-restart")
def welcome(ack, payload, client):
    ack()

    blocks = Blocks(
        text=dedent(
            """
            hi!! hello welcome greetings

            i am here to show you around <...> and <...>

            when you're ready, press here to continue:"""
        ),
        buttons=[
            Button(
                text="continue",
                action_id="welcome_finished",
            ),
        ],
        user_id=payload["user_id"],
    )

    client.chat_postMessage(channel=payload["user_id"], blocks=blocks.render())


@app.action("welcome_finished")
def code_of_conduct(ack, payload, client):
    ack()

    blocks = Blocks(
        text="<code of conduct text>",
        buttons=[
            Button(
                text="i can do that!",
                action_id="coc_agree",
                style="primary",
            ),
            Button(
                text="i can't do that :V",
                action_id="coc_disagree",
            ),
        ],
        user_id=payload["block_id"],
    )

    client.chat_postMessage(
        channel=payload["block_id"],
        blocks=blocks.render(),
    )


@app.action("coc_disagree")
def coc_disagree(ack, payload, client):
    ack()

    blocks = Blocks(
        text=dedent(
            """
            -_-

            that's okay. it also means i can't in good conscience let you in. <filler text>"""
        ),
        buttons=[
            Button(
                text="nvm maybe i can",
                action_id="coc_reluctantly_agree",
            ),
        ],
        user_id=payload["block_id"],
    )

    client.chat_postMessage(
        channel=payload["block_id"],
        blocks=blocks.render(),
    )


@app.action("coc_agree")
def coc_agree(ack, payload, client):
    ack()

    blocks = Blocks(
        text="wonderful :tw_relieved:",
        buttons=[],
        user_id=payload["block_id"],
    )

    client.chat_postMessage(
        channel=payload["block_id"],
        blocks=blocks.render(),
    )

    encourage_make_profile(payload["block_id"], client)


@app.action("coc_reluctantly_agree")
def coc_reluctantly_agree(ack, payload, client):
    ack()

    blocks = Blocks(
        text="thought so :3",
        buttons=[],
        user_id=payload["block_id"],
    )

    client.chat_postMessage(
        channel=payload["block_id"],
        blocks=blocks.render(),
    )

    encourage_make_profile(payload["block_id"], client)


def encourage_make_profile(user_id, client):
    blocks = Blocks(
        text="<encourage make profile text>",
        buttons=[
            Button(
                text="i've done it",
                action_id="profile_finished",
            )
        ],
        user_id=user_id,
    )

    client.chat_postMessage(
        channel=user_id,
        blocks=blocks.render(),
    )


@app.action("profile_finished")
def recommend_channels(ack, payload, client):
    ack()

    blocks = Blocks(
        text="<recommend channels text>",
        buttons=[
            Button(
                text="<button text>",
                action_id="channel_rec_finished",
            ),
        ],
        user_id=payload["block_id"],
    )

    client.chat_postMessage(
        channel=payload["block_id"],
        blocks=blocks.render(),
    )


@app.action("channel_rec_finished")
def collect_feedback(ack, payload, client):
    ack()

    blocks = Blocks(
        text=dedent(
            """
        <collect feedback text>

        :ultrafastparrot: - <good feedback text>
        :thincc: - i'm feeling a bit confused or intimidated
        :fucking_sobbing: - i still feel really lost
        """
        ),
        buttons=[
            Button(
                text=":ultrafastparrot:",
                action_id="feedback_good",
            ),
            Button(
                text=":thincc:",
                action_id="feedback_not_good",
            ),
            Button(
                text=":fucking_sobbing:",
                action_id="feedback_horrible",
            ),
        ],
        user_id=payload["block_id"],
    )

    client.chat_postMessage(
        channel=payload["block_id"],
        blocks=blocks.render(),
    )


SocketModeHandler(app, environ["SLACK_XAPP_TOKEN"]).start()
