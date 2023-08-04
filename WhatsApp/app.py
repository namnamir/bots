from sentences import sentences
from triggers import triggers
from gifs import gif_error1
from gifs import gif_error2
from api import keys

from flask import Flask, request, render_template
from wit import Wit
import requests
import json
import random
import datetime
import time


app = Flask(__name__)

execution_time = {}

# Initialize the Wit.ai API client with your access token
client = Wit(keys['wit_api'])

def send_msg(response_type, response_body, to_number):
    headers = {
        'Authorization': f'Bearer {keys["meta_api"]}',
    }

    response = {
        'messaging_product': 'whatsapp',
        'to': to_number,
    }

    if response_type == 'text':
        response['type'] = 'text'
        response['text'] = {
            'preview_url': True,
            'body': response_body
        }
    elif response_type == 'image_url':
        response['type'] = 'image'
        response['image'] = {
            'link': response_body,  # url
            # 'mime_type': response_body[1],  # image/png, image/jpeg
        }
    elif response_type == 'image_id':
        response['type'] = 'image'
        response['image'] = {
            'id': response_body  # id
        }
    elif response_type == 'video':
        response['type'] = 'video'
        response['video'] = {
            'link': response_body,  # url
        }
    elif response_type == 'location':
        response['type'] = 'location'
        response['location'] = {
            'longitude': response_body[0],
            'latitude': response_body[1],
            'name': response_body[2],
            'address': response_body[3]
        }
    elif response_type == 'reaction':
        response['type'] = 'reaction'
        response['reaction'] = {
            'message_id': response_body,  # id; i.e., wamid.HBgLMzE2O...xRAA=
            'emoji': response_body  # emoji; i.e., \uD83D\uDE00
        }
    elif response_type == 'reply_text':
        response['type'] = 'text'
        response['text'] = {
            'preview_url': True,
            'body': response_body
        }
        response['context'] = {
            'message_id': response_body  # id; i.e., wamid.HBgLMzE2O...xRAA=
        }
    elif response_type == 'reply_image':
        response['type'] = 'image'
        response['image'] = {
            'link': response_body
        }
        response['context'] = {
            'message_id': response_body  # id; i.e., wamid.HBgLMzE2O...xRAA=
        }

    response = requests.post(keys['meta_api_url'], headers=headers, json=response)


class Bot:
    def __init__(self) -> None:
        pass

    def gif(term):
        lmt = 1
        ckey = "wa_bot"

        try:
            # our test search
            search_term = term.split(' ')[1].strip()

            # get the top 8 GIFs for the search term
            r = requests.get(
                f"https://tenor.googleapis.com/v2/search?q={search_term}\
                    &key={keys['tenro_api']}&client_key={ckey}&limit={lmt}"
            )

            if r.status_code == 200:
                # load the GIFs using the urls for the smaller GIF sizes
                try:
                    return json.loads(r.content)['results'][0]['media_formats']['tinymp4']['url']
                except KeyError:
                    return random.choice(gif_error1)
        except Exception as e:
            return random.choice(gif_error2)

    def qoute(contact_name):
        return random.choice(sentences).format(contact_name)

    def set_timer(term, message_to):
        global execution_time
        # if it is defined what to send
        if len(term.split(' ')) >= 4:
            time = term.split(' ')[1].strip().split(':')
            if len(time) != 3:
                send_msg(
                    'text',
                    'The time is not written correctly. Write command like \
                    "--timer [time] [name] [order]; like --timer 13:10:10 timer1 --love"',
                    message_to
                )
            timer_name = term.split(' ')[2]
            response_type = term.split(' ')[3]
        else:
            send_msg(
                'text',
                'write command like "--timer [time] [name] [order]; like --timer 13:10:10 timer1 --love"',
                message_to
            )
        # set the desired execution time as a time object
        timer = [
            timer_name,
            response_type,
            datetime.time(hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
        ]
        if message_to not in execution_time:
            execution_time[message_to] = []
        execution_time[message_to].append(timer)

        Bot.run_timer()
        return f'timer is set {timer}'

    def delete_timer():
        pass

    def show_timer():
        pass

    def run_timer():
        global execution_time
        # loop forever
        while True:
            for message_to, timers in execution_time.items():
                for i, timer in enumerate(timers):
                    # get the current time
                    current_time = datetime.datetime.now().time()
                    print(f'~{i}~~{timer[2] == current_time}~{timer[2]}~~', current_time)

                    # check if the current time matches the execution time
                    if current_time == timer[2]:
                        # execute the function
                        send_msg('text', Bot.qoute(), message_to)
                    else:
                        # sleep for one minute and check again
                        time.sleep(60)


@app.route('/receive_msg', methods=['POST', 'GET'])
def webhook():
    msg = request.get_json()
    try:
        if msg['entry'][0]['changes'][0]['value']['messages'][0]['id']:
            message = msg['entry'][0]['changes'][0]['value']['messages'][0]
            message_id = message['id']
            message_text = message['text']['body'].lower().strip()
            contact_name = msg['entry'][0]['changes'][0]['value']['contacts']['profile']['name']
            response_body = 'error'
            response_type = 'text'

            if message['type'] == 'text':
                if message_text.startswith('--'):
                    message_text = message_text.replace('--', '').strip()
                    if message_text.split(' ')[0] in triggers['gif']:
                        response_body = Bot.gif(message_text)
                        response_type = 'video'
                    elif message_text.split(' ')[0] in triggers['love']:
                        response_body = Bot.qoute(contact_name)
                        response_type = 'text'
                    elif message_text.split(' ')[0] in triggers['timer']:
                        send_msg('text', Bot.set_timer(message_text, message['from']), message['from'])

            send_msg(response_type, response_body, message['from'])
    except Exception as e:
        pass
    return '200 OK HTTPS.'


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
