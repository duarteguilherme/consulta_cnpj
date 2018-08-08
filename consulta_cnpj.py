"""
In order to use this crawler, we'll not be employing requests.  Instead, we'll
be using curl through subprocess module. The reason is certificates and TLS on
government webpages in Brazil are deprecated. It's not easy to handle the
problem using requests.
"""

import time
from contextlib import ContextDecorator
from urllib.parse import urlencode
from tempfile import NamedTemporaryFile

import numpy as np
from bs4 import BeautifulSoup
from keras.models import load_model
from scipy import ndimage
from subprocess import Popen, PIPE


class Session(ContextDecorator):
    """Context manager to handle curl on terminal directly"""

    URL = "https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/{}"

    def __enter__(self):
        self.cookies = NamedTemporaryFile()
        self.curl = "curl --tlsv1.0 -ksS -b {} -c {}".format(
            self.cookies.name, self.cookies.name
        )
        self.get("cnpjreva_solicitacao.asp")
        return self

    def __exit__(self, *args):
        self.cookies.close()

    @staticmethod
    def run_process(process_str, verbose=False):
        """Run `process_str` on terminal. This function will be useful in order
        to execute `curl` on terminal."""
        if verbose:
            print(process_str)

        process = Popen(process_str.split(" "), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if not stdout:
            raise RuntimeError(
                "{}\nwhen trying to run\n\n$ {}".format(
                    stderr.decode("utf-8"), process_str
                )
            )

        return stdout

    def get(self, url):
        url = self.URL.format(url)
        return self.run_process("{} {}".format(self.curl, url))

    def post(self, url, data):
        url = self.URL.format(url)
        data = urlencode(data)
        cmd = '{} -d "{}" -H "Content-Type: application/x-www-form-urlencoded" {}'
        return self.run_process(cmd.format(self.curl, data, url))


class CrawlerReceita:
    def __init__(self, path_to_model=None):
        self.model = load_model(path_to_model or "captcha_receita.h5")
        self.classes = {
            index: char
            for index, char in enumerate("OFVRW794DQ6EM3YBJ8NGP1TX2HZIKCSAL5U")
        }

    def solve_captcha(self, session):
        """Method to download and solve the captcha using Keras."""
        image_in_bytes = session.get("captcha/gerarCaptcha.asp")
        tmp = NamedTemporaryFile(suffix=".png")
        with open(tmp.name, "wb") as fobj:
            fobj.write(image_in_bytes)

        time.sleep(1)  # this website demands a certain wait time
        data = ndimage.imread(tmp.name)
        data = data.reshape(1, 50, 180, 4)

        captcha = data.astype("float32")
        captcha /= np.max(captcha)

        prediction = self.model.predict_classes(captcha.astype("float32"))
        prediction = "".join(self.classes[x] for x in prediction.flatten())

        tmp.close()
        return prediction.lower()

    def __call__(self, cnpj):
        """Method to query a CNPJ. Input bust be a CNPJ (only numbers, no
        punctuation). It returns a dict."""
        with Session() as session:
            captcha = self.solve_captcha(session)
            data = {
                "origem": "comprovante",
                "cnpj": cnpj,
                "txtTexto_captcha_serpro_gov_br": captcha,
                "submit1": "Consultar",
                "search_type": "cnpj",
            }

            session.get("Cnpjreva_solicitacao3.asp")
            validation = session.post("valida.asp", data=data)

            html = BeautifulSoup(validation, "html.parser")
            next_link = html.find("a")["href"].strip()
            session.get(next_link)
            session.get("Cnpjreva_Vstatus.asp?origem=comprovante&cnpj={}".format(cnpj))
            session.get("Cnpjreva_Campos.asp")
            result = session.get("Cnpjreva_Comprovante.asp").decode("latin1")

            if "Cnpjreva_Erro.asp" in result:
                raise RuntimeError(
                    ("CAPTCHA probably failed. I'm afraid you'll have to try again.")
                )

            return self.parse_page(result)

    def parse_page(self, page):
        parsed = BeautifulSoup(page, "html.parser")
        cells = (
            table.find_all("td")
            for table in parsed.find_all("table", attrs={"border": 0})
        )

        data = {}
        for cell in cells:
            if len(cell.find_all("font")) < 2:
                continue
            key, *values = cell.find_all("font")
            data[key] = values[0] if len(values) == 1 else values

        return data
