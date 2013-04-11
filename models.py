# -*- coding: utf-8 -*-

import time

import sae.kvdb

kv = sae.kvdb.KVClient()

def set(key, value, timeout=0):
    for i in xrange(10000):
        ret = kv.set(key, value, timeout)
        if ret:
            break
        time.sleep(0.2)

def get(key):
    return kv.get(key)

def delete(key):
    kv.delete(key)

def set_append(key, value):
    t = str(time.time())
    kv.set('%s:%s' % (key, t), value)

def set_get(key):
    ret = kv.get_by_prefix(key, 1000)
    now = time.time()
    drop = filter(lambda x:float(x[0].split(':')[1])<now-60, ret)
    for item in drop:
        kv.delete(drop[0])
    return map(lambda x:x[1], filter(lambda x:float(x[0].split(':')[1])>=now-60, ret))

def lock_acquire(key):
    now = time.time()
    while True:
        tmp = kv.get('lock:%s' % key)
        if not tmp:
            kv.set('lock:%s' % key, now, now+600)
            tmp = kv.get('lock:%s' % key)
            if tmp == now:
                break
        time.sleep(0.1)

def lock_release(key):
    kv.delete('lock:%s' % key)
