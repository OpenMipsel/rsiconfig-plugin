from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens.InputBox import InputBox
from Components.Input import Input
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Tools.HardwareInfo import HardwareInfo
import os

from Components.ServiceEventTracker import ServiceEventTracker
import NavigationInstance
from enigma import iPlayableService, iRecordableService, iServiceInformation
from Components.config import config, ConfigSubList, ConfigSubsection, ConfigSlider

from Screens.InfoBarGenerics import InfoBarPlugins, InfoBarEPG
from Screens.InfoBar import InfoBar
from Components.Sources.List import List
import keymapparser

from time import *
import time
import datetime

newInfoBarPlugins__init__ = None

config.rsi = ConfigSubsection()
config.rsi.vfdoffstandby = ConfigYesNo(default=False)
config.rsi.recstandby = ConfigYesNo(default=False)
config.rsi.keymaphelper = ConfigYesNo(default=True)
boxime = HardwareInfo().get_device_name()
if boxime == 'minime':
	boxime = 'me'
if boxime == 'premium+' or boxime == 'premium':
	config.rsi.redled = ConfigSelection(choices={"alwaysoff": _("Always off"), "standbyoff": _("Standby off"), "alwayson": _("Always on"), "recon": _("Recording on"), "hdon": _("HD on")}, default="recon")
	config.rsi.blueled = ConfigSelection(choices={"alwaysoff": _("Always off"), "standbyoff": _("Standby off"), "alwayson": _("Always on"), "recon": _("Recording on"), "hdon": _("HD on")}, default="standbyoff")
	config.rsi.greenled = ConfigSelection(choices={"alwaysoff": _("Always off"), "standbyoff": _("Standby off"), "alwayson": _("Always on"), "recon": _("Recording on"), "hdon": _("HD on")}, default="hdon")
elif boxime == 'ultra':
	config.rsi.firstled = ConfigSelection(choices={"alwaysoff": _("Always off"), "standbyoff": _("Standby off"), "alwayson": _("Always on"), "recon": _("Recording on"), "hdon": _("HD on")}, default="alwayson")
	config.rsi.secondled = ConfigSelection(choices={"alwaysoff": _("Always off"), "standbyoff": _("Standby off"), "alwayson": _("Always on"), "recon": _("Recording on"), "hdon": _("HD on")}, default="standbyoff")
elif boxime == 'me' or boxime == 'gb800ue':
	config.rsi.normalled = ConfigSelection(choices={"0": _("Off"), "1": _("Blue"), "2": _("Red"), "3": _("Purple")}, default="1")
	config.rsi.recordled = ConfigSelection(choices={"0": _("Off"), "1": _("Blue"), "2": _("Red"), "3": _("Purple")}, default="2")
	config.rsi.hdled = ConfigSelection(choices={"0": _("Off"), "1": _("Blue"), "2": _("Red"), "3": _("Purple")}, default="1")
	config.rsi.standbyled = ConfigSelection(choices={"0": _("Off"), "1": _("Blue"), "2": _("Red"), "3": _("Purple")}, default="3")
	config.rsi.syncNTPtime = ConfigSelection(choices=[("1", _("Press OK"))], default="1")
	config.rsi.syncDVBtime = ConfigSelection(choices=[("1", _("Press OK"))], default="1")
	config.rsi.syncManually = ConfigSelection(choices=[("1", _("Press OK"))], default="1")
	config.rsi.empty = ConfigSelection(choices=[("1", _(" "))], default="1")
if boxime == 'premium+' or boxime == 'ultra':
	config.rsi.fanoff = ConfigSelection(choices={"alwaysoff": _("Always off"), "standbyoff": _("Standby off"), "alwayson": _("Always on")}, default="standbyoff")

#For me led control we have to know present state of recording and hd
screensize = 0
standby = 0
recording = 0
hd = 0


def redled(switch):
	if switch == 0:
		try:
			open("/proc/led", "w").write("3")
		except:
			pass
	if switch == 1:
		try:
			open("/proc/led", "w").write("4")
		except:
			pass


def blueled(switch):
	if switch == 0:
		try:
			open("/proc/led", "w").write("1")
		except:
			pass
	if switch == 1:
		try:
			open("/proc/led", "w").write("2")
		except:
			pass


def greenled(switch):
	if switch == 0:
		try:
			open("/proc/led", "w").write("5")
		except:
			pass
	if switch == 1:
		try:
			open("/proc/led", "w").write("6")
		except:
			pass


