import logging
from datetime import datetime
from pathlib import Path
import pyperclip
import pandas as pd

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.remote.webelement import WebElement


class BotNamePage(BotBase):
    pass
