# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gera Késsler <gera.kessler@gmail.com>
# This file is covered by the GNU General Public License.

import wx
from threading import Thread
import subprocess
from re import compile
from time import sleep
from winsound import PlaySound, SND_FILENAME, SND_ASYNC, SND_LOOP, SND_PURGE
import os
from json import load
import shutil
import zipfile
import gui
import globalPluginHandler
import addonHandler
from urllib import request
import socket
from comtypes.client import CreateObject as COMCreate

import api
import controlTypes
from scriptHandler import script
from ui import message, browseableMessage

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
	if os.path.splitext(targetFile)[1] in FORMAT_LIST:
		return targetFile
	else:
		message('Archivo no soportado')
		return None

# constantes (url de los binarios, rutas de los binarios ff, ruta del complemento, lista de formatos soportados)
MAIN_PATH= os.path.dirname(__file__)
MPEG_PATH= os.path.join(MAIN_PATH, 'bin', 'ffmpeg.exe')
PLAY_PATH= os.path.join(MAIN_PATH, 'bin', 'ffplay.exe')
DL_URL= 'https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest'
with open(os.path.join(MAIN_PATH, 'format.list'), 'r') as list_file:
	FORMAT_LIST= load(list_file)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__()
		self.check= False
		self.switch= False
		self.percent= 0
		self.binFilesVerify()

	def getScript(self, gesture):
		if not self.switch:
			return globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script= globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		if not script:
			self.finish()
			return
		return globalPluginHandler.GlobalPlugin.getScript(self, gesture)

	def finish(self, sound= True):
		self.switch= False
		if sound: PlaySound(os.path.join(MAIN_PATH, 'sounds', 'out.wav'), SND_FILENAME)
		self.clearGestureBindings()
		# self.bindGestures(self.__gestures)

	def binFilesVerify(self):
		if os.path.isdir(os.path.join(MAIN_PATH, 'bin')):
			self.check= True
			return
		THREAD= Thread(target= self.filesDownload, daemon= True)
		THREAD.start()

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
			request.urlretrieve(result[1], os.path.join(MAIN_PATH, 'ffmpeg_temp.zip'), reporthook= self.__call__)
			self.extractFiles()

	def extractFiles(self):
		zip_file= zipfile.ZipFile(os.path.join(MAIN_PATH, 'ffmpeg_temp.zip'))
		root= zip_file.namelist()[0]
		zip_file.extractall(MAIN_PATH)
		zip_file.close()
		os.remove(os.path.join(MAIN_PATH, 'ffmpeg_temp.zip'))
		shutil.move(os.path.join(MAIN_PATH, root, 'bin'), MAIN_PATH)
		shutil.rmtree(os.path.join(MAIN_PATH, root))
		os.remove(os.path.join(MAIN_PATH, 'bin', 'ffprobe.exe'))
		wx.MessageDialog(None, _('El proceso ha finalizado correctamente'), _('ffTools:'), wx.OK).ShowModal()
		self.check= True

	@script(
		category= 'ffTools',
		description= 'Activa la capa de comandos (f, modificación de formato. c, modificación de velocidad y corte. l, conversión por lotes)',
		gesture= None
	)
	def script_commandLayer(self, gesture):
		self.bindGestures(self.__newGestures)
		self.switch= True
		PlaySound(os.path.join(MAIN_PATH, 'sounds', 'in.wav'), SND_FILENAME)

	def script_fileModify(self, gesture):
		self.finish(False)
		if not self.check:
			self.binFilesVerify()
			return
		file_path= getFilePath()
		if file_path:
			file_name= os.path.split(file_path)[1]
			modify_dialog= ModifyDialog(gui.mainFrame, file_name, file_path, os.path.splitext(file_name)[0])
			gui.mainFrame.prePopup()
			modify_dialog.Show()

	def script_fileCut(self, gesture):
		self.finish(False)
		if not self.check:
			self.binFilesVerify()
			return
		file_path= getFilePath()
		if file_path:
			file_name= os.path.split(file_path)[1]
			cut_dialog= CutDialog(gui.mainFrame, file_name, file_path, os.path.splitext(file_name)[0])
			gui.mainFrame.prePopup()
			cut_dialog.Show()

	def script_batchConversion(self, gesture):
		self.finish(False)
		if not self.check:
			self.binFilesVerify()
			return
		batch_dialog= BatchDialog(gui.mainFrame, 'Conversión por lotes')
		gui.mainFrame.prePopup()
		batch_dialog.Show()

	@script(
			category= 'ffTools',
			description= 'Activa la previsualización del archivo de audio o video con el foco',
			gesture= None
	)
	def script_preview(self, gesture):
		self.finish(False)
		if not self.check:
			self.binFilesVerify()
			return
		file_path= getFilePath()
		if file_path:
			command= f'{PLAY_PATH} "{file_path}" -window_title "{os.path.splitext(os.path.split(file_path)[1])[0]}"'
			newProcessing= NewProcessing(command, False)
			THREAD= Thread(target=newProcessing.newProcess, daemon= True)
			THREAD.start()

	def script_viewReadme(self, gesture):
		self.finish(False)
		wx.LaunchDefaultBrowser(f'file://{addonHandler.Addon(os.path.join(MAIN_PATH, "..", "..")).getDocFilePath()}', flags=0)

	__newGestures= {
		"kb:f1": "viewReadme",
		"kb:f": "fileModify",
		"kb:l": "batchConversion",
		"kb:c": "fileCut"
	}

