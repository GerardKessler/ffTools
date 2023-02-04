import appModuleHandler
from scriptHandler import script
import api
from os import path
from . import keyFunc

class AppModule(appModuleHandler.AppModule):

	@script(gesture="kb:downArrow")
	def script_volumeDown(self, gesture):
		keyFunc.press_key(0x39)

	@script(gesture="kb:upArrow")
	def script_volumeUp(self, gesture):
		keyFunc.press_key(0x30)

