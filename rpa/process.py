import logging

from rpa.page import BotNamePage
from utilities.bitrix import Bitrix
from utilities.bot_setup import LogInfoConfig
from utilities.common.exceptions import ClientExecutionException


class BotNameProcess(BotNamePage):
    DEPARTMENT = "CONTABIL"
    BOT_DIRECTORY_NAME = "ANALISE_BALANCETES"
    NOTIFY_AT_BEGINNING  = False

    def prepare(self, client: dict[str,str]) -> None:
        ...

    def execute(self, client: dict[str,str]) -> None:
        ...

    def teardown(self) -> None:
        self.driver.quit()

    def __str__(self) -> str:
        return self.BOT_DIRECTORY_NAME
