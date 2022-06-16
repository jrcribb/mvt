# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2022 Claudio Guarnieri.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging

from mvt.common.command import Command

from .modules.adb import ADB_MODULES

log = logging.getLogger(__name__)


class CmdAndroidCheckADB(Command):

    name = "check-adb"
    modules = ADB_MODULES

    def __init__(self, target_path=None, results_path=None, ioc_files=[],
                 module_name=None, serial=None, fast_mode=False):
        super().__init__(target_path=target_path, results_path=results_path,
                         ioc_files=ioc_files, module_name=module_name,
                         serial=serial, fast_mode=fast_mode, log=log)
