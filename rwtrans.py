import requests
import random
import time
import sys
import os
from hashlib import md5

from rwpy.mod import Mod
from rwpy.code import Ini,Section,Attribute
from rwpy.errors import ModNotExistsError

appid = ''
appkey = ''
WAIT_TIME = 1.0
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
    if len(sys.argv) != 2:
        print('参数错误')
        exit(-1)

    mod = None
    try:
        mod = Mod(sys.argv[1])
    except ModNotExistsError:
        print('Mod不存在')
        exit(-2)

    bt = BaiduTranslator(appid,appkey)
    inis = mod.getinis()
    lang = os.path.join(mod,'lang')
    os.mkdir(lang)
    default = Ini(os.path.join(lang,'default.lan'))
    default_sec = default.get_section('core')
    zh = Ini(os.path.join(lang,'zh.lan'))
    zh_sec = zh.get_section('core')

    for ini in inis:
        flag = False

        for sec in ini.sections:
            for attr in list(filter(lambda x: x.key in names,sec.getattrs())):
                flag = True
                replace_name = '{0}_{1}_{2}'.format(ini.filename,sec.name,attr.key)
                replace_name_zh = replace_name + '_zh'
                default_sec.append(Attribute('@global ' + replace_name,attr.value))
                tran = bt.translate(attr.value)
                trans = tran[0]['dst']
                #TODO
                sec.get_attribute(attr.key + '_zh').value = trans
                time.sleep(WAIT_TIME)

        if flag:
            try:
                ini.write()

            except IOError:
                print('文件{0}输出出错'.format(ini.filename))

