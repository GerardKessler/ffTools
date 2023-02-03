import appModuleHandler
from scriptHandler import script
import api
from os import path
from . import keyFunc

class AppModule(appModuleHandler.AppModule):
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		self.fg= None

	def event_NVDAObject_init(self, obj):
		fg= api.getForegroundObject()
		file_name= path.splitext(path.split(fg.name)[1])[0]
		fc= api.getFocusObject()
		fg.name= file_name
		fc.name= file_name
		fg.windowText= file_name

	@script(gesture="kb:downArrow")
	def script_volumeDown(self, gesture):
		keyFunc.press_key(0x39)

	@script(gesture="kb:upArrow")
	def script_volumeUp(self, gesture):
		keyFunc.press_key(0x30)

