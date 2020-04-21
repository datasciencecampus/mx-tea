#!/usr/bin/env python
import requests
import json



""" Your Slack webhook """
slack_webhook = 'slack_webhook'

""" Question message """
slack_question_message = "Morning all, give this post a thumbs up if you are available for a tea break this afternoon!"


def ask_question(event, context):
	""" Asks the question to the Slack channel """
	headers = {'Content-type': 'application/json'}
	payload = {'text': slack_question_message}
	payload = json.dumps(payload)
	requests.post(slack_webhook, data=payload, headers=headers)

### post_message()


