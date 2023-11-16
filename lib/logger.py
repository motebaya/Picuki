#!/usr/bin/env python3
"""
Logger 
@github.com/motebaya at 2023.06.3 - 08.42AM
"""
import logging
from colorama.ansi import Fore as col

logging.addLevelName(logging.WARNING, f"{col.YELLOW}Warning{col.RESET}")
logging.addLevelName(logging.ERROR, f"{col.RED}Error{col.RESET}")
logging.addLevelName(logging.DEBUG, f"{col.GREEN}Debug{col.RESET}")
logging.addLevelName(logging.INFO, f"{col.CYAN}Info{col.RESET}")

# default verbose -> off
logging.basicConfig(
    format="\033[0m %(asctime)s %(levelname)s:%(message)s ", level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)