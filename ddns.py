print('''ddns-py 启动！
一款用于 cloudflare DNS 的 DDNS 工具。
版本：1.3
作者：bddjr
仓库：https://github.com/bddjr/ddns-py
=============================================='''
)

#部分源码借鉴自 https://zhuanlan.zhihu.com/p/461993720

#Py3自带模块
import json, time, sys, copy, os

def logger(text):
    if isinstance(text, dict):
        text = json.dumps(text, indent=4)
    print("[{}] {}".format(
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        text
    ))

try:
    #Py3可能不自带的模块
    def pip_install(name):
        logger('尝试使用清华源安装模块 '+name)
        cmd = 'pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple'
        print(cmd)
        os.system(cmd)
        print()

        logger('尝试导入模块 '+name)
        try:
            exec('import ' + name)
            return
        except: pass

        logger('尝试直接安装模块 '+name)
        cmd = 'pip install requests'
        print(cmd)
        os.system(cmd)
        print()

        logger('再次尝试导入模块 '+name)
        try:
            exec('import ' + name)
            return
        except: pass

        logger('导入失败。:(')
        exit()

    try: import requests
    except: pip_install('requests')

    del pip_install

    config_filepath = 'ddns.py.config.json'
    logger('读取配置文件 ' + config_filepath)
    if not os.path.exists(config_filepath):
        logger('未找到配置文件，尝试生成模板')
        with open(config_filepath, 'x') as f:
            f.write(
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
        exit()

    config = json.load(open(config_filepath, 'r'))

    config = {
        "api_key": str.strip(config['api_key']),
        "zone_id": str.strip(config['zone_id']),
        "type": str.upper(str.strip(config['type'])),
        "get_ip_from": str.strip(config['get_ip_from']),
        "name": str.lower(str.strip(config['name'])),
        "ttl": int(config['ttl']),
        "proxied": bool(config['proxied'])
    }

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
        logger('【提醒】请预先确认您的网络支持公网IPv4再使用。判断方法：路由器显示的 WAN IP 与 https://4.ipw.cn 显示的一致')
    elif config['type'] == "AAAA":
        if config_getipform_lower in ["https://4.ipw.cn","http://4.ipw.cn"]:
            logger('【错误】AAAA记录是用于IPv6的，但您错误地将get_ip_from填写为获取IPv4的，请改成 https://6.ipw.cn')
            exit()
        logger('【提醒】请预先确认您的网络支持公网IPv6再使用。家庭宽带可能需要将光猫、路由器的防火墙关闭（会暴露所有IPv6端口！）')
    else:
        logger('【错误】该程序不支持{}类型记录！请修改type'.format(config['type']))
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

    mode = None

    # 通过命令行参数，自动获得模式编号
    for i in sys.argv:
        stri = str.strip(i)
        if stri in ['mode=1','mode=2','mode=3']:
            mode = int(stri[-1])

    # 没有符合的命令行参数，询问
    if mode == None:
        try:
            mode = int(input(
'''选择操作模式
%s
请输入编号：''' % ('\n'.join(modelist))
            ))
        except:
            print('\n输入格式错误！')
            exit()
        print('')

    print('模式：%s\n—————————————————————————' % (modelist[mode-1]))
    del modelist


    headers = {
        'Authorization': 'Bearer ' + config['api_key'],
        'Content-Type': 'application/json'
    }

    ip = None
    def get_ip():
        logger('获取 IP')
        global ip
        resp = requests.get(config['get_ip_from'])
        if resp.status_code != 200:
            raise "HTTP ERROR " + resp.status_code
        ip = str.rstrip(resp.text)
        logger('IP: {}'.format(ip))


    def get_dns():
        resp = requests.get(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(config['zone_id']),
            headers = headers
        )
        loaded_json = json.loads(resp.text)
        #logger(loaded_json)
        if not loaded_json['success']:
            logger(loaded_json['errors'])
            return False
        return loaded_json


    def get_record(loaded_json):
        domains = loaded_json['result']
        for domain in domains:
            if config['name'] == domain['name'] and config['type'] == domain['type']:
                logger('指定类型的指定域名已有解析记录')
                return domain
        logger('指定类型的指定域名无记录')
        return None

    def set_dns():
        post_json = {
            'type': config['type'],
            'name': config['name'],
            'content': ip,
            'proxied': config['proxied'],
            'ttl': config['ttl']
        }

        def update_dns_record():
            if dns_id == None:
                logger('正在添加解析')
                resp = requests.post(
                    'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(
                        config['zone_id']
                    ),
                    json = post_json,
                    headers = headers
                )
            else:
                logger('正在更新解析')
                resp = requests.put(
                    'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(
                        config['zone_id'],
                        dns_id
                    ),
                    json = post_json,
                    headers = headers
                )
            loaded_json = json.loads(resp.text)
            #logger(loaded_json)
            if loaded_json['success']:
                return True
            else:
                logger(loaded_json['errors'])
                return False

        logger('获取 DNS')
        loaded_json = get_dns()
        if loaded_json == False:
            logger('获取失败。:(')
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
        update_dns_success = update_dns_record()
        if update_dns_success:
            logger('解析设置成功！:D')
        else:
            logger('解析设置失败。:(')
        return update_dns_success



    if mode == 1:
        get_ip()
        set_dns()

    elif mode == 2:
        try:
            get_ip()
            update_dns_success = set_dns()
            old_ip = ip
            run_mode_2_success = True
        except Exception as e:
            print(e)
            run_mode_2_success = False

        while True:
            if run_mode_2_success and update_dns_success:
                logger('{}秒后检测IP是否变化\n'.format(config['ttl']))
                time.sleep(config['ttl'])
            else:
                logger('似乎发生了错误，15秒后重试\n')
                time.sleep(15)

            try:
                get_ip()
                if old_ip == ip and update_dns_success and run_mode_2_success:
                    logger('本地对比IP无变化。')
                else:
                    update_dns_success = set_dns()
                    old_ip = ip
                run_mode_2_success = True
            except Exception as e:
                print(e)
                run_mode_2_success = False

    elif mode == 3:
        logger('获取 DNS')
        loaded_json = get_dns()
        if loaded_json == False:
            logger('获取失败。:(')
            exit()
        record = get_record(loaded_json)
        if record == None:
            exit()
        dns_id = record['id']

        logger('删除 DNS 解析记录')
        resp = requests.delete(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(
                config['zone_id'],
                dns_id
            ),
            headers = headers
        )
        loaded_json = json.loads(resp.text)
        #logger(loaded_json)
        if bool(loaded_json['success']):
            logger('解析删除成功！:D')
        else:
            logger(loaded_json['errors'])
            logger('解析删除失败。:(')


except KeyboardInterrupt:
    print('\nCtrl+C')
    sys.exit()