class NewProcessing():

	def __init__(self, command, hide_console):
		self.command= command
		self.hide_console= hide_console

	def newProcess(self, total_seconds= None):
		value= 0
		if self.hide_console:
			PlaySound(os.path.join(MAIN_PATH, 'sounds', 'tictac.wav'), SND_LOOP | SND_ASYNC)
			process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
			pattern = compile(r'time=(\d\d:\d\d:\d\d\.\d\d)')
			try:
				for line in process.stdout:
					match= pattern.search(line)
					if match:
						time_str = match.group(1)
						h, m, s = time_str.split(':')
						current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
						percentage = current_seconds / total_seconds * 100
						percentage= round(percentage)
						if percentage >= value+10:
							message(f'{percentage} porciento')
							value= percentage
				process.wait()
				if process.returncode != 0:
					message(f'Ha habido un error durante la conversión: {process.returncode}')
				else:
					message('La conversión ha terminado correctamente.')
			except UnicodeDecodeError:
				pass
			process.wait()
			PlaySound(os.path.join(MAIN_PATH, 'sounds', 'out.wav'), SND_FILENAME)
		else:
			PROCESS= subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
			stdout, stderr= PROCESS.communicate()
			PROCESS.stdin.close()
			PROCESS.stdout.close()
			PROCESS.stderr.close()

