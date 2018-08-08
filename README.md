# Consulta CNPJ

Consulta de CNPJ no site da receita, quebrando o captcha, implementado em
Python.

O modelo para quebra de captcha foi criado com base no brilhante trabalho de
Daniel Falbel, Julio Trecenti, Caio Lente, Athos Damiani e todo o pessoal do
[decryptr](https://github.com/decryptr). Inclusive a base de treino usada foi
coletada por eles.

## Instalação

Antes de mais nada você precisar ter disponível
[arquivo que carrega o modelo](https://drive.google.com/file/d/1-I75klD5hnfY8TFogYJ9mLmBrF2Vg9Gw/view).

### Local

O script necessita do `curl` para rodar. No Linux Debian/Ubuntu, basta rodar:

```sh
$ sudo apt-get install curl
```

Também devem ser instaladas as dependências listadas no `requirements.txt`.

### Docker

Salve o arquivo do modelo como `captcha_receita.h5`  na raíz do projeto. Então:

```sh
$ docker build -t consulta_cnpj .
$ docker run -it --rm consulta_cnpj ipython
```
## Uso

Para usar o scraper:

```python
from consulta_cnpj import CrawlerReceita
crawler = CrawlerReceita()
print(crawler("60701190000104"))
```

Se o `captcha_receita.h5` não estiver na raíz do projeto, você pode passar a
localização dele na hora de instanciar a classe `CrawlerReceita`:

```python
crawler = CrawlerReceita("/path/to/my/models/whatever.h5")
```

O modelo que quebra o captcha está com acurácia de 75%. Mais pra frente, vou
deixá-lo rodando mais tempo para chegar a uns 95%.
