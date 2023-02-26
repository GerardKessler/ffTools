# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gera Késsler <gera.kessler@gmail.com>
# This file is covered by the GNU General Public License.
# This software uses code of FFMpeg. licensed under the LGPLv2.1

import appModuleHandler
from scriptHandler import script
import api
import globalVars
from os import path
from . import keyFunc

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode
class AppModule(appModuleHandler.AppModule):

	@script(gesture="kb:downArrow")
	def script_volumeDown(self, gesture):
		keyFunc.press_key(0x39)

	@script(gesture="kb:upArrow")
	def script_volumeUp(self, gesture):
		keyFunc.press_key(0x30)
