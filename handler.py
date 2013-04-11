# -*- coing: utf-8 -*-

import time
import random

import utils
import models

valid_char = map(chr, range(ord('a'), ord('a')+26)+range(ord('0'), ord('0')+10)+range(ord('A'), ord('A')+26))

def update(doc, parent, user, version, diff):
    if not diff:
        return
    models.lock_acquire(doc)
    now = time.time()
    patch = models.get(doc)
    if not patch:
        patch = []
    pre = []
    version_count = models.get('version:%s:%s' % (user, doc))
    if not version_count:
        version_count = 0
    version_max = models.get('versionmax:%s:%s' % (user, doc))
    if not version_max:
        version_max = 0
    version_time = models.get('versiontime:%s:%s' % (user, doc))
    if not version_time:
        version_time = 0
    same = []
    if parent != version_time:
        models.set('version:%s:%s' % (user, doc), 1, now+60)
        models.set('versionmax:%s:%s' % (user, doc), version, now+60)
        models.set('versiontime:%s:%s' % (user, doc), parent, now+60)
        if version == 1:
            same = [(version, diff)]
        else:
            models.set('versions:%s:%s' % (user, doc), [(version, diff)], now+60)
    else:
        same = models.get('versions:%s:%s' % (user, doc))
        if not same:
            same = []
        version_count += 1
        models.set('version:%s:%s' % (user, doc), version_count, now+60)
        if version > version_max:
            version_max = version
        models.set('versionmax:%s:%s' % (user, doc), version_max, now+60)
        if version_count == version_max:
            same.append((version, diff))
            models.delete('versions:%s:%s' % (user, doc))
        else:
            models.set('versions:%s:%s' % (user, doc), same+[(version, diff)], now+60)
            same = []
    if not same:
        models.lock_release(doc)
        return
    same = sorted(same)
    version = same[0][0]
    for i in reversed(patch):
        if i['timestamp'] == parent or (i['user'] == user and i['version']+1 == version):
            break
        pre = i['diff']+pre
    diff = []
    for i in same:
        diff += utils.forward(pre, i[1])
    version = same[-1][0]
    ret = {'parent': parent, 'timestamp': now, 'user': user, 'version': version, 'diff': diff}
    models.set(doc, filter(lambda x:x['timestamp']>=now-60, patch)+[ret])
    models.set('last:%s' % doc, now)
    text = models.get('doc:%s' % doc)
    if text:
        text = text[1]
    else:
        text = ''
    text = utils.text_patch(text, diff)
    models.set('doc:%s' % doc, (now, text))
    models.lock_release(doc)

def get_patch(doc, parent, user):
    timestamp = models.get('last:%s' % doc)
    if not timestamp or timestamp <= parent:
        return False
    diff = models.get(doc)
    if not diff:
        diff = []
    ret = []
    version = 0
    for i in reversed(diff):
        if i['timestamp'] > timestamp:
            timestamp = i['timestamp']
        if i['timestamp'] == parent:
            break
        if i['user'] == user and i['version'] > version:
            version = i['version']
        ret = i['diff']+ret
    return (timestamp, version, ret)

def get_rand(l=6):
    ret = ''
    for i in xrange(l):
        ret += valid_char[random.randint(0, len(valid_char)-1)]
    return ret
