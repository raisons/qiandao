FROM python:3.11.7

WORKDIR /qiandao

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Shanghai

COPY requirements.txt /qiandao/requirements.txt

# 安装依赖
RUN pip install --no-cache-dir  -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY qiandao /qiandao/

COPY ./entrypoint /qiandao/entrypoint

ENTRYPOINT ["./entrypoint", "web"]