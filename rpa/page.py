import re
import json
import requests
import unicodedata
import pandas as pd
from time import sleep
from datetime import datetime, date
from utilities.settings import BITRIX_WEBHOOK
from utilities.common.exceptions import ClientExecutionException

class AtualizacaoDeInformacoesNoBitrix_Page:

    def de_para_nome_colunas_planilha_to_api(self, item):

        colunas_nomes = {
            'Tipo da empresa': "Tipo de empresa", # planilha para api
            'Comentário': "Observação",
        }

        return colunas_nomes.get(item, item)

    def de_para_nome_colunas_api_to_planilha(self, item):

        colunas_nomes = {
            'Tipo de empresa': "Tipo da empresa", # api para planilha
             "Observação": 'Comentário',
        }

        return colunas_nomes.get(item, item)

    def consultar_campos_no_bitrix(self, tipo_do_campo, lista_colunas):

        '''
        tipo_do_campo:
            Company
            Deal
        lista_colunas:
            - lista com todas as colunas que serão consultadas no Bitrix. O nome deve ser EXATAMENTE igual ao nome da coluna exibida no B24.
        '''

        def _obter_deal_fields():

            try:
                print('Consultando os campos dos cards de negócios no Bitrix')
                response = requests.post(BITRIX_WEBHOOK + "crm.deal.fields")
                if response.status_code == 200:
                    return response.json()['result']
            except Exception as error:
                raise Exception(f"[Erro] ao obter os campos dos cards de negócios no Bitrix")
            
        def _obter_company_fields():

            try:
                print('Consultando os campos de empresas no Bitrix')
                response = requests.post(BITRIX_WEBHOOK + "crm.company.fields")
                if response.status_code == 200:
                    return response.json()['result']
            except Exception as error:
                raise Exception(f"Erro ao obter os campos de empresas no Bitrix'")

        def _get_company_list(cliente_ativo = True):

            lista_de_empresas = []
            start = 0

            while True:

                if cliente_ativo:

                    headers = {"Content-Type": "application/json"}
                    params = {
                        "start": start,
                        "filter": {"UF_CRM_1715878731": "24101"}, # Empresas ativas
                    }
                    response = requests.post(BITRIX_WEBHOOK + "crm.company.list", json = params, headers = headers) 

                else:
                    response = requests.post(BITRIX_WEBHOOK + "crm.company.list")
                
                data = response.json()

                if response.status_code == 200:
                    lista_de_empresas.extend(data['result'])

                    if "next" in data and isinstance(data['next'], int):
                        start = data["next"]
                        print(start)
                    else:
                        return lista_de_empresas
                    
        if tipo_do_campo == 'Company':
            campos = _obter_company_fields()

        if tipo_do_campo == 'Deal':
            campos = _obter_deal_fields()

        campos_para_atualizar = []
        nao_encontrados = []

        for item in lista_colunas:
            
            item = self.de_para_nome_colunas_planilha_to_api(item)
            
            encontrado = False

            for nome_campo, chaves_internas_campo in campos.items():

                if item.upper() == (chaves_internas_campo.get('title', '')).upper():
                    campos_para_atualizar.append({
                        'nome_do_campo': item,
                        'tipo_de_dado': chaves_internas_campo['type'],
                        'id_do_campo': nome_campo,
                    })
                    encontrado = True
                    break

                elif item.upper() == chaves_internas_campo.get('listLabel', '').upper():
                    campos_para_atualizar.append({
                        'nome_do_campo': item,
                        'tipo_de_dado': chaves_internas_campo['type'],
                        'id_do_campo': nome_campo,
                    })
                    encontrado = True
                    break

                elif item.upper() == chaves_internas_campo.get('formLabel', '').upper():
                    campos_para_atualizar.append({
                        'nome_do_campo': item,
                        'tipo_de_dado': chaves_internas_campo['type'],
                        'id_do_campo': nome_campo,
                    })
                    encontrado = True
                    break

                elif item.upper() == chaves_internas_campo.get('filterLabel', '').upper():
                    campos_para_atualizar.append({
                        'nome_do_campo': item,
                        'tipo_de_dado': chaves_internas_campo['type'],
                        'id_do_campo': nome_campo,
                    })
                    encontrado = True
                    break

            if not encontrado:
                nao_encontrados.append(item)

        return campos_para_atualizar
    
    def atualizar_campos_bitrix(self, id_card, campos, tipo_card):

        def _normalizar_string(texto):

            if not isinstance(texto, str):
                texto = str(texto)
            texto = texto.strip()
            texto = unicodedata.normalize('NFKD', texto)
            texto = texto.encode('ASCII', 'ignore').decode('ASCII')
            texto = re.sub(r'\s+', ' ', texto)
            return texto.upper()

        def _buscar_ids_selecionaveis(id_do_campo, dado, tipo_card):

            url = BITRIX_WEBHOOK + "crm.company.fields"
            try:

                response = requests.post(url)

                if response.status_code != 200:
                    raise ValueError('Erro na consulta de campos das empresas')
                
                campos = response.json().get('result', None)
                campo_selecionado = campos[id_do_campo]

                ids = campo_selecionado.get('items', None)
                for id in ids:
                    if _normalizar_string(dado) == _normalizar_string(id['VALUE']):
                        return id['ID']
                    
           
            except Exception as e:
                raise Exception(f"Erro ao atualizar o {tipo_card} Card: {e}")

        def _buscar_usuario_por_nome(nome):

            url = BITRIX_WEBHOOK + "user.get"
            
            payload = {
                "filter": {
                    "NAME_SEARCH": nome
                }
            }

            response = requests.post(
                url = url,
                json = payload
            )
            result = response.json().get("result", [])

            if not result and len(nome.split()) > 2:

                nome = nome.split()[0] + ' ' + nome.split()[1] 
                payload = {
                "filter": {
                    "NAME_SEARCH": nome
                    }
                }

                response = requests.post(
                    url = url,
                    json = payload
                )
                result = response.json().get("result", [])

            if len(result) < 1:
                return [ ]
            
            return int(result[0].get('ID', None))
        
        def _buscar_contato_por_nome(nome):

            url = BITRIX_WEBHOOK + "crm.contact.list"

            nome_completo = nome.replace('[c]','').replace('[C]','').strip()
            partes = nome_completo.split()

            payload = {
                "filter": {
                    "=NAME": partes[0],
                    "=LAST_NAME": " ".join(partes[1:])
                },
                "select": ["ID", "NAME", "LAST_NAME", "EMAIL"]
            }

            response = requests.post(
                url = url,
                json = payload
            )

            result = response.json().get("result", [])
            if result:
                return int(result[0]['ID'])
            else:
                raise ValueError('ID do contato não encontrado')
        
        def _validar_dado(id_do_campo, tipo_do_campo, dado, tipo_card):
            
            if not dado:
                return None

            try:
                if tipo_do_campo == 'string':

                    if id_do_campo == 'UF_CRM_1734547962' and str(dado).endswith('.0'):
                        dado = str(dado).replace('.0','')
                    return str(dado)
                
                elif tipo_do_campo == 'integer':
                    return int(dado)

                elif tipo_do_campo == 'double':
                    return float(str(dado).replace('.', '').replace(',', '.'))

                elif tipo_do_campo == 'boolean':
                    if isinstance(dado, bool):
                        return dado
                    if str(dado).lower() in ['true', '1', 'sim', 'y']:
                        return True
                    elif str(dado).lower() in ['false', '0', 'não', 'nao']:
                        return False
                    raise ValueError("Valor booleano inválido")

                elif tipo_do_campo == 'char':
                    return str(dado)[0] if dado else None

                elif tipo_do_campo == 'date':
                    if isinstance(dado, (datetime, pd.Timestamp)):
                        return dado.date().isoformat()

                    elif isinstance(dado, date):
                        return dado.isoformat()

                    elif isinstance(dado, str) and dado.strip():
                        dado = dado.strip().replace('/', '-')

                        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                            try:
                                return datetime.strptime(dado, fmt).date().strftime("%d-%m-%Y")
                            except ValueError:
                                continue

                elif tipo_do_campo == 'datetime':
                    if isinstance(dado, str) and dado != '':
                        dado = dado.replace('/','-')
                        return datetime.strptime(dado, "%d-%m-%Y").date().isoformat()
                    elif isinstance(dado, datetime):
                        return dado.isoformat()
                    return datetime.strptime(dado, "%Y-%m-%d %H:%M:%S").isoformat()

                elif tipo_do_campo in ['crm_status', 'enumeration', 'crm_currency', 'user', 'employee', 'crm']:
                    
                    if tipo_do_campo == 'crm_status':
                        pass

                    elif tipo_do_campo == 'enumeration':
                        dado = _buscar_ids_selecionaveis(id_do_campo, dado, tipo_card)
                    
                    elif tipo_do_campo == 'crm_currency': # TODO Implementar busca de currency (moedas)
                        pass

                    elif tipo_do_campo == 'user' or tipo_do_campo == 'employee':
                        dado = _buscar_usuario_por_nome(dado)

                    elif tipo_do_campo == 'crm':
                        dado = _buscar_contato_por_nome(dado)

                    return int(dado) if str(dado).isdigit() else str(dado)

                elif tipo_do_campo == 'file':
                    return str(dado)

                elif tipo_do_campo == 'url':
                    # if str(dado).startswith('http'):
                    #     return str(dado)                    
                    if isinstance(dado, str):
                        return str(dado)
                    else:
                        return ValueError("URL inválida")

                else:
                    raise ValueError(f"Tipo de dado não reconhecido: {tipo_do_campo}")
            
            except Exception as e:
                raise ValueError(f"[{id_do_campo}] Erro ao validar '{dado}': {e}")

        def _conferir_se_campo_foi_atualizado_corretamente(payload, campo_id, card_id):

            print('Conferindo se o dado foi atualizado corretamente no Bitrix!')
            
            url = "https://bwa.bitrix24.com.br/rest/2072/csqxphcxktu5ujiu/crm.company.get"
            params = {"id": card_id}

            while True:
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()

                    result = response.json().get('result', None)
                    if not result:
                        raise KeyError('Result não encontrado no company get')
                    break
                except (KeyError, requests.RequestException) as error:
                    print(f'ERRO na consulta do card {card_id}: {error}')
                    sleep(2)
                    continue

            dado_no_bitrix = result[campo_id]
            dado_atualizacao = payload['fields'][campo_id]

            dado_no_bitrix = str(dado_no_bitrix)
            dado_atualizacao = str(dado_atualizacao)

            if not dado_atualizacao or dado_atualizacao == '0' or dado_atualizacao == 0 or dado_atualizacao == 'false' or dado_atualizacao == 'False':
                if dado_no_bitrix == '0' or  dado_no_bitrix == 0 or dado_no_bitrix == 'false' or dado_no_bitrix == 'False' or dado_no_bitrix == False:
                    print('Dado atualizado com sucesso!')
                    return True
                
            elif dado_atualizacao:
                if dado_no_bitrix == '1' or  dado_no_bitrix == 1 or dado_no_bitrix == 'true' or dado_no_bitrix == 'True' or dado_no_bitrix == True:
                    print('Dado atualizado com sucesso!')
                    return True
                
            if dado_no_bitrix == dado_atualizacao:
                print('Dado atualizado com sucesso!')
                return True
            return False

        payload = {
            "id": id_card,
            "fields": {}
        }

        for dado in campos:

            if dado['nome_do_campo'] == 'ID':
                continue
            elif dado['nome_do_campo'] == 'CNPJ':
                continue

            dado_validado = _validar_dado(dado['id_do_campo'], dado['tipo_de_dado'], dado['dado_para_atualizar'], tipo_card)
            if not dado_validado:
                continue
            payload['fields'][dado['id_do_campo']] = dado_validado

        if tipo_card == 'Company':
            url = BITRIX_WEBHOOK + "crm.company.update"

        if tipo_card == 'Deal':
            url = BITRIX_WEBHOOK + "crm.deal.update"        

        while True:
        
            response = requests.post(url, json = payload).json()
            
            error = response.get('error')
            result = response.get('result')
            error_description = response.get('error_description')

            if error_description == 'Company is not found':
                with open("EmpresasNaoEcontradas.txt", "a", encoding="utf-8") as arquivo:
                    arquivo.write("======================================================" + "\n")
                    arquivo.write(f'Erro na empresa de ID {id_card}: {error_description}' + "\n")
                    arquivo.write(f'Payload utilizado:' + "\n")
                    arquivo.write(json.dumps(payload, indent=2, ensure_ascii=False))
                    arquivo.write("\n")
                raise ClientExecutionException('Empresa nao encontrada no Bitrix!', success = False)

            if error == 'QUERY_LIMIT_EXCEEDED':
                print("Limite de requisições excedido. Aguardando 5 segundos...")
                sleep(5)
                continue

            if error:
                sleep(5)
                print(error)
                continue

            if not result:
                sleep(5)
                print(response.json())
                continue
            
            print(f'{tipo_card} Card {id_card} atualizado com os novos valores!')
        
            # TODO Corrigir a conferencia da atualização
            # if not _conferir_se_campo_foi_atualizado_corretamente(payload, dado['id_do_campo'], id_card):
            #     print('O Campo não foi atualizado corretamente, tentando novamente!')
            #     continue

            break
        print('')