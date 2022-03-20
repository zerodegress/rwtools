#!/usr/bin/env python3
import sys
import os
import shutil
import datetime
import re
import json
from typing import List,Tuple,Optional
from zipfile import ZipFile

from tqdm import tqdm
from colorama import Fore,Back,Style

from rwpy.mod import Mod
from rwpy.code import Ini,Section,Element,Attribute
from rwpy.util import CodeList,load_codelist,filterl


def mkmsg(file: str,linenum: int,content: str,desc: str) -> Tuple[str,int,str]:
    return (file,linenum,'行号:{0}|{1}->{2}'.format(linenum,desc,content))


def exitr(code: int):
    if target_name == '.tmprw':
        shutil.rmtree(target_name,True)
    exit(code)


def err(text: str):
    print(Fore.RED + text + Style.RESET_ALL)


def prompt(text: str):
    print(Fore.YELLOW + text + Style.RESET_ALL)


def info(text: str):
    print(text)
    

if __name__ == '__main__':
    argv: List[str] = sys.argv[1:]
    target_name: str = ''
    if len(argv) == 0:
        err('参数不足')
        exit(-1)
    else:
        if argv[-1].startswith('-'):
            err('缺少目标参数')
            exit(-2)
        target_name = argv[-1]
        argv.pop()
        
    if not os.path.exists(target_name):
        err('路径不存在')
        exit(-4)
        
    if os.path.isfile(target_name):
    
        if not target_name.endswith('.zip') and not target_name.endswith('.rwmod'):
            err('目标文件不是可用的压缩文件')
            exit(-3)
            
        else:
            with ZipFile(target_name) as rwmod:
                os.mkdir('.tmprw')
                rwmod.extractall('.tmprw')
                target_name = '.tmprw'
                
    withcl: bool = False
    codelist: Optional[dict] = None
    
    if os.path.isfile('ncodelist.json'):
        withcl = True
        with open('ncodelist.json','r') as f:
            codelist = json.loads(f.read())
                
    mod: Mod = Mod(target_name)
    inis: List[Ini] = mod.getinis()
    errors: List[str] = []
    prompts: List[str] = []
    mpbar = tqdm(inis)
    
    for ini in mpbar:
        
        if ini.filename == 'mod-info.txt':
            continue
        
        mpbar.set_description('正在检查{0}'.format(ini.filename))
        
        for attr in ini.attributes:
            prompts.append(mkmsg(ini.filename,attr.linenum,str(attr),'不建议ini头部出现属性'))
            
        for ele in ini.elements:
            if re.match(r'^\s*(#.*)?$',str(ele)) is None:
                errors.append(mkmsg(ini.filename,ele.linenum,str(ele),'非法的ini头部元素'))
                
        spbar = tqdm(ini.sections)
        for sec in spbar:
            spbar.set_description('正在检查段落{0}'.format(sec.name))
            msec: Optional[dict] = None
        
            if sec.name.startswith('comment_'):
                continue
                
            if not withcl:
                continue        
                
            if not sec.name.startswith('template'):
                for s in codelist['sections']:
                    if not re.match(s['name'],sec.name) is None:
                        msec = s
                if msec is None:
                    errors.append(mkmsg(ini.filename,sec.linenum,'[{0}]'.format(sec.name),'未知的段落名'))
                    continue
                    
            
            apbar = tqdm(sec.getattrs())
            for attr in apbar:
                apbar.set_description('正在检查{0}'.format(str(attr)))
                p: List[Tuple[str,str]] = []
                
                if withcl:
                    
                    if not sec.name.startswith('template'):
                        flag: bool = True
                        
                        for a in msec['attributes']:
                            if not re.match(a['key'],attr.key) is None:
                                flag = False
                        if flag:
                            errors.append(mkmsg(ini.filename,attr.linenum,str(attr),'未知的属性'))
                            apbar.set_description('\"{0}\"出错:{1}'.format(str(attr),'未知的属性'))
                            
            apbar.close()
            
        spbar.close()
            
    mpbar.close()
    
    if len(errors) + len(prompts) <= 10:
        print(Fore.RED) 
        
        for error in errors:
            print('文件:{0}|{1}'.format(error[0],error[2]))
    
        print(Fore.YELLOW)
    
        for pro in prompts:
            print('文件:{0}|{1}'.format(pro[0],pro[2]))
    
        print(Style.RESET_ALL)
        
    else:
    
        with open(str(datetime.date.today()) + '.txt','w') as f:
        
            for error in sorted(errors,key=lambda x: x[0]):
                f.write('文件:{0}|{1}\n'.format(error[0],error[2]))
                
            for pro in sorted(prompts,key=lambda x: x[0]):
                f.write('文件:{0}|{1}\n'.format(pro[0],pro[2]))
                
        print('条目较多，已输出到{0}.txt中'.format(str(datetime.date.today())))
    
    if target_name == '.tmprw':
        shutil.rmtree(target_name,True)
        