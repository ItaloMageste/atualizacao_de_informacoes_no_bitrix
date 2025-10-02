import os
import re
import json
import math
import logging
import pandas as pd
from pathlib import Path
from rpa.page import AtualizacaoDeInformacoesNoBitrix_Page
from utilities.common.Portal import PortalBWA
from utilities.common.files import get_file_by_partial_name
from utilities.common.portalApi import login_on_portal, login_on_portal

from settings import NOME_PLANILHA


bwa = PortalBWA()
bx_company_att = AtualizacaoDeInformacoesNoBitrix_Page()

token = login_on_portal()

def le_planilha_companys(nome_arquivo, tabela = None):

    path = Path.cwd() / 'tabela'

    arquivo_path = get_file_by_partial_name(path, nome_arquivo)

    if not tabela:

        if '.xlsx' in nome_arquivo:
            df = pd.read_excel(arquivo_path)

        elif '.csv' in nome_arquivo:
            # df = pd.read_csv(arquivo_path, sep = ';', encoding='latin-1')
            df = pd.read_csv(arquivo_path, sep = ';')

    else:

        if '.xlsx' in nome_arquivo:
            df = pd.read_excel(arquivo_path, sheet_name = tabela)

        elif '.csv' in nome_arquivo:
            df = pd.read_csv(arquivo_path, sheet_name = tabela, sep = ';', encoding='latin-1')

    return df

def verificar_e_criar_execucao(empresa, token):

    def _limpar_valores_json(dados: dict) -> dict:

        novo_dados = {}
        for chave, valor in dados.items():
            if isinstance(valor, float) and math.isnan(valor):
                novo_dados[chave] = None
            else:
                novo_dados[chave] = valor
        return novo_dados
    
    def _criar_execucao(empresa):
        
        # if not empresa['CNPJ']:
        #     logging.info(f'[PortalBWA] Execução NÃO criada para a empresa de ID {empresa["ID"]} | CNPJ VAZIO NA PLANILHA')
        #     print(f'[PortalBWA] Execução NÃO criada para a empresa de ID {empresa["ID"]} | CNPJ VAZIO NA PLANILHA')       
        #     return

        if not empresa['ID']:
            print(f'[PortalBWA] Execução NÃO criada - Empresa sem ID na planilha!!')
            return

        id_planilha = int(empresa['ID'])

        bwa.create_execution(
            robo_id = 144,
            status_01 = "4",
            colunas = json.dumps(
                _limpar_valores_json(
                    {
                        "coluna_01": id_planilha,
                    }
                ),
            )
        )

        logging.info(f'[PortalBWA] Execução criada para a empresa de ID {empresa["ID"]} - {NOME_PLANILHA}')
        print(f'[PortalBWA] Execução criada para a empresa de ID {empresa["ID"]} - {NOME_PLANILHA}')       
    
    _criar_execucao(empresa)

if __name__ == "__main__":

    os.system('cls')

    bwa = PortalBWA()
    bx_company_att = AtualizacaoDeInformacoesNoBitrix_Page()

    token = login_on_portal()
    empresas = []

    df = le_planilha_companys(NOME_PLANILHA)
    df = df.where(pd.notna(df), None)
    df = df.applymap(lambda x: '' if pd.isna(x) else x)

    for index, empresa in df.iterrows():

        verificar_e_criar_execucao(empresa, token)