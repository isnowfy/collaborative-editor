# -*- coding: utf-8 -*-

import os
import re
import json
import time

import bottle
from bottle import run
from bottle import route
from bottle import request
from bottle import response
from bottle import template
from bottle import static_file
from bottle import default_app

import handler
import models
import render

DEV_ROOT = os.path.realpath(os.path.dirname(__file__))
VALID = re.compile(r'^[a-z0-9A-z]+$')
valid_doc = lambda x:not not VALID.match(x)
bottle.TEMPLATE_PATH.append(DEV_ROOT+'/templates/')

@route('/')
def index():
    rand_doc = handler.get_rand()
    bottle.redirect('/doc/%s/' % rand_doc)

@route('/first', method='POST')
def first():
    doc = request.forms.get('doc')
    text = models.get('doc:%s' % doc)
    now = time.time()
    if text:
        now, text = text
    else:
        text = ''
    return json.dumps({'txt': text, 'timestamp': now})

@route('/password', method='POST')
def change_pass():
    password = request.forms.get('password')
    newpass = request.forms.get('newpassword')
    if not newpass:
        newpass = password
    doc = request.forms.get('doc')
    old = models.get('password:%s' % doc)
    if not old:
        old = ''
    if old != password:
        return 'error'
    models.set('password:%s' % doc, newpass)
    bottle.redirect('/pass/%s/%s/' % (newpass, doc))

@route('/pass/<passw>/<doc>/')
def pass_show(passw, doc):
    password = models.get('password:%s' % doc)
    if not password:
        password = ''
    if password != passw:
        return 'error'
    user = handler.get_rand()
    now = time.time()
    return template('test', user=user, timestamp=now, doc=doc, password=passw)

@route('/doc/<doc>/')
def show(doc):
    password = models.get('password:%s' % doc)
    if password:
        return template('pass', doc=doc)
    user = handler.get_rand()
    now = time.time()
    return template('test', user=user, timestamp=now, doc=doc, password='')

@route('/handle', method='POST')
def handle():
    parent = float(request.forms.get('parent'))
    doc = request.forms.get('doc')
    user = request.forms.get('user')
    patch = None
    if not valid_doc(doc):
        return json.dumps('error')
    while True:
        patch = handler.get_patch(doc, parent, user)
        if patch:
            break
        time.sleep(0.1)
    ret = {'timestamp': patch[0], 'version': patch[1], 'patch': patch[2]}
    return json.dumps(ret)

@route('/send', method='POST')
def send():
    diff = json.loads(request.forms.get('diff'))
    parent = float(request.forms.get('parent'))
    doc = request.forms.get('doc')
    version = int(request.forms.get('version'))
    user = request.forms.get('user')
    password = request.forms.get('password')
    old = models.get('password:%s' % doc)
    if not old:
        old = ''
    if not valid_doc(doc) or old != password:
        return 'error'
    handler.update(doc, parent, user, version, diff)

@route('/preview/<doc>/')
def preview(doc):
    return template('preview', doc=doc)
    
@route('/show/<doc>.js')
def share(doc):
    response.content_type = 'text/javascript; charset=utf-8'
    text = models.get('doc:%s' % doc)
    if not text:
        text = ''
    else:
        text = text[1]
    return render.get_js(text)

@route('/static/js/<path:path>')
def js(path):
    return static_file(path, root=DEV_ROOT+'/static/js/')

@route('/static/css/<path:path>')
def css(path):
    return static_file(path, root=DEV_ROOT+'/static/css/')

if __name__ == '__main__':
    run(host="0.0.0.0", port=7000, reloader=True)

app = default_app()
