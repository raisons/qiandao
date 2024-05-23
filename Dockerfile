FROM python:3.11.7

WORKDIR /qiandao

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 设置pip源
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple && pip install --upgrade pip

COPY requirements.txt /qiandao/requirements.txt

# 安装依赖
RUN pip install --no-cache-dir  -r ./requirements.txt


COPY qiandao /qiandao/qiandao

COPY qiandao.yaml /qiandao/qiandao.yaml

COPY ./docker-entrypoint.sh /server

ENTRYPOINT ["python", "-m", "qiandao", "--scheduled"]
