import requests
import random
import time
import sys
import os
from hashlib import md5

from rwpy.mod import Mod
from rwpy.code import Ini,Section,Attribute,read_multiline,to_multiline
from rwpy.errors import ModNotExistsError

appid = ''
appkey = ''
wait_time = 1.0
flang = 'en'
tlang = 'zh'
endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path

names: list= [
'displayText',
'displayDescription',
'text',
'description',
'showMessageToPlayer'
]

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

def make_salt():
    return random.randint(32768, 65536)

class BaiduTranslator(object):
    def __init__(self,appid: str,appkey: str,from_lang: str='en',to_lang: str='zh'):
        self.__appid = appid
        self.__appkey = appkey
        self.from_lang = from_lang
        self.to_lang = to_lang

    def translate(self,query: str):
        salt =str(make_salt())
        sign = make_md5(self.__appid + query + salt + self.__appkey)
        payload = {'appid': self.__appid, 'q': query, 'from': self.from_lang, 'to': self.to_lang, 'salt': salt, 'sign': sign}
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()
        return result['trans_result']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('参数错误')
        exit(-1)
    args = []
    for arg in sys.argv:
        args.append(arg)
    last = ''
    while len(args) > 0:
        last = args.pop(0)
        if last.startswith('-f'):
            flang = last.lstrip('-f').strip('\"')
            last = ''
        elif last.startswith('-t'):
            tlang = last.lstrip('-t').strip('\"')
            last = ''
        elif last.startswith('-id'):
            appid = last.lstrip('-id').strip('\"')
        elif last.startswith('-key'):
            appkey = last.lstrip('-key').strip('\"')
        elif last.startswith('-'):
            print('错误的参数\"{0}\"'.format(last))
            exit(-3)
    if last == '':
        print('未提供Mod文件夹参数')
        exit(-4)
    mod = None
    try:
        mod = Mod(last)
    except ModNotExistsError:
        print('Mod不存在')
        exit(-2)

    bt = BaiduTranslator(appid,appkey,from_lang=flang,to_lang=tlang)
    inis = mod.getinis()
    lang = Ini(os.path.join(mod.dir,'lang.template'))
    lang.get_section('core').get_attribute('@copyFromSection').value = 'template_default,template_' + tlang
    default_sec = lang.get_section('template_default')
    tolang_sec = lang.get_section('template_' + tlang)
    

    for ini in inis:
        flag = False
        if ini.filename.endswith('.ini'):
            src = read_multiline(ini.get_section('core').get_attribute('copyFrom').value)
            if src != '' or not src.isspace():
                src += ',\n'
            src += 'ROOT:lang.template'
            ini.core['copyFrom'].value = to_multiline(src)
            
        for sec in ini.sections:
            for attr in list(filter(lambda x: x.key in names,sec.getattrs())):
                flag = True
                default_global = '{0}_{1}_{2}_{3}'.format('default',os.path.basename(ini.filename.rstrip('.ini')),sec.name,attr.key)
                tolang_global = '{0}_{1}_{2}_{3}'.format(tlang,os.path.basename(ini.filename.rstrip('.ini')),sec.name,attr.key)
                default_sec.get_attribute('@global ' + default_global).value = attr.value
                t = attr.value
                attr.value = '${' + default_global + '}'
                sec.get_attribute(attr.key + '_' + tlang).value = '${' + tolang_global + '}'
                try:
                    tran = bt.translate(t)
                    time.sleep(wait_time)
                    trans = ''
                    trans = tran[0]['dst']
                    tolang_sec.get_attribute('@global ' + tolang_global).value = trans
                except KeyError:
                    print('文件{0}翻译出错'.format(ini.filename),end=',')
                    print('出错位置：{0}段落{1}行'.format(sec.name,attr.linenum))
                    print(str(trans))

        try:
            ini.write()
        except IOError:
            print('文件：{0}写入失败'.format(ini.filename))
    
    try:
        lang.write()
    except IOError:
        print('文件：{0}写入失败'.format(lang.filename))
    

