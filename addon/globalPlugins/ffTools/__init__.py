# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gera Késsler <gera.kessler@gmail.com>
# This file is covered by the GNU General Public License.

import wx
from threading import Thread
import subprocess
from re import compile
from time import sleep
import os
import shutil
import zipfile
import gui
import globalPluginHandler
from urllib import request
import socket
from comtypes.client import CreateObject as COMCreate

import api
import controlTypes
from scriptHandler import script
from ui import message, browseableMessage
from tones import beep

# # código desarrollado originalmente por Alberto Buffolino para el complemento Column review
def getFilePath():
	docPath= ""
	fg= api.getForegroundObject()
	if fg.role != api.controlTypes.Role.PANE and fg.appModule.appName != "explorer":
		return None
	shell= COMCreate("shell.application")
	for window in shell.Windows():
		try:
			if window.hwnd and window.hwnd == fg.windowHandle:
				focusedItem= window.Document.FocusedItem
				break
		except:
			pass
	else:
		desktop_path= os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
		docPath= '\"' + desktop_path + '\\' + api.getDesktopObject().objectWithFocus().name + '\"'
		return None
	targetFile= focusedItem.path
	return targetFile

MAINPATH= os.path.dirname(__file__)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__()
		self.check= False
		self.switch= False
		self.percent= 0
		self.verify()

	def verify(self):
		if not os.path.isdir(os.path.join(MAINPATH, 'bin')): os.mkdir(os.path.join(MAINPATH, 'bin'))
		if os.path.isfile(os.path.join(MAINPATH, 'bin', 'ffmpeg.exe')):
			if os.path.isfile(os.path.join(MAINPATH, 'bin', 'ffplay.exe')):
				self.check= True
				return
		Thread(target= self.filesDownload, daemon= True).start()

	def __call__(self, block_num, block_size, total_size):
		readsofar= block_num * block_size
		if total_size > 0:
			percent= readsofar * 1e2 / total_size
			percent_format= int(percent*1)
			if percent_format <= (self.percent+10): return
			self.percent= percent_format
			message(f'{percent_format} porciento')

	def filesDownload(self):
		modal= wx.MessageDialog(None, _('Es necesario descargar los binarios de FFMPEG. ¿Quieres hacerlo ahora?'), _('Importante:'), wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		if modal.ShowModal() == wx.ID_YES:
			# wx.MessageDialog(None, _('Descargando los archivos. Puede seguir trabajando con su pc. Se le notificará al finalizar el proceso'), _('ffTools:'), wx.OK).ShowModal()
			url= 'https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest'
			pattern= compile(r'href=[\"\'](https://github.com/yt\-dlp/FFmpeg\-Builds/releases/download/autobuild[\d\-]+/(ffmpeg\-n[\d\w\.\-]+zip))[\"\']')
			try:
				socket.setdefaulttimeout(30) # Error si pasan 30 segundos sin internet
				try:
					content= request.urlopen(url).read().decode('utf-8')
				except:
					wx.MessageDialog(None, _('Error en la conexión. Por favor compruebe su conexión a internet y vuelva a intentarlo en unos minutos'), _('ffTools:'), wx.OK).ShowModal()
					return
			except Exception as e:
					wx.MessageDialog(None, _('Error en la conexión. Por favor compruebe su conexión a internet y vuelva a intentarlo en unos minutos'), _('ffTools:'), wx.OK).ShowModal()
					return
			result= pattern.search(content)
			url_dl= result[1]
			request.urlretrieve(result[1], os.path.join(MAINPATH, 'bin', 'ffmpeg_temp.zip'), reporthook= self.__call__)
			self.extractFiles()

	def extractFiles(self):
		zip_file= zipfile.ZipFile(os.path.join(MAINPATH, 'bin', 'ffmpeg_temp.zip'))
		root= zip_file.namelist()[0]
		zip_file.extractall(os.path.join(MAINPATH, 'bin'))
		zip_file.close()
		os.remove(os.path.join(MAINPATH, 'bin', 'ffmpeg_temp.zip'))
		shutil.move(os.path.join(MAINPATH, 'bin', root, 'bin', 'ffmpeg.exe'), os.path.join(MAINPATH, 'bin', 'ffmpeg.exe'))
		shutil.move(os.path.join(MAINPATH, 'bin', root, 'bin', 'ffplay.exe'), os.path.join(MAINPATH, 'bin', 'ffplay.exe'))
		shutil.rmtree(os.path.join(MAINPATH, 'bin', root))
		wx.MessageDialog(None, _('El proceso ha finalizado correctamente'), _('ffTools:'), wx.OK).ShowModal()

	def getScript(self, gesture):
		if not self.switch:
			return globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script= globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		if not script:
			self.finish()
			return
		return globalPluginHandler.GlobalPlugin.getScript(self, gesture)

	def finish(self):
		beep(220,10)
		self.switch= False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	@script(
		category= 'ffTools',
		# Translators: Descripción del comando en el diálogo gestos de entrada
		description= _('Activa la capa de comandos'),
		gesture= 'kb:NVDA+control+f'
	)
	def script_commandLayer(self, gesture):
		beep(880,5)
		self.bindGestures(self.__newGestures)
		self.switch= True

	def script_preview(self, gesture):
		self.finish()
		if not self.check:
			self.verify()
			return
		file_path= getFilePath()
		if file_path:
			command= f'{os.path.join(MAINPATH, "bin", "ffplay.exe")} "{file_path}"'
			newProcessing = NewProcessing(file_path)
			Thread(target= newProcessing.newProcess, args= (command, False), daemon= True).start()

	__newGestures= {
		"kb:space": "preview"
	}

class NewProcessing():

	def __init__(self, file_path):
		self.settings= subprocess.STARTUPINFO()
		self.settings.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		self.level= None

	def detect(self):
		out= self.getOut()
		self.level= self.extractValue(out)
		print(f'{"Volúmen máximo" if float(self.level) == 0.0 else f"Nivel: -{self.level}"}')

	def volume(self):
		new_level= float(self.level) + 1.0
		print(f'Aumentando el volúmen del archivo en {new_level} DB')
		self.newProcess(str(new_level))

	def getOut(self):
		command= f'ffmpeg -i "{self.file_path}" -af "volumedetect" -dn -vn -sn -f null /dev/null'
		out= subprocess.Popen(command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
		content= str(out.stderr.read())
		return content

	def newProcess(self, command, hide_console):
		# command= f'{os.path.join(MAINPATH, 'bin', 'ffmpeg.exe')} -i "{self.file_path}" -af volume= {new_level}dB:precision= fixed "{os.path.splitext(self.file_path)[0]}-f.mp3"'
		if hide_console:
			subprocess.Popen(command, startupinfo= self.settings)
		else:
			subprocess.run(command)

	def extractValue(self, content):
		pattern= compile(r'max_volume:\s+\-?(\d+\.\d+)\sdB')
		value= pattern.search(content)[1]
		return value