class ModifyDialog(wx.Dialog):
	def __init__(self, parent, title, file_path, file_name):
		super(ModifyDialog, self).__init__(parent, -1, title=title)
		self.file_path= file_path
		self.file_name= file_name
		self.duration, self.bitrate= self.getFileInfo()

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		name_label= wx.StaticText(self, wx.ID_ANY, _("Nombre del archivo saliente"))
		sizer_1.Add(name_label, 0, 0, 0)

		self.out_name = wx.TextCtrl(self, wx.ID_ANY, f'{self.file_name}-m')
		sizer_1.Add(self.out_name, 0, 0, 0)

		format_label= wx.StaticText(self, wx.ID_ANY, _("Formato a convertir"))
		sizer_1.Add(format_label, 0, 0, 0)

		format_list= ['.aiff', '.aac', '.wma', '.ogg', '.wav', '.flac', '.mp3', '.mp4', '.avi', '.wmv', '.mov', '.flv', '.mkv']
		self.format_list = wx.ListBox(self, wx.ID_ANY, choices=format_list)
		sizer_1.Add(self.format_list, 0, 0, 0)
		self.format_list.SetSelection(6)

		self.checkbox= wx.CheckBox(self, label='Normalizar el volúmen de audio', pos=(20, 20))
		sizer_1.Add(self.checkbox, 0, 0, 0)
		self.checkbox.SetValue(False)
		self.checkbox.Bind(wx.EVT_CHECKBOX, self.onCheckBox)

		self.volume_label= wx.StaticText(self, wx.ID_ANY, _(u'Volúmen de salida'))
		sizer_1.Add(self.volume_label, 0, 0, 0)

		volume_list= ['15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8', '-9', '-10', '-11', '-12', '-13', '-14', '-15']
		self.volume_list = wx.ListBox(self, wx.ID_ANY, choices=volume_list)
		sizer_1.Add(self.volume_list, 0, 0, 0)
		self.volume_list.SetSelection(15)

		bitrate_label= wx.StaticText(self, wx.ID_ANY, _(f'Bitrate. Valor original; {self.bitrate}'))
		sizer_1.Add(bitrate_label, 0, 0, 0)

		bitrate_list= ['366', '320', '256', '224', '192', '160', '128', '112', '96']

		self.bitrate_list = wx.ListBox(self, wx.ID_ANY, choices=bitrate_list)
		sizer_1.Add(self.bitrate_list, 0, 0, 0)
		self.bitrate_list.SetSelection(6)

		sizer_2 = wx.StdDialogButtonSizer()
		sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

		self.apli_button= wx.Button(self, wx.ID_ANY, '&Aplicar')
		sizer_2.AddButton(self.apli_button)
		self.apli_button.Bind(wx.EVT_BUTTON, self.onApli)

		self.cancel_button = wx.Button(self, wx.ID_ANY, '&Cancelar')
		sizer_2.AddButton(self.cancel_button)
		self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)

		sizer_2.Realize()

		self.SetSizer(sizer_1)
		sizer_1.Fit(self)

		self.SetEscapeId(self.cancel_button.GetId())

		self.Layout()

	def onApli(self, event):
		self.Destroy()
		out_path= f'{os.path.split(self.file_path)[0]}\\{self.out_name.GetValue()}{self.format_list.GetStringSelection()}'
		if out_path == self.file_path:
			wx.MessageDialog(None, 'El nombre y formato de salida coinciden', 'Proceso Cancelado').ShowModal()
			return
		if self.checkbox.GetValue():
			command= f'{MPEG_PATH} -y -i "{self.file_path}" -b:a {self.bitrate_list.GetStringSelection()}k -filter:a "loudnorm=I=-16:LRA=11:TP=-0.1" "{os.path.split(self.file_path)[0]}\\{self.out_name.GetValue()}{self.format_list.GetStringSelection()}"'
		else:
			command= f'{MPEG_PATH} -y -i "{self.file_path}" -b:a {self.bitrate_list.GetStringSelection()}k -af "volume={self.volume_list.GetStringSelection()}dB" "{os.path.split(self.file_path)[0]}\\{self.out_name.GetValue()}{self.format_list.GetStringSelection()}"'
		tiempo_total= self.getSeconds(self.duration)
		newProcessing= NewProcessing(command, True)
		THREAD= Thread(target=newProcessing.newProcess, args=(tiempo_total,), daemon= True)
		THREAD.start()

	def onCancel(self, event):
		self.Destroy()

	def onCheckBox(self, event):
		if self.checkbox.GetValue():
			self.volume_list.Hide()
			self.volume_label.Hide()
		else:
			self.volume_list.Show()
			self.volume_label.Show()
		self.Layout()

	def getFileInfo(self):
		command= [MPEG_PATH, '-i', self.file_path]
		PROCESS= subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
		stdout, stderr= PROCESS.communicate()
		for line in stderr.decode('utf-8').split('\n'):
			if "Duration:" in line:
				pattern= compile(r'Duration:\s0?0?:?([\d\:]+)\.\d.+bitrate:\s(\d{2,4})\skb/s')
				data= pattern.search(line)
				return data[1], data[2]

	def getSeconds(self, time):
		try:
			time= time.split(':')
			time= [int(t) for t in time]
		except ValueError:
			raise ValueError("El formato de la cadena no es válido")
		if len(time) == 2:
			return time[0] * 60 + time[1]
		elif len(time) == 3:
			return time[0] * 3600 + time[1] * 60 + time[2]
		else:
			return None

