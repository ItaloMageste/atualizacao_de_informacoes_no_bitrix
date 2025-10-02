from settings import routes
from rpa.process import AtualizacaoDeInformacoesNoBitrix_Process
from utilities.ConnectionsV5 import Connections

def run():

    Connections(
        AtualizacaoDeInformacoesNoBitrix_Process,
        routes,
        "status_01",
        execute_delay=15,
        attempts=4,
        max_executions=2,
    ).run()


if __name__ == "__main__":
    print("Iniciando RPA...")
    run()
    print("Finalizando RPA...")

