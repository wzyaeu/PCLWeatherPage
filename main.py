from flask import Flask, request
import os
import time
import json
import requests
from datetime import datetime
import re
import threading

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import base64

app = Flask(__name__)
FILE_PATH = os.path.dirname(__file__)
VERSION = 'v1.2-20260705'

timestamp = lambda : int(time.time())

def api(path,params={}):
    print('请求api')
    url = f'https://{content['apihost']}{path}'
    return requests.get(url,headers={
        'Authorization':f'Bearer {jwt}'
    },params=params).text

def check_file(filename = None):
    global content
    if filename is None:
        os.makedirs(os.path.join(FILE_PATH,'svgfiles'),exist_ok=True)
        os.makedirs(os.path.join(FILE_PATH,'weatherdata'),exist_ok=True)
        os.makedirs(os.path.join(FILE_PATH,'config'),exist_ok=True)
        files = [
            ('priv',''),
            ('pub',''),
            ('apihost',''),
            ('locations',''),
            ('pid',''),
            ('tid',''),
            ('port','2521'),
        ]
        content = {}

        for name, default in files:
            file_path = os.path.join(FILE_PATH, 'config', name+'.txt')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    fd = f.read().strip()
                    if not fd:
                        with open(file_path, 'w') as fw:
                            fw.write(default)
                        fd = default
            else:
                with open(file_path, 'w') as fw:
                    fw.write(default)
                fd = default
            content[name] = fd

    else:
        file_path = os.path.join(FILE_PATH, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                fd = f.read().strip()
        else:
            fd = ''
        return fd
    
def check_port():
    if not content.get('port').isdigit(): # type: ignore
        content['port'] = '2521'
        with open(os.path.join(FILE_PATH, 'port.txt'), 'w') as fw:
            fw.write('2521')
    if not (1 <= int(content['port']) <= 25565):
        content['port'] = '2521'
        with open(os.path.join(FILE_PATH, 'port.txt'), 'w') as fw:
            fw.write('2521')
    return int(content['port'])

def gen_jwt():
    try:
        global gen_jwt, jwt_end_time
        base64url_encode = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode("ascii")

        header = {
            "alg": "EdDSA",
            "kid": content['tid']
        }

        jwt_end_time = timestamp()-30+2*60*60

        payload = {
            "sub": content['pid'],
            "iat": timestamp()-30,
            "exp": jwt_end_time
        }

        private_key = serialization.load_pem_private_key(
            content['priv'].encode(),
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(f'{base64url_encode(json.dumps(header).encode())}.{base64url_encode(json.dumps(payload).encode())}'.encode()) # type: ignore

        return f'{base64url_encode(json.dumps(header).encode())}.{base64url_encode(json.dumps(payload).encode())}.{base64url_encode(signature)}'
    except:
        return ''
    
def read_tamplate(name):
    tname = os.path.join(FILE_PATH,'templates',name+'.xaml')
    with open(tname,'r',encoding='utf-8') as f:
        return f.read()
    
def replaces(string: str, s: dict):
    output = string
    for l, d in s.items():
        output = output.replace('{'+l+'}', d)
    return output

def iso8601_to_normaltime(iso: str):
    dt = datetime.fromisoformat(iso)
    return dt.strftime("%m/%d %H:%M")

def svg_to_xamlpath(icon):
    if os.path.exists(os.path.join(FILE_PATH,'svgfiles',icon+'.svg')):
        with open(os.path.join(FILE_PATH,'svgfiles',icon+'.svg'), 'r', encoding='utf-8') as f:
            svgdata = f.read()
    else:
        svgdata = requests.get(f'https://icons.qweather.com/assets/icons/{icon}.svg',headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0'}).text
        with open(os.path.join(FILE_PATH,'svgfiles',icon+'.svg'), 'w', encoding='utf-8') as f:
            f.write(svgdata)
    d_values = re.findall(r'd="([^"]+)"', svgdata)
    result = " ".join(d_values)
    return result

@app.route('/')
def mainpage():
    print('获取到请求')
    global jwt, jwt_end_time
    location = request.args.get('location','')
    t_error = read_tamplate('error')
    
    if jwt == '':
        print('配置未达到要求被驳回')
        return t_error.replace('{{text}}','JWT生成错误，检查你的配置。')
    elif not content['apihost']:
        print('配置未达到要求被驳回')
        return t_error.replace('{{text}}','未填写apihost。')
    elif not location:
        print('地址未达到要求被驳回')
        return t_error.replace('{{text}}','获取地址中locationID未填写。')
    elif location not in content['locations'].splitlines():
        print('地址未达到要求被驳回')
        return t_error.replace('{{text}}','地址中locationID不在locations.txt。')
    
    print(f'jwt结束时间 {jwt_end_time} 当前时间 {timestamp()}')
    if jwt_end_time - 1*60 < timestamp(): # 在最后1分钟前刷新
        print('重新生成jwt')
        jwt = gen_jwt()

    print('接受请求')
    t_mainpage = read_tamplate('mainpage')
    t_futweather_item = read_tamplate('futweather-item')

    location_data_nowtime_file = f'weatherdata/nowweather-time-{location}.txt'
    location_data_nowdata_file = f'weatherdata/nowweather-data-{location}.txt'
    nowweather_time = (lambda x: 0 if x == '' else x)(check_file(location_data_nowtime_file))
    print(f'nowweather格式化后时间 {nowweather_time} 当前格式化后时间 {int(timestamp()/(30*60))}')
    try:
        nowweather_time = int(nowweather_time) # type: ignore
        assert nowweather_time == int(timestamp()/(30*60))
    except:
        print(f'nowweather重新获取内容')
        nowweather_time = int(timestamp()/(30*60))
        with open(os.path.join(FILE_PATH, location_data_nowtime_file),'w',encoding='utf-8') as f:
            f.write(str(int(timestamp()/(30*60))))
        nowweather_data = json.loads(api('/v7/weather/now',{'location':location}))
        with open(os.path.join(FILE_PATH, location_data_nowdata_file),'w',encoding='utf-8') as f:
            json.dump(nowweather_data,f,ensure_ascii=False)
    else:
        with open(os.path.join(FILE_PATH, location_data_nowdata_file),'r',encoding='utf-8') as f:
            nowweather_data = json.load(f)
        
    location_data_futtime_file = f'weatherdata/futweather-time-{location}.txt'
    location_data_futdata_file = f'weatherdata/futweather-data-{location}.txt'
    futweather_time = (lambda x: 0 if x == '' else x)(check_file(location_data_futtime_file))
    print(f'futweather格式化后时间 {nowweather_time} 当前格式化后时间 {int(timestamp()/(30*60))}')
    try:
        futweather_time = int(futweather_time) # type: ignore
        assert futweather_time == int(timestamp()/(60*60))
    except:
        print(f'futweather重新获取内容')
        futweather_time = int(timestamp()/(60*60))
        with open(os.path.join(FILE_PATH, location_data_futtime_file),'w',encoding='utf-8') as f:
            f.write(str(int(timestamp()/(60*60))))
        futweather_data = json.loads(api('/v7/weather/30d',{'location':location}))
        with open(os.path.join(FILE_PATH, location_data_futdata_file),'w',encoding='utf-8') as f:
            json.dump(futweather_data,f,ensure_ascii=False)
    else:
        with open(os.path.join(FILE_PATH, location_data_futdata_file),'r',encoding='utf-8') as f:
            futweather_data = json.loads(f.read())

    print(f'开始获取主页')
    t_mainpage = replaces(t_mainpage,{
        'locations':location,
        'nowweather-time':iso8601_to_normaltime(nowweather_data['now']['obsTime']),
        'nowweather-temp':(nowweather_data['now']['temp']),
        'nowweather-weathericon':svg_to_xamlpath(nowweather_data['now']['icon']),
        'nowweather-feeltemp':(nowweather_data['now']['feelsLike']),
        'nowweather-weather':(nowweather_data['now']['text']),
        'nowweather-winddir':(nowweather_data['now']['windDir'][:-1]),
        'nowweather-windscale':(nowweather_data['now']['windScale']),
        'nowweather-windspeed':(nowweather_data['now']['windSpeed']),
        'nowweather-humidity':(nowweather_data['now']['humidity']),
        'nowweather-precip':(nowweather_data['now']['precip']),
        'nowweather-cloud':(lambda x:'Uk' if x == '' else x)(nowweather_data['now'].get('cloud','Uk')),
        'nowweather-vis':(nowweather_data['now']['vis']),
        'nowweather-pressure':(nowweather_data['now']['pressure']),
        'nowweather-dew':(lambda x:'Uk' if x == '' else x)(nowweather_data['now'].get('dew','Uk')),

        'futweather-time':iso8601_to_normaltime(futweather_data['updateTime']),
        'futweather-items':'\n'.join([
            replaces(t_futweather_item,{
                'date':(day_data['fxDate'][5:]),
                'maxtemp':(day_data['tempMax']),
                'mintemp':(day_data['tempMin']),
                'dayicon':svg_to_xamlpath(day_data['iconDay']),
                'nighticon':svg_to_xamlpath(day_data['iconNight']),
                'precip':(day_data['precip']),
                'humidity':(day_data['humidity']),
            })
            for index, day_data in enumerate(futweather_data['daily'], start=1)
        ]),

        'nowweather-sources':', '.join(nowweather_data['refer']['sources']),
        'nowweather-license':'\\n'.join(nowweather_data['refer']['license']),
        'futweather-sources':', '.join(futweather_data['refer']['sources']),
        'futweather-license':'\\n'.join(futweather_data['refer']['license']),

        'version':VERSION
    })

    print(f'完毕')
    return t_mainpage

check_file()
jwt = gen_jwt()
app.run(port=check_port(), debug=True)