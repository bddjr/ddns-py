# ddns-py
一款用于 cloudflare DNS 的 DDNS 工具。  

```
py ddns.py
ddns-py 启动！
一款用于 cloudflare DNS 的 DDNS 工具。
版本：1.10.3
作者：bddjr
仓库：https://github.com/bddjr/ddns-py
==============================================
[2026-03-16 16:07:53] 读取配置文件 ddns.py.config.json
[2026-03-16 16:07:53] {
    "api_key": "PYb**********************************_fv",
    "zone_id": "193bddad5f6be731564ddb79eff6b4d1",
    "type": "A",
    "get_ip_from": "https://ddns.oray.com/checkip",
    "name": "🔣🔣🔣🔣",
    "ttl": 60,
    "proxied": false
}
[2026-03-16 16:07:53] 【提醒】请预先确认您的网络支持公网IPv4再使用。
—————————————————————————
选择操作模式
1 更新记录后退出
2 循环检查IP变化并更新记录
3 删除记录后退出
请输入编号：1

模式：1 更新记录后退出
—————————————————————————
[2026-03-16 16:07:54] 获取 IP
[2026-03-16 16:07:55] IP: 🔣🔣🔣🔣
[2026-03-16 16:07:55] 获取解析
[2026-03-16 16:07:56] 指定类型的指定域名已有解析记录
[2026-03-16 16:07:56] 正在更新解析
[2026-03-16 16:08:02] 解析设置成功！:D
```

***
## 配置

### ip
如果使用IPv4（A），请确认您的网络支持公网IPv4。
```
    "type": "A",
    "get_ip_from": "https://ddns.oray.com/checkip",
```

如果使用IPv6（AAAA），请确认您的网络支持公网IPv6。家庭宽带可能需要将光猫、路由器的防火墙关闭（会暴露所有IPv6端口！）
```
    "type": "AAAA",
    "get_ip_from": "https://6.ipw.cn",
```

### api_key
在 <https://dash.cloudflare.com/profile/api-tokens> 上方的 “API令牌” 里点击 “创建令牌” ，然后找到 “编辑区域DNS” 并点击右边的 “使用模板” ，后面的步骤你自己来。

### zone_id
区域id。

### name
填写您想要DDNS的域名。

### ttl
填写DNS缓存时间（单位：秒）。

### proxied
开启 proxied 仅用于为网页服务器套 cloudflare CDN 作为防护，其它多数服务不适用，还可能会减速，请慎重开启

***
## 启动方法
### Windows
```
pip3 install requests
py ddns.py
```

### Ubuntu
```
pip3 install requests
python3 ddns.py
```

***
## 命令行参数
### 使用命令行参数跳过询问模式
在命令后面按照如下格式加上参数  
```
mode=2
```
其中 `=` 后面是模式编号，请参照下方列出的编号进行修改，不得在等号两侧添加空格。  
```
1 更新记录后退出
2 循环检查IP变化并更新记录
3 删除记录后退出
```

### 使用命令行参数指定配置文件读取路径
在命令后面按照如下格式加上参数  
```
configfile=ddns.py.config.json
```
其中 `=` 后面是配置文件所在的相对路径或绝对路径，相对路径参照`ddns.py`所在文件夹，而非命令行所在文件夹。  
不得在等号两侧添加空格。  
