#!/usr/bin/env python3
# author: @github.com/motebaya
# Copyright 2023.06.3 08:42:53 AM
# file: __logger__

import logging
# <-- logger / debug file -->
logging.addLevelName(logging.WARNING, '\033[33mWarning\033[0m')
logging.addLevelName(logging.DEBUG, '\033[32mdebug\033[0m')
logging.addLevelName(logging.INFO, '\033[36minfo\033[0m')

logging.basicConfig(
    format="\033[0m %(asctime)s %(levelname)s:%(message)s ", level=logging.DEBUG, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)