class CutDialog(wx.Dialog):
	def __init__(self, parent, title, file_path, file_name):
		super(CutDialog, self).__init__(parent, -1, title=title)
		self.file_path= file_path
		self.file_name= file_name
		self.duration= self.getDuration()

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		self.checkbox= wx.CheckBox(self, label='Modificar la velocidad del archivo', pos=(20, 20))
		sizer_1.Add(self.checkbox, 0, 0, 0)
		self.checkbox.SetValue(False)
		self.checkbox.Bind(wx.EVT_CHECKBOX, self.onCheckBox)

		self.rate_label= wx.StaticText(self, wx.ID_ANY, 'Velocidad de salida')
		sizer_1.Add(self.rate_label, 0, 0, 0)
		self.rate_label.Hide()

		self.rate_dic= {'doble tempo': [2.0, 0.5], '90 porciento más': [1.9, 0.55], '80 porciento más': [1.8, 0.6], '70 porciento más': [1.7, 0.65], '60 porciento más': [1.6, 0.7], '50 porciento más': [1.5, 0.75], '40 porciento más': [1.4, 0.8], '30 porciento más': [1.3, 0.85], '20 porciento más': [1.2, 0.9], '10 porciento más': [1.1, 0.95], 'Tempo actual': [1.0, 1.0], '10 porciento menos': [0.9, 1.2], '20 porciento menos': [0.8, 1.4], '30 porciento menos': [0.7, 1.6], '40 porciento menos': [0.6, 1.8], 'mitad de tempo': [0.5, 2.0]}
		self.rate_list = wx.ListBox(self, wx.ID_ANY, choices=list(self.rate_dic.keys()))
		sizer_1.Add(self.rate_list, 0, 0, 0)
		self.rate_list.SetSelection(10)
		self.rate_list.Hide()

		self.start_label= wx.StaticText(self, wx.ID_ANY, 'Corte inicial')
		sizer_1.Add(self.start_label, 0, 0, 0)

		self.start= wx.TextCtrl(self, wx.ID_ANY, '00:00')
		sizer_1.Add(self.start, 0, 0, 0)

		self.end_label= wx.StaticText(self, wx.ID_ANY, f'Corte final- Tiempo total; {self.duration}')
		sizer_1.Add(self.end_label, 0, 0, 0)

		self.end= wx.TextCtrl(self, wx.ID_ANY, self.duration)
		sizer_1.Add(self.end, 0, 0, 0)

		sizer_2 = wx.StdDialogButtonSizer()
		sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

		self.apli_button= wx.Button(self, wx.ID_ANY, '&Aplicar')
		sizer_2.AddButton(self.apli_button)
		self.apli_button.Bind(wx.EVT_BUTTON, self.onApli)

		self.cancel_button = wx.Button(self, wx.ID_ANY, '&Cancelar')
		sizer_2.AddButton(self.cancel_button)
		self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)

		sizer_2.Realize()

		self.SetSizer(sizer_1)
		sizer_1.Fit(self)

		self.SetEscapeId(self.cancel_button.GetId())

		self.Layout()

	def onCheckBox(self, event):
		if self.checkbox.GetValue():
			self.start_label.Hide()
			self.start.Hide()
			self.end_label.Hide()
			self.end.Hide()
			self.rate_label.Show()
			self.rate_list.Show()
		else:
			self.rate_label.Hide()
			self.rate_list.Hide()
			self.start_label.Show()
			self.start.Show()
			self.end_label.Show()
			self.end.Show()
		self.Layout()

	def onApli(self, event):
		root= os.path.split(self.file_path)
		filename= os.path.splitext(root[1])
		if self.checkbox.GetValue():
			command= f'{MPEG_PATH} -i "{self.file_path}" -filter:a "atempo={self.rate_dic[self.rate_list.GetStringSelection()][0]}" "{root[0]}\\{filename[0]}-v{filename[1]}"'
			total_seconds= round(self.getSeconds(self.duration) * self.rate_dic[self.rate_list.GetStringSelection()][1])
		else:
			command= f'{MPEG_PATH} -i "{self.file_path}" -ss {self.start.GetValue()} -to {self.end.GetValue()} -c copy "{root[0]}\\{filename[0]}-c{filename[1]}"'
			start= self.getSeconds(self.start.GetValue())
			end= self.getSeconds(self.end.GetValue())
			total_seconds= end - start
		THREAD= Thread(target=self.executeCommand, args=(command, total_seconds), daemon= True)
		THREAD.start()
		self.Destroy()

	def executeCommand(self, command, total_seconds):
		PlaySound(os.path.join(MAIN_PATH, 'sounds', 'tictac.wav'), SND_LOOP | SND_ASYNC)
		value= 0
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
		pattern = compile(r'time=(\d\d:\d\d:\d\d\.\d\d)')
		for line in process.stdout:
			match= pattern.search(line)
			if match:
				time_str = match.group(1)
				h, m, s = time_str.split(':')
				current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
				percentage = current_seconds / total_seconds * 100
				percentage= round(percentage)
				if percentage >= value+10:
					message(f'{percentage} porciento')
					value= percentage
		process.wait()
		if process.returncode != 0:
			message(f'Ha habido un error durante la conversión: {process.returncode}')
		else:
			message('La conversión ha terminado correctamente.')
		PlaySound(None, SND_PURGE)

	def getSeconds(self, time):
		try:
			time= time.split(':')
			time= [int(t) for t in time]
		except ValueError:
			wx.MessageDialog(None, 'El formato de la cadena no es válido', '😟').ShowModal()
			raise ValueError("El formato de la cadena no es válido")
		if len(time) == 2:
			return time[0] * 60 + time[1]
		elif len(time) == 3:
			return time[0] * 3600 + time[1] * 60 + time[2]
		else:
			return None

	def onCancel(self, event):
		self.Destroy()

	def getDuration(self):
		command= [MPEG_PATH, '-i', self.file_path]
		PROCESS= subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
		stdout, stderr= PROCESS.communicate()
		duration = None
		for line in stderr.decode('utf-8').split('\n'):
			if "Duration" in line:
				duration= line.split(',')[0].split(': ')[-1]
				pattern= compile(r'0?0?:?([\d\:]+)\.')
				duration_format= pattern.search(duration)[1]
				return duration_format

