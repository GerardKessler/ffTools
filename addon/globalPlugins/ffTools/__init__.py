# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gera Késsler <gera.kessler@gmail.com>
# This file is covered by the GNU General Public License.

import wx
from threading import Thread
import subprocess
from re import compile
from time import sleep
import os
from json import load
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
	if os.path.splitext(targetFile)[1] in FORMAT_LIST:
		return targetFile
	else:
		message('Archivo no soportado')
		return None

# constantes (url de los binarios, rutas de los binarios ff, ruta del complemento, lista de formatos soportados)
MAIN_PATH= os.path.dirname(__file__)
MPEG_PATH= os.path.join(MAIN_PATH, 'bin', 'ffmpeg.exe')
PLAY_PATH= os.path.join(MAIN_PATH, 'bin', 'ffplay.exe')
PROBE_PATH= os.path.join(MAIN_PATH, 'bin', 'ffprobe.exe')
DL_URL= 'https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest'
with open(os.path.join(MAIN_PATH, 'format.list'), 'r') as list_file:
	FORMAT_LIST= load(list_file)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__()
		self.check= False
		self.switch= False
		self.value= 0
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
		if sound: beep(220,10)
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def binFilesVerify(self):
		if os.path.isdir(os.path.join(MAIN_PATH, 'bin')):
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
		wx.MessageDialog(None, _('El proceso ha finalizado correctamente'), _('ffTools:'), wx.OK).ShowModal()

	@script(
		category= 'ffTools',
		# Translators: Descripción del comando en el diálogo gestos de entrada
		description= _('Activa la capa de comandos'),
		gesture= 'kb:NVDA+shift+e'
	)
	def script_commandLayer(self, gesture):
		self.bindGestures(self.__newGestures)
		self.switch= True
		beep(880,5)

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

	def script_preview(self, gesture):
		self.finish(False)
		if not self.check:
			self.binFilesVerify()
			return
		file_path= getFilePath()
		if file_path:
			command= f'{PLAY_PATH} "{file_path}" -window_title "{os.path.splitext(os.path.split(file_path)[1])[0]}"'
			newProcessing= NewProcessing(command, False)
			Thread(target=newProcessing.newProcess, daemon= True).start()

	__newGestures= {
		"kb:space": "preview",
		"kb:f": "fileModify",
		"kb:c": "fileCut"
	}

class NewProcessing():

	def __init__(self, command, hide_console):
		self.command= command
		self.hide_console= hide_console

	def newProcess(self):
		if self.hide_console:
			message('Proceso iniciado')
			execute= subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
			stdout, stderr= execute.communicate()
			execute.stdin.close()
			execute.stdout.close()
			execute.stderr.close()
		else:
			process= subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
			stdout, stderr= process.communicate()
			process.stdin.close()
			process.stdout.close()
			process.stderr.close()
		message('Proceso Finalizado')
import wx

class Ventana(wx.Frame):
    def __init__(self, parent, title):
        super(Ventana, self).__init__(parent, title=title, size=(300, 200))

        # Crear un panel para la ventana
        panel = wx.Panel(self)

        # Crear la casilla de verificación
        self.checkbox = wx.CheckBox(panel, label="Normalizar", pos=(20, 20))

        # Desmarcar la casilla de verificación por defecto
        self.checkbox.SetValue(False)

        # Crear el ListBox con los bitrates de audio
        self.listbox = wx.ListBox(panel, pos=(20, 50), size=(200, 100))
        self.listbox.AppendItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])

        # Asociar el evento OnCheckBox a la casilla de verificación
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)

        # Mostrar la ventana
        self.Show(True)

    def OnCheckBox(self, event):
        if self.checkbox.GetValue():
            # Si la casilla está marcada, ocultar el ListBox
            self.listbox.Hide()
        else:
            # Si la casilla está desmarcada, mostrar el ListBox
            self.listbox.Show()
        # Actualizar la ventana para que se muestren los cambios
        self.Layout()

if __name__ == '__main__':
    app = wx.App()
    Ventana(None, title='Ejemplo de ventana con casilla de verificación y ListBox')
    app.MainLoop()

