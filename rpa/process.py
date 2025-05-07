import pandas as pd
from pathlib import Path
from rpa.page import AtualizacaoDeInformacoesNoBitrix_Page


class AtualizacaoDeInformacoesNoBitrix_Process(AtualizacaoDeInformacoesNoBitrix_Page):
    DEPARTMENT = "CONTABIL"
    BOT_DIRECTORY_NAME = "ANALISE_BALANCETES"
    NOTIFY_AT_BEGINNING  = False

    def prepare(self, client: dict[str,str]) -> None:
        ...

    def execute(self, client: dict[str,str]) -> None:
        
        card_id = int(client.CARD_ID)

        path_csv = Path(Path.cwd()/'tabela'/'company (2) copy.csv')
        df_csv = pd.read_csv(path_csv, sep = ';')
        nomes_colunas = list(df_csv.columns)

        colunas_company = self.consultar_campos_no_bitrix('Company', nomes_colunas)

        df_filtrado_por_id = df_csv[df_csv['ID'] == card_id].fillna('')
        
        for coluna in colunas_company:
            
            if coluna['nome_do_campo'] == 'ID':
                continue
            elif coluna['nome_do_campo'] == 'CNPJ':
                continue

            if not df_filtrado_por_id.empty:
                dado_att = df_filtrado_por_id.iloc[0][self.de_para_nome_colunas_api_to_planilha(coluna['nome_do_campo'])]
                if not dado_att:     
                    continue
            else:
                continue            

            self.atualizar_campo_bitrix(
                id_card =           '39989',                # TODO REMOVER
                # id_card =           client.CARD_ID,       # TODO DESCOMENTAR
                id_do_campo =       coluna['id_do_campo'],
                tipo_do_campo =     coluna['tipo_de_dado'],
                dado =              dado_att,
                tipo_card =         'Company'
            )
    

    def __str__(self) -> str:
        return self.BOT_DIRECTORY_NAME
