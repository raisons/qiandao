FROM python:3.11.7

WORKDIR /qiandao

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /qiandao/requirements.txt

# 安装依赖
RUN pip install --no-cache-dir  -r ./requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple

COPY qiandao /qiandao/qiandao

COPY example.qiandao.yaml /qiandao/qiandao.yaml

# 修改时区 否则报错debian可以直接设置环境变量
ENV TZ=Asia/Shanghai

ENTRYPOINT ["python", "-m", "qiandao", "--scheduled"]
