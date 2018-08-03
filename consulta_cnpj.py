from tempfile import NamedTemporaryFile
import sys
from bs4 import BeautifulSoup
import tensorflow as tf
from keras.models import load_model, Sequential, Model # basic class for specifying and training a neural network
from keras.layers import Reshape,Input, Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from keras.utils import np_utils # utilities for one-hot encoding of ground truth values
from scipy import ndimage
import numpy as np
import json
import ssl
from subprocess import Popen, PIPE
import time


# In order to use this crawler, we'll not be employing requests
# Instead, we'll be using curl through subprocess module
# The reason is certificates and TSL on government webpages in Brazil are deprecated
# It's not easy to handle the problem using requests


# Funcoes relativas ao modelo que quebra o captcha do tse
def carrega_modelo():
    """ Load 'CNPJ' model
    """
    model = load_model('captcha_receita.h5')
    return model

model = carrega_modelo()
classes = dict(zip(list(range(35)), ['O', 'F', 'V', 'R', 'W', '7', '9', '4', 'D', 'Q', '6', 'E', 'M', '3', 'Y', 'B', 'J', '8', 'N', 'G', 'P', '1', 'T', 'X', '2', 'H', 'Z', 'I', 'K', 'C', 'S', 'A', 'L', '5', 'U']))
num_classes = len(classes)

def quebra_captcha(captcha):
    captcha = captcha.astype('float32')
    captcha /= np.max(captcha)
    prediction = model.predict_classes(captcha.astype('float32')) 
    return(prediction)


def run_process(process_str, verbose=False):
    """ Run 'process_str' on terminal
    This function will be useful in order to execute curl on terminal
    """
    if verbose:
        print(process_stf)
    process = Popen(process_str.split(' '),stdout = PIPE, stderr = PIPE) 
    stdout, stderr = process.communicate()
    if not stdout:
        raise RuntimeError(stderr)
    return(stdout)






class Session:
    """ Class created in order to handle curl on terminal directly
    """
    def __init__(self):
        open("cookiefile", "w")

    def get(self, url):
        pagina = run_process("curl --tlsv1.0 -k -b cookiefile -c cookiefile " + url)
        return pagina

    def post(self, url, data):
        data = '&'.join([ key + '=' + str(data[key]) for key in data.keys() ])
        pagina = run_process('curl -d "' + data + '" -H "Content-Type: application/x-www-form-urlencoded" --tlsv1.0 -k -b cookiefile -c cookiefile ' + url)
        return pagina





class crawlerReceita:
    def __init__(self):
        self.sessao = Session()
        pagina = self.sessao.get("https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/cnpjreva_solicitacao.asp")
        
    def baixa_captcha(self):
        """ Este metodo baixa captcha da receita
        e já quebra usando modelo feito em keras
        """
        url = "https://www.receita.fazenda.gov.br/PessoaJuridica/CNPJ/cnpjreva/captcha/gerarCaptcha.asp"
        pagina = self.sessao.get(url)
        tmp = NamedTemporaryFile(suffix='.png')

        with open(tmp.name, 'wb') as fobj:
            fobj.write(pagina)

        imagem_data = (ndimage.imread(tmp.name))

        # Site da receita exige tempo de espera
        time.sleep(1)

        imagem_data = imagem_data.reshape(1,50,180,4)
        predicao = quebra_captcha(imagem_data).flatten()
        predicao = ''.join([ classes[x] for x in predicao ]).lower()
        tmp.close()
        return(predicao)

    def consulta_cnpj(self, cnpj):
        """ Método para consulta de cnpj,
        Basta inserir cnpj sem traço ou ponto e
        ele retorna um dicionario com os dados
        """
        captcha = self.baixa_captcha()
        dados_post = {
                "origem":"comprovante",
                "cnpj":"01109184000195",
                "txtTexto_captcha_serpro_gov_br":captcha,
                "submit1":"Consultar",
                "search_type":"cnpj"
        }

        # 1)
        self.sessao.get("https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/Cnpjreva_solicitacao3.asp")

        # 2) Post
        pagina_validacao = self.sessao.post('https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/valida.asp', data = dados_post)
        link_dados  = 'https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/' + BeautifulSoup(pagina_validacao, "html.parser").find('a')['href'].strip()
        proxima_pagina = self.sessao.get(link_dados)

        # 3)
        self.sessao.get('https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/Cnpjreva_Vstatus.asp?origem=comprovante&cnpj=' + cnpj)

        # 4)
        self.sessao.get('https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/Cnpjreva_Campos.asp')

        # 5)
        pagina = self.sessao.get('https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/Cnpjreva_Comprovante.asp') 
        if "Cnpjreva_Erro.asp" in pagina.decode('latin1'):
            raise Exception('Erro na continuidade. Provavelmente modelo não acertou captcha. Tente novamente')
        else:
            return self.parse_page(pagina.decode('latin1'))

    def parse_page(self, page):
        """ Limpa a página recebida e retorna dados
        """
        parsed_page = BeautifulSoup(page, "html.parser")

        # This part could be implemented with dict comprehension
        # It was written with for and ifs for readability
        tabelas = parsed_page.find_all('table',attrs={'border':0})
        tds = []
        for i in tabelas:
            tds += i.find_all('td')
        dados = { }
        for i in tds:
            if len(i.find_all('font')) >= 2:
                dados[i.find_all('font')[0].text.strip()] = '#'.join(
                        [j.text.strip() for j in i.find_all('font')[1:] ]
                            )
        return dados




































