from decouple import config

PORTAL_BASE_URL = config("PORTAL_BASE_URL")
PORTAL_USERNAME = config("PORTAL_USERNAME")
PORTAL_PASSWORD = config("PORTAL_PASSWORD")
BOT_NAME = config("BOT_NAME")
APP_EXECUTAVEL = config("APP_EXECUTAVEL")
WROBO_DEPENDENT = config("WROBO_DEPENDENT")
CLIENTS_BASE_DIR =  config("CLIENTS_BASE_DIR")
BASE = config("BASE")
BASE_FILTER = "1" if config("BASE") == "NATAL" else "2"
STATUS = config("STATUS")
PAGINATE = config("PAGINATE")
EXTRA_COLS = {
    'CARD_ID': 0
}
DESENVOLVIMENTO = config("DESENVOLVIMENTO")

UNICO_USER = config("USUARIO_UNICO")
UNICO_PASSWORD = config("SENHA_UNICO")

routes = f"nome_do_robo={BOT_NAME}&status_0{STATUS}=4&paginate={PAGINATE}&base={BASE_FILTER}"

WAIT_TIMES = {
    "VERY_SHORT": 5,
    "SHORT": 15,
    "MID": 45,
    "LONG": 90,
    "VERY_LONG": 180,
}
