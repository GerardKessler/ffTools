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

# url de descarga de los archivos ffmpeg
DL_URL= 'https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest'
# Ruta del complemento
MAINPATH= os.path.dirname(__file__)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__()
		self.check= False
		self.switch= False
		self.percent= 0
		self.ffplay_file= os.path.join(MAINPATH, 'bin', 'ffplay.exe')
		self.ffmpeg_file= os.path.join(MAINPATH, 'bin', 'ffmpeg.exe')
		self.ffprobe_file= os.path.join(MAINPATH, 'bin', 'ffprobe.exe')
		self.verify()
		self.volume_bar= 0
		self.format_list= [".mp3", ".ogg", ".flac", ".wav", ".m4a", ".flv", ".mkv", ".avi", ".mp4"]

	def verify(self):
		if os.path.isdir(os.path.join(MAINPATH, 'bin')):
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
			pattern= compile(r'href=[\"\'](https://github.com/yt\-dlp/FFmpeg\-Builds/releases/download/autobuild[\d\-]+/(ffmpeg\-n[\d\w\.\-]+zip))[\"\']')
			try:
				socket.setdefaulttimeout(30) # Error si pasan 30 segundos sin internet
				try:
					content= request.urlopen(DL_URL).read().decode('utf-8')
				except:
					wx.MessageDialog(None, _('Error en la conexión. Por favor compruebe su conexión a internet y vuelva a intentarlo en unos minutos'), _('ffTools:'), wx.OK).ShowModal()
					return
			except Exception as e:
					wx.MessageDialog(None, _('Error en la conexión. Por favor compruebe su conexión a internet y vuelva a intentarlo en unos minutos'), _('ffTools:'), wx.OK).ShowModal()
					return
			result= pattern.search(content)
			url_dl= result[1]
			request.urlretrieve(result[1], os.path.join(MAINPATH, 'ffmpeg_temp.zip'), reporthook= self.__call__)
			self.extractFiles()

	def extractFiles(self):
		zip_file= zipfile.ZipFile(os.path.join(MAINPATH, 'ffmpeg_temp.zip'))
		root= zip_file.namelist()[0]
		zip_file.extractall(MAINPATH)
		zip_file.close()
		os.remove(os.path.join(MAINPATH, 'ffmpeg_temp.zip'))
		shutil.move(os.path.join(MAINPATH, root, 'bin'), MAINPATH)
		shutil.rmtree(os.path.join(MAINPATH, root))
		wx.MessageDialog(None, _('El proceso ha finalizado correctamente'), _('ffTools:'), wx.OK).ShowModal()

	def getScript(self, gesture):
		if not self.switch:
			return globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script= globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		if not script:
			self.finish()
			return
		return globalPluginHandler.GlobalPlugin.getScript(self, gesture)

	def finish(self, sound= True):
		if sound: beep(220,10)
		self.switch= False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	@script(
		category= 'ffTools',
		# Translators: Descripción del comando en el diálogo gestos de entrada
		description= _('Activa la capa de comandos'),
		gesture= 'kb:NVDA+shift+f'
	)
	def script_commandLayer(self, gesture):
		beep(880,5)
		self.bindGestures(self.__newGestures)
		self.switch= True

	def script_preview(self, gesture):
		self.finish(False)
		if not self.check:
			self.verify()
			return
		file_path= getFilePath()
		if file_path:
			command= f'{self.ffplay_file} "{file_path}" -window_title {os.path.splitext(os.path.split(file_path)[1])[0]}'
			newProcessing= NewProcessing(command, None, file_path, False)
			Thread(target=newProcessing.newProcess, daemon= True).start()

	@script(gesture="kb:NVDA+shift+w")
	def script_extract(self, gesture):
		self.finish(False)
		if not self.check:
			self.verify()
			return
		file_path= getFilePath()
		if file_path:
			newProcessing= NewProcessing(None, self.ffprobe_file, file_path, False)
			Thread(target=newProcessing.extractTime, args=(self.ffmpeg_file, 'beginning', '03:00'), daemon= True).start()

	def script_volumeDetect(self, gesture):
		self.finish(False)
		if not self.check:
			self.verify()
			return
		file_path= getFilePath()
		if file_path:
			newProcessing = NewProcessing(None, self.ffmpeg_file, file_path, False)
			Thread(target= newProcessing.detect, daemon= True).start()

	def script_formatChange(self, gesture):
		self.bindGestures(self.__formatGestures)
		self.switch= True
		message("selecciona el formato con flechas arriba y abajo y pulsa intro")

	def script_volumeChange(self, gesture):
		self.bindGestures(self.__volumeGestures)
		self.switch= True
		message("selecciona el volúmen con flechas arriba y abajo y pulsa intro")

	def script_upVolume(self, gesture):
		self.volume_bar+=0.5
		message(str(self.volume_bar))

	def script_downVolume(self, gesture):
		self.volume_bar -= 0.5
		message(str(self.volume_bar))

	def script_downFormat(self, gesture):
		self.volume_bar-=1
		if self.volume_bar >= 0:
			message(self.format_list[self.volume_bar])
		else:
			self.volume_bar= len(self.format_list)-1
			message(self.format_list[self.volume_bar])

	def script_upFormat(self, gesture):
		self.volume_bar+=1
		if self.volume_bar < len(self.format_list):
			message(self.format_list[self.volume_bar])
		else:
			self.volume_bar= 0
			message(self.format_list[self.volume_bar])

	def script_sendVolume(self, gesture):
		self.finish(False)
		if not self.check:
			self.verify()
			return
		file_path= getFilePath()
		if file_path:
			newProcessing = NewProcessing(None, self.ffmpeg_file, file_path, True)
			Thread(target=newProcessing.volumeChange, args=(self.volume_bar,), daemon= True).start()
			self.volume_bar= 0

	def script_sendFormat(self, gesture):
		self.finish(False)
		if not self.check:
			self.verify()
			return
		file_path= getFilePath()
		if file_path:
			if self.format_list[self.volume_bar] == os.path.splitext(file_path)[1]:
				message('Proceso cancelado. Los formatos de entrada y salida son iguales:)')
				return
			command= f'{self.ffmpeg_file} -i "{file_path}" "{os.path.splitext(file_path)[0]}{self.format_list[self.volume_bar]}"'
			newProcessing = NewProcessing(command, self.ffmpeg_file, file_path, True)
			Thread(target=newProcessing.formatChange, daemon= True).start()
			message(f'Cambiando el formato de {os.path.splitext(file_path)[1]} a {self.format_list[self.volume_bar]}')
			self.volume_bar= 0

	def script_close(self, gesture):
		self.finish()
		message('Cancelado')

	__newGestures= {
		"kb:space": "preview",
		"kb:d": "volumeDetect",
		"kb:f": "formatChange",
		"kb:v": "volumeChange"
	}

	__volumeGestures= {
		"kb:upArrow":"upVolume",
		"kb:downArrow":"downVolume",
		"kb:escape":"close",
		"kb:enter":"sendVolume"
	}

	__formatGestures= {
		"kb:upArrow":"upFormat",
		"kb:downArrow":"downFormat",
		"kb:escape":"close",
		"kb:enter":"sendFormat"
	}

