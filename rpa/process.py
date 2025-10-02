import pandas as pd
from time import sleep
from pathlib import Path
from utilities.settings import DOWNLOADS_DIR
from utilities.common.files import clean_directory
from rpa.page import AtualizacaoDeInformacoesNoBitrix_Page
from utilities.common.portalApi import download_execution_files, login_on_portal

from settings import NOME_PLANILHA

class AtualizacaoDeInformacoesNoBitrix_Process(AtualizacaoDeInformacoesNoBitrix_Page):

    DEPARTMENT = "CONTABIL"
    BOT_DIRECTORY_NAME = "ANALISE_BALANCETES"
    NOTIFY_AT_BEGINNING  = False

    def prepare(self, client: dict[str,str]) -> None:
        ...

    def execute(self, client: dict[str,str]) -> None:

        token = login_on_portal()
        clean_directory(DOWNLOADS_DIR, [".gitkeep"])
        download_execution_files(token, client.id_execucao, "input", DOWNLOADS_DIR, extract_files=True)
        
        nome_arquivo = NOME_PLANILHA

        path_csv = Path(Path.cwd()/'tabela'/ nome_arquivo) # TODO Remover antes de finalmente entregar o RPA
        
        card_id = int(client.CARD_ID)

        if '.csv' in nome_arquivo:
            df = pd.read_csv(path_csv, sep = ';')
        
        elif '.xlsx' in nome_arquivo:
            df = pd.read_excel(path_csv)

        nomes_colunas = list(df.columns)

        if 'Nome da Empresa' in nomes_colunas:
            tipo_planilha = 'Company'
        elif 'Nome do negócio' in nomes_colunas:
            tipo_planilha = 'Deal'
        else:
            # raise ValueError('Não foi possível verificar se a planilha é de Empresas ou de Negócios!')
            tipo_planilha = 'Company'

        colunas_company = self.consultar_campos_no_bitrix(tipo_planilha, nomes_colunas)

        df_filtrado_por_id = df[df['ID'] == card_id].fillna('')

        for coluna in colunas_company:

            coluna["dado_para_atualizar"] = None

            if coluna['nome_do_campo'] == 'ID':
                continue
            elif coluna['nome_do_campo'] == 'CNPJ':
                continue

            if not df_filtrado_por_id.empty:
                dado_att = df_filtrado_por_id.iloc[0][self.de_para_nome_colunas_api_to_planilha(coluna['nome_do_campo'])]
                if not dado_att:     
                    continue
                coluna["dado_para_atualizar"] = dado_att
        
        self.atualizar_campos_bitrix(
            id_card =           client.CARD_ID,
            campos =            colunas_company,
            tipo_card =         tipo_planilha
        )
        print(f'Dados da planilha: {NOME_PLANILHA}')
        print('[AVISO] Fim da execução')
    
    def __str__(self) -> str:
        return self.BOT_DIRECTORY_NAME
