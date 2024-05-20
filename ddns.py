version = "1.9"

if __name__ != "__main__":
    raise TypeError('不支持作为模块导入')

try:
    print(
f'''ddns-py 启动！
一款用于 cloudflare DNS 的 DDNS 工具。
版本：{version}
作者：bddjr
仓库：https://github.com/bddjr/ddns-py
=============================================='''
    )

    #部分源码借鉴自 https://zhuanlan.zhihu.com/p/461993720

    #Py3自带模块
    import json, time, sys, copy, os, re

    def logger(text):
        if isinstance(text, dict):
            text = json.dumps(text, indent=4)
        print("[{}] {}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            text
        ))

    #Py3可能不自带的模块
    notChecked_pip3 = False
    def pip_install(name):
        global notChecked_pip3
        if notChecked_pip3:
            logger(f'检查 pip3 命令')
            cmd = 'pip3 -V'
            print(cmd)
            status = os.system(cmd)
            if status != 0:
                logger(f'请先安装 pip3 。:(')
                exit()
            notChecked_pip3 = False

        logger('尝试使用清华源安装模块 '+name)
        cmd = 'pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple'
        print(cmd)
        status = os.system(cmd)
        print()
        if status == 0:
            logger('尝试导入模块 '+name)
            exec('import ' + name)
            return

        logger('尝试直接安装模块 '+name)
        cmd = 'pip3 install requests'
        print(cmd)
        status = os.system(cmd)
        print()
        if status == 0:
            logger('尝试导入模块 '+name)
            exec('import ' + name)
            return

        logger(f'模块 {name} 安装失败，请检查是否联网。:(')
        exit()

    try: import requests
    except: pip_install('requests')

    del pip_install

    # 读配置
    dirname = os.path.dirname(__file__)

    config_filepath = 'ddns.py.config.json'
    mode = None

    # 通过命令行参数，自动获得模式编号
    for i in sys.argv:
        s = str.strip(i)
        if s.startswith('configfile='):
            config_filepath = s[len('configfile=') : ]
        elif s.startswith('mode='):
            mode = s[len('mode=') : ]

    logger('读取配置文件 ' + config_filepath)
    config_filepath = os.path.join(dirname, config_filepath)
    if not os.path.exists(config_filepath):
        logger('未找到配置文件')
        if str.lower(str.strip(input('您需要生成配置文件模板吗？(y/n)'))).startswith('y'):
            open(config_filepath, 'x', encoding='utf-8').write(
'''{
"api_key": "",
"zone_id": "",
"type": "A",
"get_ip_from": "https://4.ipw.cn",
"name": "example.com",
"ttl": 60,
"proxied": false
}
'''
            )
            logger('配置文件模板已生成，请在配置文件里填写 name（域名） api_key（API密钥） zone_id（区域ID）')
        else:
            logger('您已取消')
        exit()

    try:
        f = open(config_filepath, 'r', encoding='utf-8')
    except Exception as e:
        logger(e)
        logger('配置文件读取失败，请检查文件权限。:(')
        exit()
    try:
        config = json.load(f)
        f.close()
        del f
    except:
        logger('配置文件读取失败，JSON格式错误。:(')
        exit()
    del config_filepath

    try:
        config = {
            "api_key": str.strip(config['api_key']),
            "zone_id": str.strip(config['zone_id']),
            "type": str.upper(str.strip(config['type'])),
            "get_ip_from": str.strip(config['get_ip_from']),
            "name": str.lower(str.strip(config['name'])),
            "ttl": int(config['ttl']),
            "proxied": bool(config['proxied'])
        }
    except:
        logger('配置文件读取失败，请检查是否有缺失的项，或类型是否正确，可尝试将配置文件删除或重命名，然后运行程序重新生成再填写。')

    def pixel_str(instr):
        return instr[0:3] + "*" * (len(instr)-6) + instr[-3:]

    printconfig = copy.deepcopy(config)
    printconfig['api_key'] = pixel_str(printconfig['api_key'])
    printconfig['zone_id'] = pixel_str(printconfig['zone_id'])
    logger(json.dumps(printconfig, indent=4))
    del printconfig

    b = False
    if config['api_key'] == '':
        logger('【错误】请在配置文件里填写 api_key（API密钥）')
        b = True
    if config['zone_id'] == '':
        logger('【错误】请在配置文件里填写 zone_id（区域ID）')
        b = True
    if config['name'] in ['','example.com']:
        logger('【错误】请在配置文件里填写 name（域名）')
        b = True
    if config['ttl'] < 1:
        logger('【错误】TTL不得小于1秒！')
        b = True

    if b:
        exit()
    del b

    config_getipform_lower = str.lower(config['get_ip_from'])
    if config['type'] == "A":
        if config_getipform_lower in ["https://6.ipw.cn","http://6.ipw.cn"]:
            logger('【错误】A记录是用于IPv4的，但您错误地将get_ip_from填写为获取IPv6的，请改成 https://4.ipw.cn')
            exit()
        logger('【提醒】请预先确认您的网络支持公网IPv4再使用。')
        ipRegexp = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
    elif config['type'] == "AAAA":
        if config_getipform_lower in ["https://4.ipw.cn","http://4.ipw.cn"]:
            logger('【错误】AAAA记录是用于IPv6的，但您错误地将get_ip_from填写为获取IPv4的，请改成 https://6.ipw.cn')
            exit()
        logger('【提醒】请预先确认您的网络支持公网IPv6再使用。家庭宽带可能需要将光猫、路由器的防火墙关闭（会暴露所有IPv6端口！）')
        ipRegexp = re.compile(r'([0-9a-fA-F]{1,4})?(::?[0-9a-fA-F]{1,4}){1,7}')
    else:
        logger(f'【错误】该程序不支持{config['type']}类型记录！请修改type')
        exit()
    del config_getipform_lower

    if config['proxied']:
        logger('【警告】开启 proxied 仅用于为网页服务器套 cloudflare CDN 作为防护，其它多数服务不适用，还可能会减速，请慎重开启')

    print('—————————————————————————')


    modelist = [
        '1 更新记录后退出',
        '2 循环检查IP变化并更新记录',
        '3 删除记录后退出'
    ]

    # 没有符合的命令行参数，询问
    if mode == None:
        mode = input(
f'''选择操作模式
{'\n'.join(modelist)}
请输入编号：'''
        )
    
    try:
        mode = int(mode)
        print('\n模式：' + modelist[mode-1])
    except:
        print('\n找不到模式，请检查输入是否有误。:(')
        exit()

    del modelist
    print('—————————————————————————')


    headers = {
        'Authorization': f'Bearer {config['api_key']}',
        'Content-Type': 'application/json'
    }

    ip = None
    def get_ip():
        logger('获取 IP')
        global ip
        ip = None
        try:
            resp = requests.get(config['get_ip_from'])
        except Exception as e:
            logger(e)
            return
        if resp.status_code != 200:
            logger(f"获取IP失败！HTTP状态码 {resp.status_code}")
            return
        ipMatched = ipRegexp.search(resp.text)
        if ipMatched:
            ip = ipMatched.group(0)
            logger('IP: ' + ip)
        else:
            logger(f"获取IP失败！正则表达式找不到IP")


    def get_dns():
        try:
            resp = requests.get(
                f'https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records',
                headers = headers
            )
        except Exception as e:
            logger(e)
            logger('获取DNS失败，请检查是否断网。:(')
            return False
        try:
            loaded_json = json.loads(resp.text)
        except Exception as e:
            logger(e)
            logger('获取DNS后遇到了未知的问题，网络请求已完成，但返回的JSON解码失败。:(')
            return False
        #logger(loaded_json)
        if loaded_json['success']:
            return loaded_json
        logger(loaded_json['errors'])
        logger('获取DNS失败，请检查api_key与zone_id是否有效。:(')
        return False


    def get_record(loaded_json):
        domains = loaded_json['result']
        for d in domains:
            if config['name'] == d['name'] and config['type'] == d['type']:
                logger('指定类型的指定域名已有解析记录')
                return d
        logger('指定类型的指定域名无记录')
        return None
    
    

    def set_dns():
        if ip == None:
            return False
        post_json = {
            'type': config['type'],
            'name': config['name'],
            'content': ip,
            'proxied': config['proxied'],
            'ttl': config['ttl']
        }

        def update_dns_record():
            try:
                if dns_id == None:
                    logger('正在添加解析')
                    resp = requests.post(
                        f'https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records',
                        json = post_json,
                        headers = headers
                    )
                else:
                    logger('正在更新解析')
                    resp = requests.put(
                        f'https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records/{dns_id}',
                        json = post_json,
                        headers = headers
                    )
            except Exception as e:
                logger(e)
                logger('解析设置失败，请检查是否断网。:(')
                return False
            try:
                loaded_json = json.loads(resp.text)
            except Exception as e:
                logger(e)
                logger('尝试设置解析后遇到了未知的问题，网络请求已完成，但返回的JSON解码失败。:(')
                return False
            #logger(loaded_json)
            if loaded_json['success']:
                logger('解析设置成功！:D')
                return True
            logger(loaded_json['errors'])
            logger('解析设置失败，请检查api_key与zone_id是否有效。:(')
            return False

        logger('获取 DNS')
        loaded_json = get_dns()
        if loaded_json == False:
            return False
        record = get_record(loaded_json)
        if record != None:
            if record['content'] == ip:
                logger('DNS对比IP无变化。')
                return True
            dns_id = record['id']
        else:
            dns_id = None

        logger('设置 DNS')
        return update_dns_record()



    if mode == 1:
        get_ip()
        set_dns()
    elif mode == 2:
        get_ip()
        update_dns_success = set_dns()
        old_ip = ip

        while True:
            if update_dns_success:
                sleep_time = max(config['ttl'], 60)
                logger(f'{sleep_time}秒后检测IP是否变化\n')
            else:
                sleep_time = 30
                logger(f'似乎发生了错误，{sleep_time}秒后重试\n')

            time.sleep(sleep_time)

            get_ip()
            if old_ip == ip and update_dns_success:
                logger('本地对比IP无变化。')
            else:
                update_dns_success = set_dns()
                old_ip = ip
    elif mode == 3:
        logger('获取 DNS')
        loaded_json = get_dns()
        if loaded_json == False:
            exit()
        record = get_record(loaded_json)
        if record == None:
            exit()
        dns_id = record['id']

        logger('删除 DNS 解析记录')
        try:
            resp = requests.delete(
                f'https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records/{dns_id}',
                headers = headers
            )
        except Exception as e:
            logger(e)
            logger('解析删除失败，请检查是否断网。:(')
            exit()
        try:
            loaded_json = json.loads(resp.text)
        except Exception as e:
            logger(e)
            logger('尝试设置解析后遇到了未知的问题，网络请求已完成，但返回的JSON解码失败。:(')
            exit()
        #logger(loaded_json)
        if loaded_json['success']:
            logger('解析删除成功！:D')
        else:
            logger(loaded_json['errors'])
            logger('解析删除失败，请检查api_key与zone_id是否有效。:(')


except KeyboardInterrupt:
    print('\nCtrl+C')