class ModifyDialog(wx.Dialog):
	def __init__(self, parent, title, file_path, file_name):
		super(ModifyDialog, self).__init__(parent, -1, title=title)
		self.file_path= file_path
		self.file_name= file_name

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		name_label= wx.StaticText(self, wx.ID_ANY, _("Nombre del archivo saliente"))
		sizer_1.Add(name_label, 0, 0, 0)

		self.out_name = wx.TextCtrl(self, wx.ID_ANY, f'{self.file_name}-mod')
		sizer_1.Add(self.out_name, 0, 0, 0)

		format_label= wx.StaticText(self, wx.ID_ANY, _("Formato a convertir"))
		sizer_1.Add(format_label, 0, 0, 0)

		format_list= ['.aac', '.wma', '.ogg', '.wav', '.flac', '.mp3', '.mp4', '.avi', 'mpg', 'mov', 'mkv', 'flv']
		self.format_list = wx.ListBox(self, wx.ID_ANY, choices=format_list)
		sizer_1.Add(self.format_list, 0, 0, 0)
		self.format_list.SetSelection(5)

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
		self.Destroy()
		out_path= f'{os.path.split(self.file_path)[0]}\\{self.out_name.GetValue()}{self.format_list.GetStringSelection()}'
		if out_path == self.file_path:
			wx.MessageDialog(None, 'El nombre y formato de salida coinciden', 'Proceso Cancelado').ShowModal()
			return
		if self.checkbox.GetValue():
			command= f'{MPEG_PATH} -y -i "{self.file_path}" -acodec {self.format_list.GetStringSelection()[1:]} -b:a {self.bitrate_list.GetStringSelection()}k -filter:a "loudnorm=I=-16:LRA=11:TP=-0.1" "{os.path.split(self.file_path)[0]}\\{self.out_name.GetValue()}{self.format_list.GetStringSelection()}"'
		else:
			command= f'{MPEG_PATH} -y -i "{self.file_path}" -acodec {self.format_list.GetStringSelection()[1:]} -b:a {self.bitrate_list.GetStringSelection()}k -af "volume={self.volume_list.GetStringSelection()}dB" "{os.path.split(self.file_path)[0]}\\{self.out_name.GetValue()}{self.format_list.GetStringSelection()}"'
		newProcessing= NewProcessing(command, True)
		Thread(target=newProcessing.newProcess, daemon= True).start()

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

class CutDialog(wx.Dialog):
	def __init__(self, parent, title, file_path, file_name):
		super(CutDialog, self).__init__(parent, -1, title=title)
		self.file_path= file_path
		self.file_name= file_name
		self.duration= self.getDuration()

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		start_label= wx.StaticText(self, wx.ID_ANY, 'Inicio')
		sizer_1.Add(start_label, 0, 0, 0)

		self.start= wx.TextCtrl(self, wx.ID_ANY, '00:00')
		sizer_1.Add(self.start, 0, 0, 0)

		duration_label= wx.StaticText(self, wx.ID_ANY, f'Final- Total {self.duration}')
		sizer_1.Add(duration_label, 0, 0, 0)

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

	def onApli(self, event):
		self.Destroy()
		root= os.path.split(self.file_path)
		filename= os.path.splitext(root[1])
		command= f'{MPEG_PATH} -i "{self.file_path}" -ss {self.start.GetValue()} -to {self.end.GetValue()} -c copy "{root[0]}\\{filename[0]}-cut{filename[1]}"'
		execute= subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
		stdout, stderr= execute.communicate()
		execute.stdin.close()
		execute.stdout.close()
		execute.stderr.close()
		message('Proceso finalizado')

	def onCancel(self, event):
		self.Destroy()

	def getDuration(self):
		command= [MPEG_PATH, '-i', self.file_path]
		output= subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
		stdout, stderr= output.communicate()
		duration = None
		for line in stderr.decode('utf-8').split('\n'):
			if "Duration" in line:
				duration= line.split(',')[0].split(': ')[-1]
				pattern= compile(r'0?0?:?([\d\:]+)\.')
				duration_format= pattern.search(duration)[1]
				return duration_format
