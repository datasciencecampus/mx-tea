#!/usr/bin/env python
import requests
import random as rnd
import math
import json



""" Post your meeting links below """
meeting_links = \
	[
		'link_1',
		'link_2',
		'etc'
	]

""" Your Slack webhook """
slack_webhook = 'slack_webhook'

""" Your Slack token """
slack_token = 'slack_token'

""" Slack channel ID """
slack_channel_id = 'slack_channel_id'

""" Slack bot ID """
slack_bot_id = 'slack_bot_id'

""" Question message """
slack_question_message = "Morning all, give this post a thumbs up if you are available for a tea break this afternoon!"

""" Requested group size (note, the algorithm may use +1 if ir provides a better split of people """
group_size = 4



def get_posts():
	""" Gets posts from the channel by the bot and returns as JSON object """
	url = f"https://slack.com/api/channels.history?token={slack_token}&channel={slack_channel_id}&bot_id={slack_bot_id}"
	return requests.get(url).json()


def get_recent_question(posts):
	""" Gets the most recent question post from the channel by the bot """
	latest_poll = {}
	for post in posts['messages']:
		if post.get('text') == f"{slack_question_message}":
			latest_poll = post
			break
	return latest_poll


def get_attendees_ids(poll):
	""" Gets a list of attendees slack IDs """
	attendees_ids = []
	reactions = poll.get('reactions')
	for reaction in reactions:
		if reaction.get('name') == "+1":
			attendees_ids.append(reaction.get('users'))
	return attendees_ids[0]


def allocate(names):
	""" Allocates names to groups """
	rnd.shuffle(names)

	result = []

	# increase groupsize by one if the groups are more evenly split by doing so
	groupsize = group_size if abs(((len(names) / group_size) % 1) - 0.5) >= abs(((len(names) / (group_size + 1)) % 1) - 0.5) else group_size + 1

	# increase groupsize if we don't have enough meeting links
	groupsize = max(groupsize, math.ceil(len(names) / len(meeting_links)))

	while True:
		# Make sure no group has less than two people
		if len(names) > groupsize + 2:
			result.append(names[0:groupsize])
			names = names[groupsize:]
		else:
			result.append(names[0:])
			break

	return result


def present(groups, meeting_links):
	""" Create post for slack channel """
	msg = []
	msg.append("Good afternoon everyone, below are this afternoons tea break groups")
	num = 0
	for i, group in enumerate(groups):
		msg.append("--------------------------------------------------------------------------------")
		msg.append(f"Group {i + 1}: ")
		msg.append(meeting_links[num])
		msg.append("--------------------------------------------------------------------------------")
		for member in group:
			msg.append(f"<@{member}>")
		num = num + 1

	return '\n'.join(map(str, msg))


def post_to_slack(msg):
	""" Post groups to slack channel """
	headers = {'Content-type': 'application/json'}
	payload = {'text': msg}
	payload = json.dumps(payload)
	requests.post(slack_webhook, data=payload, headers=headers)


def process(event, context):
	""" Pipeline process required for Cloud Function """
	posts = get_posts()
	poll = get_recent_question(posts)
	attendees_ids = get_attendees_ids(poll)
	groups = allocate(attendees_ids)
	msg = present(groups, meeting_links)
	post_to_slack(msg)


##process()