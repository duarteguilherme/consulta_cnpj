FROM gw000/keras:1.2.1-py3
WORKDIR /cnpj

COPY requirements.txt requirements.txt
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install -r requirements.txt

COPY captcha_receita.h5 captcha_receita.h5
COPY consulta_cnpj.py consulta_cnpj.py
