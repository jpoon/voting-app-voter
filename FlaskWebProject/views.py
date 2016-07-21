from flask import Flask, render_template, request, make_response, g
from FlaskWebProject import app
from azure.storage.queue import QueueService, QueueMessageFormat
import os
import random
import json

option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")

storage_account = os.getenv('AZURE_STORAGE_ACCOUNT', '[MY_STORAGE_ACCOUNT_NAME]')
storage_access_key = os.getenv('AZURE_STORAGE_ACCESS_KEY', '[MY_STORAGE_ACCOUNT_ACCESS_KEY]')

def get_queue():
    if not hasattr(g, 'queue'):
        g.queue = QueueService(account_name=storage_account, account_key=storage_access_key)
        g.queue.create_queue('votes')
        g.queue.encode_function = QueueMessageFormat.text_base64encode
    return g.queue

@app.route("/", methods=['POST','GET'])
def home():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        queue = get_queue()
        vote = request.form['vote']
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        queue.put_message('votes', unicode(data))

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp