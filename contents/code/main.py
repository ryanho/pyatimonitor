# -*- coding: utf-8 -*-

""" pyATImonitor. This is a simple widget for KDE SC 4.3 and above that 
    using ATI catalyst driver to monitor core clocks, memory clocks,
    gpu usage and core temperature.
    
    Copyright (C) 2009  Ryan Ho <koungho@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from subprocess import Popen, PIPE
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

class ATImon(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
 
    def init(self):
        #self.resize(-1,-1)
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
 
        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        #self.setBackgroundHints(Plasma.Applet.DefaultBackground)
        #self.setBackgroundHints(Plasma.Applet.NoBackground)
        #self.setBackgroundHints(Plasma.Applet.StandardBackground)
        self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
        #self.icon = Plasma.IconWidget()
        
        result = self.getresult()
 
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
        self.meter1 = Plasma.Meter(self.applet)
        self.meter1.setMeterType(Plasma.Meter.BarMeterHorizontal)
        self.meter1.setLabel(0,'GPU load')
        self.meter1.setLabel(1, result[2] + '%')
        self.meter1.setLabelFont(0,QFont('Sans',8))
        self.meter1.setMinimum(0)
        self.meter1.setMaximum(100)
        self.meter1.setValue(int(result[2]))
        self.meter2 = Plasma.Meter(self.applet)
        self.meter2.setMeterType(Plasma.Meter.BarMeterHorizontal)
        self.meter2.setLabel(1,result[3] + u'℃')
        self.meter2.setLabel(0,'GPU temp.')
        self.meter2.setLabelFont(0,QFont('Sans',8))
        self.meter2.setMinimum(0)
        self.meter2.setMaximum(110)
        self.meter2.setValue(int(result[3]))
        self.meter3 = Plasma.Meter(self.applet)
        self.meter3.setMeterType(Plasma.Meter.BarMeterHorizontal)
        self.meter3.setLabel(1,result[0] + 'MHz')
        self.meter3.setLabel(0,'Core Clock')
        self.meter3.setLabelFont(0,QFont('Sans',8))
        self.meter3.setMaximum(int(result[4]))
        self.meter3.setValue(int(result[0]))
        self.meter4 = Plasma.Meter(self.applet)
        self.meter4.setMeterType(Plasma.Meter.BarMeterHorizontal)
        self.meter4.setLabel(1,result[1] + 'MHz')
        self.meter4.setLabel(0,'Memory Clock')
        self.meter4.setLabelFont(0,QFont('Sans',8))
        self.meter4.setMaximum(int(result[5]))
        self.meter4.setValue(int(result[1]))
        self.layout.addItem(self.meter3)
        self.layout.addItem(self.meter4)
        self.layout.addItem(self.meter1)
        self.layout.addItem(self.meter2)
        self.setLayout(self.layout)
        
        timer = QTimer(self)
        self.connect(timer, SIGNAL("timeout()"), self.updateTime)
        timer.start(2000) # update every 2 seconds
        
        self.Dialog = PopupDialog()
        self.Dialog.init()
        self.Dialog.setBody(result[6])
        self.dialogTimer = QTimer()
        self.connect(self, SIGNAL("timeout()"), self.showDialog)
        
    def hoverEnterEvent(self, event):
        self.dialogTimer.start(1000)  
    
    def showDialog(self):
        self.Dialog.move(self.popupPosition(self.Dialog.sizeHint()))
        self.Dialog.showDialog()
    
    def hoverLeaveEvent(self, event):
        self.dialogTimer.stop()
        self.Dialog.hide()
        
    def getresult(self):
        # run aticonfig and get result from PIPE
        result = Popen(['aticonfig','--odgc','--odgt'], stdin=PIPE, stdout=PIPE, stderr=PIPE).stdout.read().split('\n')
        for i in result:
            if re.search(r'Default Adapter', i):
                da = i.split(' - ')
                dar = da[1] # default adapter name
            if re.search(r' *Current Clocks', i):
                cc = i.strip().split()
                ccc = cc[3] # current clock of core
                ccr = cc[4] # current clock of memory
            if re.search(r' Current Peak', i):
                cp = i.strip().split()
                cpc = cp[3] # current peak of core
                cpr = cp[4] # current peak of memory
            if re.search(r' *GPU load', i):
                gl = i.replace('%','').strip().split()
                gl = gl[3] # gpu load
            if re.search(r' *Sensor', i):
                gt = i.strip().split()
                gt = ('%.0f' % float(gt[4])) # gpu temperature
        return ccc, ccr, gl, gt, cpc, cpr, dar
    
    def updateTime(self):
        result = self.getresult()
        self.meter1.setLabel(1, result[2] + '%')
        self.meter1.setValue(int(result[2]))
        self.meter2.setLabel(1,result[3] + u'℃')
        self.meter2.setValue(int(result[3]))
        self.meter3.setLabel(1,result[0] + 'MHz')
        self.meter3.setValue(int(result[0]))
        self.meter4.setLabel(1,result[1] + 'MHz')
        self.meter4.setValue(int(result[1]))
        
class PopupDialog(Plasma.Dialog):
    def init(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        
        layout = QVBoxLayout(self)
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        self.body = QLabel()
        layout.addWidget(self.body)
        
        self.setLayout(layout)
        
    def setTitle(self, s):
        if s == "":
            self.title.setText("")
        else:
            self.title.setText("<b>"+s+"</b>")
        
    def setBody(self, s):
        self.body.setText(s)
        
    def showDialog(self):
        if self.title.text() == "" and self.body.text() == "":
           pass
        else:
            self.show()
 
def CreateApplet(parent):
    return ATImon(parent)