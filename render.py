# -*- coding: utf-8 -*-

import re
import urllib

from markdown import markdown

markdown_options = ['extra', 'codehilite']
host = 'http://doit.sinaapp.com'
#math_url = '<img src="http://latex.codecogs.com/gif.latex?%s"></img>'
math_url = '<img src="http://chart.apis.google.com/chart?cht=tx&chl=%s"></img>'
math_re = re.compile(r'(\$\$)')

def render(text):
    if not isinstance(text, unicode):
        text = text.decode('utf-8')
    return markdown(text, markdown_options)

def get_js(text):
    text = render(text)
    trans = lambda x: x.replace('\\', '\\\\').replace('\n', '\\n')
    tmp = math_re.split(text)
    text = ''
    s = ''
    find = False
    for item in tmp:
        if item == '$$':
            if find and len(s) < 200:
                text += math_url % urllib.quote(s)
            else:
                text += trans(s)
            find = not find
            s = ''
        else:
            s += item
    text += trans(s)
    ret = '''
    document.write('<link rel="stylesheet" href="%s/static/css/md_hl.css"/>');
    document.write('<link rel="stylesheet" href="%s/static/css/md_md.css"/>');
    document.write('<div id="doit" class="doit">%s</div>');
    ''' % (host, host, text)
    return ret