def firstled(switch):
	if switch == 0:
		try:
			os.system("echo 1 > /proc/led")
		except:
			pass
	else:
		try:
			os.system("echo 2 > /proc/led")
		except:
			pass


def secondled(switch):
	if switch == 0:
		try:
			os.system("echo 3 > /proc/led")
		except:
			pass
	else:
		try:
			os.system("echo 4 > /proc/led")
		except:
			pass


def singleled(color):
	try:
		if boxime == 'gb800ue':
			os.system("echo " + str(color) + " > /proc/stb/fp/led0_pattern")
		else:
			os.system("echo " + str(color) + " > /proc/led")
	except:
		pass


def singleleddelayed(color):
	try:
		if boxime == 'gb800ue':
			os.system("echo " + str(color) + " > /proc/stb/fp/led0_pattern")
		else:
			os.system("sleep 1 && echo " + str(color) + " > /proc/led")
	except:
		pass


def fanctl(switch):
	if switch == 0:
		try:
			open("/proc/fan", "w").write("0")
		except:
			pass
	else:
		try:
			open("/proc/fan", "w").write("1")
		except:
			pass


def startup(startup=1):
	print("Applying RSI Configuration Options")
	if boxime == 'premium+' or boxime == 'premium':
		if config.rsi.redled.value == 'alwaysoff' or (config.rsi.redled.value == 'hdon' and hd == 0) or (config.rsi.redled.value == 'recon' and recording == 0):
			redled(0)
		elif config.rsi.redled.value == 'alwayson' or config.rsi.redled.value == 'standbyoff' or (config.rsi.redled.value == 'hdon' and hd == 1) or (config.rsi.redled.value == 'recon' and recording == 1):
			redled(1)

		if config.rsi.blueled.value == 'alwaysoff' or (config.rsi.blueled.value == 'hdon' and hd == 0) or (config.rsi.blueled.value == 'recon' and recording == 0):
			blueled(0)
		elif config.rsi.blueled.value == 'alwayson' or config.rsi.blueled.value == 'standbyoff' or (config.rsi.blueled.value == 'hdon' and hd == 1) or (config.rsi.blueled.value == 'recon' and recording == 1):
			blueled(1)

		if config.rsi.greenled.value == 'alwaysoff' or (config.rsi.greenled.value == 'hdon' and hd == 0) or (config.rsi.greenled.value == 'recon' and recording == 0):
			greenled(0)
		elif config.rsi.greenled.value == 'alwayson' or config.rsi.greenled.value == 'standbyoff' or (config.rsi.greenled.value == 'hdon' and hd == 1) or (config.rsi.greenled.value == 'recon' and recording == 1):
			greenled(1)

	elif boxime == 'ultra':
		if config.rsi.firstled.value == 'alwaysoff' or (config.rsi.firstled.value == 'hdon' and hd == 0) or (config.rsi.firstled.value == 'recon' and recording == 0):
			firstled(0)
		elif config.rsi.firstled.value == 'alwayson' or config.rsi.firstled.value == 'standbyoff' or (config.rsi.firstled.value == 'hdon' and hd == 1) or (config.rsi.firstled.value == 'recon' and recording == 1):
			firstled(1)

		if config.rsi.secondled.value == 'alwaysoff' or (config.rsi.secondled.value == 'hdon' and hd == 0) or (config.rsi.secondled.value == 'recon' and recording == 0):
			secondled(0)
		elif config.rsi.secondled.value == 'alwayson' or config.rsi.secondled.value == 'standbyoff' or (config.rsi.secondled.value == 'hdon' and hd == 1) or (config.rsi.secondled.value == 'recon' and recording == 1):
			secondled(1)

	elif boxime == 'me' or boxime == 'gb800ue':
		if recording == 1:
			singleled(config.rsi.recordled.value)
		elif hd == 1:
			singleled(config.rsi.hdled.value)
		else:
			singleled(config.rsi.normalled.value)

	if boxime == 'premium+' or boxime == 'ultra':
			if config.rsi.fanoff.value == 'alwaysoff':
				fanctl(0)
			else:
				fanctl(1)


class ledctl(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
				iPlayableService.evVideoSizeChanged: self.__evVideoSizeChanged
			})

		NavigationInstance.instance.record_event.append(self.getRecordEvent)
		config.misc.standbyCounter.addNotifier(self.standbyCounterChanged, initial_call=False)
		startup()

	def __evVideoSizeChanged(self):
		service = session.nav.getCurrentService()
		info = service and service.info()
		height = info and info.getInfo(iServiceInformation.sVideoHeight)
		print(height)
		self.screensize(info.getInfo(iServiceInformation.sVideoHeight))

	def getRecordEvent(self, recservice, event):
		recordings = len(NavigationInstance.instance.getRecordings())
		if event == iRecordableService.evEnd:
			if recordings == 0:
				self.recording(0)
		elif event == iRecordableService.evStart:
			if recordings > 0:
				self.recording(1)

	def standbyCounterChanged(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.leaveStandby)
		self.standby(1)

	def leaveStandby(self):
		self.standby(0)

	def recording(self, switch):
		global recording
		recording = switch
		if switch == 0:
			if boxime == 'premium+' or boxime == 'premium':
				if config.rsi.redled.value == 'recon':
					redled(0)
				if config.rsi.blueled.value == 'recon':
					blueled(0)
				if config.rsi.greenled.value == 'recon':
					greenled(0)
			elif boxime == 'ultra':
				if config.rsi.firstled.value == 'recon':
					firstled(0)
				if config.rsi.secondled.value == 'recon':
					secondled(0)
			elif boxime == 'me' or boxime == 'gb800ue':
				if standby == 1:
					singleled(config.rsi.standbyled.value)
				elif hd == 1:
					singleled(config.rsi.hdled.value)
				else:
					singleled(config.rsi.normalled.value)
		if switch == 1:
			if boxime == 'premium+' or boxime == 'premium':
				if (config.rsi.redled.value == 'recon' and standby == 0) or (config.rsi.redled.value == 'recon' and config.rsi.recstandby.value == True):
					redled(1)
				if (config.rsi.blueled.value == 'recon' and standby == 0) or (config.rsi.blueled.value == 'recon' and config.rsi.recstandby.value == True):
					blueled(1)
				if (config.rsi.greenled.value == 'recon' and standby == 0) or (config.rsi.greenled.value == 'recon' and config.rsi.recstandby.value == True):
					greenled(1)
			elif boxime == 'ultra':
				if (config.rsi.firstled.value == 'recon' and standby == 0) or (config.rsi.firstled.value == 'recon' and config.rsi.recstandby.value == True):
					firstled(1)
				if (config.rsi.secondled.value == 'recon' and standby == 0) or (config.rsi.secondled.value == 'recon' and config.rsi.recstandby.value == True):
					secondled(1)
			elif boxime == 'me' or boxime == 'gb800ue':
				if standby == 0 or config.rsi.recstandby.value == True:
					singleled(config.rsi.recordled.value)

	def standby(self, switch):
		global standby
		standby = switch
		if switch == 0:
			if boxime == 'premium+' or boxime == 'ultra':
				if config.rsi.fanoff.value == 'standbyoff':
					fanctl(1)
			if boxime == 'premium+' or boxime == 'premium':
				if config.rsi.redled.value == 'standbyoff' or (config.rsi.redled.value == 'hdon' and hd == 1) or (config.rsi.redled.value == 'recon' and recording == 1):
					redled(1)
				if config.rsi.blueled.value == 'standbyoff' or (config.rsi.blueled.value == 'hdon' and hd == 1) or (config.rsi.blueled.value == 'recon' and recording == 1):
					blueled(1)
				if config.rsi.greenled.value == 'standbyoff' or (config.rsi.greenled.value == 'hdon' and hd == 1) or (config.rsi.greenled.value == 'recon' and recording == 1):
					greenled(1)
			elif boxime == 'ultra':
				if config.rsi.firstled.value == 'standbyoff' or (config.rsi.firstled.value == 'hdon' and hd == 1) or (config.rsi.firstled.value == 'recon' and recording == 1):
					firstled(1)
				if config.rsi.secondled.value == 'standbyoff' or (config.rsi.secondled.value == 'hdon' and hd == 1) or (config.rsi.secondled.value == 'recon' and recording == 1):
					secondled(1)
			elif boxime == 'me' or boxime == 'gb800ue':
				if recording == 1:
					singleleddelayed(config.rsi.recordled.value)
				elif hd == 1:
					singleleddelayed(config.rsi.hdled.value)
				else:
					singleleddelayed(config.rsi.normalled.value)
		if switch == 1:
			if boxime == 'premium+' or boxime == 'ultra':
				if config.rsi.fanoff.value == 'standbyoff':
					fanctl(0)
			if boxime == 'premium+' or boxime == 'premium':
				if config.rsi.redled.value == 'standbyoff' or config.rsi.redled.value == 'hdon' or (config.rsi.redled.value == 'recon' and config.rsi.recstandby.value == False):
					redled(0)
				if config.rsi.blueled.value == 'standbyoff' or config.rsi.blueled.value == 'hdon' or (config.rsi.blueled.value == 'recon' and config.rsi.recstandby.value == False):
					blueled(0)
				if config.rsi.greenled.value == 'standbyoff' or config.rsi.greenled.value == 'hdon' or (config.rsi.greenled.value == 'recon' and config.rsi.recstandby.value == False):
					greenled(0)
			elif boxime == 'ultra':
				if config.rsi.firstled.value == 'standbyoff' or config.rsi.firstled.value == 'hdon' or (config.rsi.firstled.value == 'recon' and config.rsi.recstandby.value == False):
					firstled(0)
				if config.rsi.secondled.value == 'standbyoff' or config.rsi.secondled.value == 'hdon' or (config.rsi.secondled.value == 'recon' and config.rsi.recstandby.value == False):
					secondled(0)
			elif boxime == 'me' or boxime == 'gb800ue':
				if recording == 0 or config.rsi.recstandby.value == False:
					singleleddelayed(config.rsi.standbyled.value)

	def sizechanged(self, switch):
		if switch == 0:
			if boxime == 'premium+' or boxime == 'premium':
				if config.rsi.redled.value == 'hdon':
					redled(switch)
				if config.rsi.blueled.value == 'hdon':
					blueled(switch)
				if config.rsi.greenled.value == 'hdon':
					greenled(switch)
			elif boxime == 'ultra':
				if config.rsi.firstled.value == 'hdon':
					firstled(switch)
				if config.rsi.secondled.value == 'hdon':
					secondled(switch)
			elif (boxime == 'me' and recording == 0) or (boxime == 'gb800ue' and recording == 0):
				singleled(config.rsi.normalled.value)
		if switch == 1:
			if boxime == 'premium+' or boxime == 'premium':
				if config.rsi.redled.value == 'hdon':
					redled(switch)
				if config.rsi.blueled.value == 'hdon':
					blueled(switch)
				if config.rsi.greenled.value == 'hdon':
					greenled(switch)
			elif boxime == 'ultra':
				if config.rsi.firstled.value == 'hdon':
					firstled(switch)
				if config.rsi.secondled.value == 'hdon':
					secondled(switch)
			elif (boxime == 'me' and recording == 0) or (boxime == 'gb800ue' and recording == 0):
				singleled(config.rsi.hdled.value)

	def screensize(self, size):
		global screensize
		global hd
		if size != screensize:
			if size > 576:
				hd = 1
				self.sizechanged(1)
			else:
				hd = 0
				self.sizechanged(0)
		screensize = size


class RSIConfig(Screen, ConfigListScreen):

	def __init__(self, session):
		Screen.__init__(self, session)

		self.skinName = ["Setup"]

		self["actions"] = NumberActionMap(["SetupActions", "OkCancelActions", "ColorActions"],
		{
			"ok": self.keyOk,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"left": self.keyLeft,
			"right": self.keyRight
		}, -2)

		self.list = []
		self["config"] = ConfigList(self.list)

		if boxime != 'ultra':
			self.list.append(getConfigListEntry(_("Turn off VFD in standby"), config.rsi.vfdoffstandby))
		if boxime == 'premium+' or boxime == 'premium':
			self.list.append(getConfigListEntry(_("Red LED behaviour"), config.rsi.redled))
			self.list.append(getConfigListEntry(_("Blue LED behaviour"), config.rsi.blueled))
			self.list.append(getConfigListEntry(_("Green LED behaviour"), config.rsi.greenled))
		elif boxime == 'ultra':
			self.list.append(getConfigListEntry(_("First LED behaviour"), config.rsi.firstled))
			self.list.append(getConfigListEntry(_("Second LED behaviour"), config.rsi.secondled))
		elif boxime == 'me' or boxime == 'gb800ue':
			self.list.append(getConfigListEntry(_("Enable Keymap Helper (Please restart OpenRSi when changed)"), config.rsi.keymaphelper))
			self.list.append(getConfigListEntry(_("Normal LED color (SD)"), config.rsi.normalled))
			self.list.append(getConfigListEntry(_("Standby LED color"), config.rsi.standbyled))
			self.list.append(getConfigListEntry(_("Recording LED color"), config.rsi.recordled))
			self.list.append(getConfigListEntry(_("HD Channel LED color"), config.rsi.hdled))
		if boxime != 'elite':
			self.list.append(getConfigListEntry(_("Enable recording LED in standby"), config.rsi.recstandby))
		if boxime == 'premium+' or boxime == 'ultra':
			self.list.append(getConfigListEntry(_("Fan behaviour"), config.rsi.fanoff))
		if boxime == 'me' or boxime == 'gb800ue':
			self.list.append(getConfigListEntry(_(" "), config.rsi.empty))
			self.list.append(getConfigListEntry(_("---Set System and RTC Time---"), config.rsi.empty))
			self.list.append(getConfigListEntry(_("Sync using internet"), config.rsi.syncNTPtime))
			self.list.append(getConfigListEntry(_("Sync using current transponder"), config.rsi.syncDVBtime))
			self.list.append(getConfigListEntry(_("Set time manually"), config.rsi.syncManually))

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))

	def keyLeft(self):
		self["config"].handleKey(KEY_LEFT)

	def keyRight(self):
		self["config"].handleKey(KEY_RIGHT)

	def keyOk(self):
		sel = self["config"].getCurrent()[1]
		if sel == config.rsi.syncNTPtime:
			cmd = '/usr/lib/enigma2/python/Plugins/Extensions/RSIConfig/ntpupdate'
			self.session.open(MyConsole, _("Time sync with NTP..."), [cmd])
		if sel == config.rsi.syncDVBtime:
			cmd = '/usr/lib/enigma2/python/Plugins/Extensions/RSIConfig/dvbupdate'
			self.session.open(MyConsole, _("Time sync with Transponder..."), [cmd])
		if sel == config.rsi.syncManually:
			ChangeTimeWizzard(self.session)

	def keySave(self):
		config.rsi.save()
		startup(0)
		self.close()

	def keyCancel(self):
		self.close()


class MyConsole(Console):
	skin = """<screen position="center,center" size="500,240" title="Command execution..." >
		<widget name="text" position="10,10" size="485,230" font="Regular;20" />
		</screen>"""

	def __init__(self, session, title="My Console...", cmdlist=None):
		Console.__init__(self, session, title, cmdlist)


class ChangeTimeWizzard(Screen):
	def __init__(self, session):
		self.session = session
		jetzt = time.time()
		timezone = datetime.datetime.utcnow()
		delta = (jetzt - time.mktime(timezone.timetuple()))
		self.oldtime = strftime("%Y:%m:%d %H:%M", localtime())
		self.session.openWithCallback(self.askForNewTime, InputBox, title=_("Please Enter new System time and press OK !"), text="%s" % (self.oldtime), maxSize=16, type=Input.NUMBER)

	def askForNewTime(self, newclock):
		try:
			length = len(newclock)
		except:
			length = 0
		if newclock is None:
			self.close()
		elif (length == 16) is False:
			self.skipChangeTime(_("new time string too short"))
		elif (newclock.count(" ") < 1) is True:
			self.skipChangeTime(_("invalid format"))
		elif (newclock.count(":") < 3) is True:
			self.skipChangeTime(_("invalid format"))
		else:
			full = []
			full = newclock.split(" ", 1)
			newdate = full[0]
			newtime = full[1]
			parts = []
			parts = newdate.split(":", 2)
			newyear = parts[0]
			newmonth = parts[1]
			newday = parts[2]
			parts = newtime.split(":", 1)
			newhour = parts[0]
			newmin = parts[1]
			maxmonth = 31
			if (int(newmonth) == 4) or (int(newmonth) == 6) or (int(newmonth) == 9) or (int(newmonth) == 11) is True:
				maxmonth = 30
			elif (int(newmonth) == 2) is True:
				if ((4 * int(int(newyear) / 4)) == int(newyear)) is True:
					maxmonth = 28
				else:
					maxmonth = 27
			if (int(newyear) < 2007) or (int(newyear) > 2027) or (len(newyear) < 4) is True:
				self.skipChangeTime(_("invalid year %s") % newyear)
			elif (int(newmonth) < 0) or (int(newmonth) > 12) or (len(newmonth) < 2) is True:
				self.skipChangeTime(_("invalid month %s") % newmonth)
			elif (int(newday) < 1) or (int(newday) > maxmonth) or (len(newday) < 2) is True:
				self.skipChangeTime(_("invalid day %s") % newday)
			elif (int(newhour) < 0) or (int(newhour) > 23) or (len(newhour) < 2) is True:
				self.skipChangeTime(_("invalid hour %s") % newhour)
			elif (int(newmin) < 0) or (int(newmin) > 59) or (len(newmin) < 2) is True:
				self.skipChangeTime(_("invalid minute %s") % newmin)
			else:
				self.newtime = "%s%s%s%s%s" % (newmonth, newday, newhour, newmin, newyear)
				self.session.openWithCallback(self.DoChangeTimeRestart, MessageBox, _("Apply the new System time?"), MessageBox.TYPE_YESNO)

	def DoChangeTimeRestart(self, answer):
		if answer is None:
			self.skipChangeTime(_("answer is None"))
		if answer is False:
			self.close()
		else:
			os.system("date %s" % (self.newtime))
			cmd = '/usr/lib/enigma2/python/Plugins/Extensions/RSIConfig/manupdate'
			self.session.open(MyConsole, _("Setting Time..."), [cmd])

	def skipChangeTime(self, reason):
		self.session.open(MessageBox, (_("Change system time was canceled, because %s") % reason), MessageBox.TYPE_WARNING)

	def close(self):
		pass


