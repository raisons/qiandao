# qiandao

基于Pydantic和APScheduler的签到框架

- 支持青龙[Todo]
- 支持docker
- 支持通知
- 支持一次性任务
- 支持定时任务

## 依赖
Python >= 3.11

## 支持应用:
- v2ex
- linux.do
- it之家
- 坦克App
- 掌上英雄联盟

## 支持通知:
- Bark

## 配置文件
配置文件具体参考项目根目录`example.qiandao.yaml`
使用时请复制一份文件名为`qiandao.yaml`
```yaml
# 通知（bark）
notify:
  hostname: "api.day.app"
  device_id: "device"

tasks:
  test:
    # 开启true，关闭false
    enable: false

  v2ex:
    enable: true
    # 填入不同应用需要的信息、cookies等
    cookies:

# 此为apscheduler的scheduler.add_job函数的参数
schedule:
  # crontab、interval、date三中
  # 此处为每日8点运行任务
  trigger: "cron"
  minute: 0
  hour: 8
  day: "*"
  month: "*"
  timezone: "Asia/Shanghai"
```

## 使用方式
### Docker Compose (推荐)

```shell
git clone https://github.com/raisons/qiandao.git
cd qiandao
cp example.qiandao.yaml qiandao.yaml
docker compose up -d --build
```

### 手动运行
1. 创建配置文件`qiandao.yaml`
2. 安装依赖，`pip install -r ./requirements.txt`
3. 运行，`python -m qiandao -c qiandao.yaml --scheduled`

> 参数：
> 
>    -c 配置文件路径
> 
>    --scheduled 定时任务运行，不加此参数为一次性任务，运行完即结束

### 青龙面板
Todo

### PIP包
Todo
