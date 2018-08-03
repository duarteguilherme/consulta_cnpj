# Consulta CNPJ

Consulta de CNPJ no site da receita, quebrando o captcha, implementado em
Python.

O modelo para quebra de captcha foi criado com base no brilhante trabalho de
Daniel Falbel, Julio Trecenti, Caio Lente, Athos Damiani e todo o pessoal do
[decryptr](https://github.com/decryptr). Inclusive a base de treino usada foi
coletada por eles.

## Instalação


O [arquivo que carrega o modelo](https://drive.google.com/file/d/1-I75klD5hnfY8TFogYJ9mLmBrF2Vg9Gw/view)
deve estar incluído na pasta do script (tanto para rodar localmente tanto para
rodar via Docker).

### Local

O script necessita do software `curl` para rodar. No Linux Debian/Ubuntu, basta
rodar:

```sh
$ sudo apt-get install curl
```

Também devem ser instaladas as dependências listadas no `requirements.txt`.


### Docker

```sh
$ docker build -t consulta_cnpj .
$ docker run -it --rm consulta_cnpj ipython
```

## Uso

Para usar o scraper:

```python
from consulta_cnpj import crawlerReceita
x = crawlerReceita()
print(x.consulta_cnpj('60701190000104'))
```

O modelo que quebra o captcha está com acurácia de 75%. Mais pra frente, vou
deixá-lo rodando mais tempo para chegar a uns 95%.