class NewProcessing():

	def __init__(self, command, executable_path, file_path, hide_console):
		self.command= command
		self.executable_path= executable_path
		self.file_path= file_path
		self.hide_console= hide_console
		self.settings= subprocess.STARTUPINFO()
		self.settings.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		self.no_settings= subprocess.STARTUPINFO()
		self.levels= None

	def detect(self):
		out= self.getOut()
		if out:
			self.levels= self.extractValue(out)
			wx.MessageDialog(None, f'Pico máximo: -{self.levels[1]}\n Nivel medio: -{self.levels[0]}', _('Resultado:'), wx.OK).ShowModal()
		else:
			message("Se ha producido un error")

	def getOut(self):
		command= f'{self.executable_path} -i "{self.file_path}" -af "volumedetect" -dn -vn -sn -f null /dev/null'
		try:
			out= subprocess.Popen(command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
		except OSError:
			out= subprocess.Popen('taskkill /f /im cmd.exe', stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
			out= subprocess.Popen(command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
		content= str(out.stderr.read())
		return content

	def volumeChange(self, value):
		message(f'Modificando el volúmen del archivo en {value} DB')
		self.newProcess(value)

	def newProcess(self, value= None):
		file_path= os.path.splitext(self.file_path)
		command= f'{self.executable_path} -i "{self.file_path}" -af "volume={value}dB" "{file_path[0]}-x{file_path[1]}"'
		if self.hide_console:
			execute= subprocess.Popen(command, startupinfo= self.settings)
			execute.wait()
			wx.MessageDialog(None, _('Proceso finalizado'), _('ffTools'), wx.OK).ShowModal()
		else:
			execute= subprocess.Popen(self.command, startupinfo= self.no_settings)

	def formatChange(self):
		execute= subprocess.Popen(self.command, startupinfo= self.settings)

	def extractValue(self, content):
		max_volume_pattern= compile(r'max_volume:\s+\-?(\d+\.\d+)')
		mean_volume_pattern= compile(r'mean_volume:\s+\-?(\d+\.\d+)')
		max_volume= max_volume_pattern.search(content)[1]
		mean_volume= mean_volume_pattern.search(content)[1]
		if mean_volume and max_volume:
			return mean_volume, max_volume

	def extractTime(self, ffmpeg, type_cut, start_time= None, finish_time= None):
		if type_cut == 'beginning':
			file_path= os.path.splitext(self.file_path)
			cut_command= f'{ffmpeg} -i "{self.file_path}" -ss {start_time} "{file_path[0]}-c{file_path[1]}"'
			try:
				out= subprocess.Popen(cut_command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
			except OSError:
				subprocess.Popen('taskkill /im /f cmd.exe', stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
				out= subprocess.Popen(cut_command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
			out.wait()
			browseableMessage("Proceso finalizado")
			return
		extract_command= f'{self.executable_path} -i "{self.file_path}"'
		try:
			out= subprocess.Popen(extract_command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
		except OSError:
			out= subprocess.Popen('taskkill /f /im cmd.exe', stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
			out= subprocess.Popen(extract_command, stdout= subprocess.PIPE, stderr= subprocess.PIPE, startupinfo= self.settings)
		content= str(out.stderr.read())
		pattern= compile(r'Duration: \d\d:(\d\d:\d\d)\.\d+')
		value= pattern.search(content)
		return value[1]