class BatchDialog(wx.Dialog):
	def __init__(self, parent, title):
		super(BatchDialog, self).__init__(parent, -1, title=title)
		self.files= 'None'

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		path_label= wx.StaticText(self, wx.ID_ANY, 'Ruta de carpeta')
		sizer_1.Add(path_label, 0, 0, 0)

		self.path_files= wx.TextCtrl(self, wx.ID_ANY, self.files)
		sizer_1.Add(self.path_files, 0, 0, 0)

		self.examinar_button= wx.Button(self, wx.ID_ANY, '&Examinar')
		self.examinar_button.Bind(wx.EVT_BUTTON, self.onExaminar)

		format_label= wx.StaticText(self, wx.ID_ANY, _("Formato a convertir"))
		sizer_1.Add(format_label, 0, 0, 0)

		format_list= ['.aiff', '.aac', '.wma', '.ogg', '.wav', '.flac', '.mp3', '.mp4', '.avi', '.wmv', '.mov', '.flv', '.mkv']
		self.format_list = wx.ListBox(self, wx.ID_ANY, choices=format_list)
		sizer_1.Add(self.format_list, 0, 0, 0)
		self.format_list.SetSelection(6)

		self.checkbox= wx.CheckBox(self, label='Normalizar el volúmen de audio', pos=(20, 20))
		sizer_1.Add(self.checkbox, 0, 0, 0)
		self.checkbox.SetValue(False)

		bitrate_label= wx.StaticText(self, wx.ID_ANY, _("Bitrate de audio"))
		sizer_1.Add(bitrate_label, 0, 0, 0)

		bitrate_list= ['366', '320', '256', '224', '192', '160', '128', '112', '96']

		self.bitrate_list = wx.ListBox(self, wx.ID_ANY, choices=bitrate_list)
		sizer_1.Add(self.bitrate_list, 0, 0, 0)
		self.bitrate_list.SetSelection(6)

		sizer_2 = wx.StdDialogButtonSizer()
		sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

		self.apli_button= wx.Button(self, wx.ID_ANY, '&Aplicar')
		sizer_2.AddButton(self.apli_button)
		self.apli_button.Bind(wx.EVT_BUTTON, self.onApli)

		self.cancel_button = wx.Button(self, wx.ID_ANY, '&Cancelar')
		sizer_2.AddButton(self.cancel_button)
		self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)

		sizer_2.Realize()

		self.SetSizer(sizer_1)
		sizer_1.Fit(self)

		self.SetEscapeId(self.cancel_button.GetId())

		self.Layout()

	def onApli(self, event):
		self.Hide()
		elements= os.listdir(self.files)
		files= [os.path.join(self.files, file) for file in elements if file.endswith(tuple(FORMAT_LIST))]
		Thread(target=self.execute, args=(files,), daemon=True).start()

	def execute(self, files):
		PlaySound(os.path.join(MAIN_PATH, 'sounds', 'tictac.wav'), SND_LOOP | SND_ASYNC)
		if not os.path.exists(os.path.join(self.path_files.GetValue(), 'convertidos')):
			os.makedirs(os.path.join(self.path_files.GetValue(), 'convertidos'))
		for file in files:
			out_file= f'{os.path.split(file)[0]}\\convertidos\\{os.path.splitext(os.path.split(file)[1])[0]}{self.format_list.GetStringSelection()}'
			if self.checkbox.GetValue():
				command= f'{MPEG_PATH} -y -i "{file}" -b:a {self.bitrate_list.GetStringSelection()}k -filter:a "loudnorm=I=-16:LRA=11:TP=-0.1" "{out_file}"'
			else:
				command= f'{MPEG_PATH} -y -i "{file}" -b:a {self.bitrate_list.GetStringSelection()}k "{out_file}"'
			PROCESS= subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
			stdout, stderr= PROCESS.communicate()
			PROCESS.stdin.close()
			PROCESS.stdout.close()
			PROCESS.stderr.close()
		self.Destroy()
		PlaySound(None, SND_PURGE)
		wx.MessageDialog(None, 'Proceso finalizado correctamente', '✌').ShowModal()

	def onCancel(self, event):
		self.Destroy()

	def onExaminar(self, event):
		Thread(target=self.getPath, daemon= True).start()

	def getPath(self):
		browse_folder= wx.DirDialog(None, 'Seleccionar la carpeta con los archivos a convertir', style=wx.DD_DEFAULT_STYLE)
		if browse_folder.ShowModal() == wx.ID_OK:
			files= browse_folder.GetPath()
			self.path_files.SetValue(files)
			self.files= files
