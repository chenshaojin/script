# 使用说明
- 启动脚本 `wx_exporter.py` 直接修改内部`yml`文件的参数调整调度周期
- 修改 `token` 的企业微信机器人的ID
- 修改 `wx_user` 文件下要通知的内容，会按照每行循环发送
```shell
$ docker login
  # → append the domain name of your Docker registry
  #   if you are not using Docker Hub; for example:
  # docker login quay.io
$ docker-compose build --pull
$ docker-compose push
# and optionally:
$ docker logout
``` 