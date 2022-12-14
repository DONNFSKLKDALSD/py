#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : rules.py.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Date  : 2022/8/25

import os
from time import time
import js2py
from utils.log import logger
from utils.web import get_interval,UA

def getRuleLists():
    base_path = os.path.dirname(os.path.abspath(__file__)) # 当前文件所在目录
    # print(base_path)
    file_name = os.listdir(base_path)
    file_name = list(filter(lambda x:str(x).endswith('.js') and str(x).find('模板') < 0,file_name))
    # print(file_name)
    rule_list = [file.replace('.js','') for file in file_name]
    # print(rule_list)
    return rule_list

def getRules(path='cache'):
    t1 = time()
    base_path = path+'/'  # 当前文件所在目录
    # print(base_path)
    os.makedirs(base_path,exist_ok=True)
    file_name = os.listdir(base_path)
    file_name = list(filter(lambda x: str(x).endswith('.js') and str(x).find('模板') < 0, file_name))
    # print(file_name)
    rule_list = [file.replace('.js', '') for file in file_name]
    js_path = [f'{path}/{rule}.js' for rule in rule_list]
    with open('js/模板.js', encoding='utf-8') as f:
        before = f.read()
    rule_codes = []
    # for js in js_path:
    #     with open(js,encoding='utf-8') as f:
    #         code = f.read()
    #         rule_codes.append(js2py.eval_js(before+code))

    ctx = js2py.EvalJs()
    codes = []
    for i in range(len(js_path)):
        js = js_path[i]
        with open(js,encoding='utf-8') as f:
            code = f.read()
            new_code = 'var muban = JSON.parse(JSON.stringify(mubanDict));\n'+code.replace('rule',f'rule{i}',1)
            # new_code = ''+code.replace('rule',f'rule{i}',1)
            codes.append(new_code)
    newCodes = before + '\n'+ '\n'.join(codes)
    # print(newCodes)
    ctx.execute(newCodes)
    for i in range(len(js_path)):
        rule_codes.append(ctx.eval(f'rule{i}'))

    # print(rule_codes)
    # print(type(rule_codes[0]),rule_codes[0])
    # print(rule_codes[0].title)
    # print(rule_codes[0].searchable)
    # print(rule_codes[0].quickSearch)
    new_rule_list = []
    for i in range(len(rule_list)):
        tmpObj = {
            'name':rule_list[i],
            'searchable':rule_codes[i].searchable or 0,
            'quickSearch':rule_codes[i].quickSearch or 0,
            'filterable':rule_codes[i].filterable or 0,
        }
        if rule_codes[i].multi:
            tmpObj['multi'] = 1
        new_rule_list.append(tmpObj)
    # print(new_rule_list)
    rules = {'list': new_rule_list, 'count': len(rule_list)}
    logger.info(f'自动配置装载耗时:{get_interval(t1)}毫秒')
    return rules

def jxTxt2Json(text:str):
    data = text.strip().split('\n')
    jxs = []
    for i in data:
        i = i.strip()
        dt = i.split(',')
        if not i.startswith('#') and len(i) > 10:
            try:
                jxs.append({
                    'name':dt[0],
                    'url':dt[1],
                    'type':dt[2] if len(dt) > 2 else 0,
                    'ua':dt[3] if len(dt) > 3 else UA,
                })
            except Exception as e:
                logger.info(f'解析行有错误:{e}')
    return jxs

def getJxs(path='js'):
    custom_jx = 'base/解析.conf'
    if not os.path.exists(custom_jx):
        with open(custom_jx,'w+',encoding='utf-8') as f1:
            msg = """# 这是用户自定义解析列表,不会被系统升级覆盖
# 0123，对应，普通解析，json解析，并发多json解析，聚合解析,参数3不填默认0
# flags是线路名称标识,会自动拦截并走以下的解析
# 名称，链接，类型,ua (ua不填默认 Mozilla/5.0) 可以手动填 Dart/2.14 (dart:io)
虾米,https://dm.xmflv.com:4433/?url=
            """
            f1.write(msg)

    with open(f'{path}/解析.conf',encoding='utf-8') as f:
        text = f.read()
    jxs = jxTxt2Json(text)
    with open(custom_jx,encoding='utf-8') as f2:
        text = f2.read()
    jxs2 = jxTxt2Json(text)
    jxs.extend(jxs2)
    print(f'共计{len(jxs)}条解析')
    return jxs

def getPys(path='txt/py'):
    t1 = time()
    base_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))  # 上级目录
    py_path = os.path.join(base_path, path)
    os.makedirs(py_path, exist_ok=True)
    file_name = os.listdir(py_path)
    file_name = list(filter(lambda x: str(x).endswith('.py'), file_name))
    # print(file_name)
    rule_list = [file.replace('.py', '') for file in file_name]
    py_path = [f'{path}/{rule}.py' for rule in rule_list]
    new_rule_list = []
    for i in range(len(rule_list)):
        new_rule_list.append({
            'name': rule_list[i],
            'searchable': 1,
            'quickSearch': 1,
            'filterable': 0,
        })
    logger.info(f'自动加载Pyramid耗时:{get_interval(t1)}毫秒')
    return new_rule_list

if __name__ == '__main__':
    print(getRuleLists())