class keymapper(Screen):
	def __init__(self, session):
		global newInfoBarPlugins__init__
		if boxime == 'me':
			keymapparser.readKeymap("/usr/lib/enigma2/python/Plugins/Extensions/RSIConfig/keymaps/azboxme.xml")
		elif boxime[:2] == 'gb':
			keymapparser.readKeymap("/usr/lib/enigma2/python/Plugins/Extensions/RSIConfig/keymaps/gigablue.xml")

		if newInfoBarPlugins__init__ is None:
			newInfoBarPlugins__init__ = InfoBarPlugins.__init__

		InfoBarPlugins.__init__ = InfoBarPlugins__init__
		InfoBarPlugins.showAzBoxPortal = showAzBoxPortal
		InfoBarPlugins.rtvswitch = rtvswitch


def InfoBarPlugins__init__(self):
	if isinstance(self, InfoBarEPG):
		self["shortcuts"] = ActionMap(["RSIConfigActions"],
		{
			"showAzBoxPortal": self.showAzBoxPortal,
			"rtvswitch": self.rtvswitch
		})

	newInfoBarPlugins__init__(self)


def showAzBoxPortal(self):
	self.session.open(AzBox_Portal)


def rtvswitch(self):
	if config.servicelist.lastmode.value == 'tv':
		print("RSI - Switch to Radio")
		InfoBar.showRadio(InfoBar.instance)
	elif config.servicelist.lastmode.value == 'radio':
		print("RSI - Switch to TV")
		InfoBar.showTv(InfoBar.instance)


class AzBox_Portal(Screen):
	skin = """
		<screen name="RSI_helper" position="center,center" size="200,100" title="RSI Keymap Helper">
		<widget source="menu" render="Listbox" zPosition="1" transparent="1" position="0,0" size="200,100" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"ok": self.okbuttonClick,
			"back": self.exit,
			"cancel": self.exit,
			"red": self.exit,
			"green": self.exit,
			"yellow": self.exit,
			"blue": self.exit,
		})

		list = []
		if config.servicelist.lastmode.value == 'tv':
			list.append((_("Switch to Radio"), "radio", "", "50"))
		elif config.servicelist.lastmode.value == 'radio':
			list.append((_("Switch to TV"), "tv", "", "50"))
		list.append((_("Recordings Player"), "recplayer", "", "50"))
		self["menu"] = List(list)

	def okbuttonClick(self):
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "radio":
				InfoBar.showRadio(InfoBar.instance)
				self.exit()
			if selection[1] == "tv":
				InfoBar.showTv(InfoBar.instance)
				self.exit()
			elif selection[1] == "recplayer":
				InfoBar.showMovies(InfoBar.instance)

	def exit(self):
		self.close()


def startConfig(session, **kwargs):
	session.open(RSIConfig)


def selSetup(menuid, **kwargs):
	if menuid != "setup":
		return []
	return [(_("RSI Configuration"), startConfig, "RSI Configuration Options", None)]


def autostart(reason, **kwargs):
	#"called with reason=1 to during shutdown, with reason=0 at startup?"
	if reason == 0:
		global session
		if "session" in kwargs:
			session = kwargs["session"]
			if config.rsi.keymaphelper.value == True:
				keymapper(session)

			ledctl(session)


def Plugins(**kwargs):
	list = []
	list.append(PluginDescriptor(name=_("RSI Configuration"), description=_("RSI Configuration Options"), where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=selSetup))
	list.append(PluginDescriptor(name=_("RSI Configuration"), description=_("RSI Configuration Options"), where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart))
	return list
