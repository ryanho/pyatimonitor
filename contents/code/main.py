# -*- coding: utf-8 -*-

""" pyATImonitor. This is a simple widget for KDE SC 4.3 and above that 
    using ATI catalyst driver to monitor core clocks, memory clocks,
    gpu usage and core temperature.
    
    Copyright (C) 2009 Ryan Ho <koungho@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2 as 
    published by the Free Software Foundation.

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
        self.resize(250, 400)
        self.connect(Plasma.Theme.defaultTheme(), SIGNAL("themeChanged()"), self.themeChanged)
        
        #load value from default theme, make this widget suit it
        theme = Plasma.Theme.defaultTheme()
        t_textcolor = theme.color(Plasma.Theme.TextColor)
        
        #load config
        cg = self.config()
        d_refreshtime = cg.readEntry("refreshtime", 2).toInt()
        d_bgStyle = cg.readEntry("bgStyle", 1)
        self.d_tempUnit = cg.readEntry("tempUnit", 1)
        
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        
        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        if d_bgStyle == 0:
            self.setBackgroundHints(Plasma.Applet.NoBackground)
        elif d_bgStyle == 1:
            self.setBackgroundHints(Plasma.Applet.StandardBackground)
        elif d_bgStyle == 2:
            self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
        else:
            self.setBackgroundHints(Plasma.Applet.StandardBackground)
        
        #self.icon = Plasma.IconWidget()
        
        result = self.getresult()
 
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
        self.cardname = Plasma.Label(self.applet)
        self.cardname.setText(result[6])
        self.cardname.setAlignment(Qt.AlignHCenter)
#        self.meter1 = Plasma.Meter(self.applet)
#        self.meter1.setMeterType(Plasma.Meter.BarMeterHorizontal)
#        self.meter1.setLabel(0,'GPU load')
#        self.meter1.setLabel(1, result[2] + '%')
#        self.meter1.setLabelFont(0, QFont('Sans',8))
#        self.meter1.setLabelColor(0, t_textcolor)
#        self.meter1.setMinimum(0)
#        self.meter1.setMaximum(100)
#        self.meter1.setValue(int(result[2]))
#        self.meter2 = Plasma.Meter(self.applet)
#        self.meter2.setMeterType(Plasma.Meter.BarMeterHorizontal)
#        if self.d_tempUnit == 1:
#            tempUnit = u'℃'
#            self.meter2.setLabel(1,result[3] + tempUnit)
#            self.meter2.setMaximum(110)
#        elif self.d_tempUnit == 2:
#            tempUnit = u'℉'
#            self.meter2.setLabel(1,self.c2f(result[3]) + tempUnit)
#            self.meter2.setMaximum(230)
#        self.meter2.setLabel(0,'GPU temp.')
#        self.meter2.setLabelFont(0, QFont('Sans',8))
#        self.meter2.setLabelColor(0, t_textcolor)
#        self.meter2.setMinimum(0)
#        self.meter2.setValue(float(result[3]))
#        self.meter3 = Plasma.Meter(self.applet)
#        self.meter3.setMeterType(Plasma.Meter.BarMeterHorizontal)
#        self.meter3.setLabel(1, result[0] + 'MHz')
#        self.meter3.setLabel(0, 'Core Clock')
#        self.meter3.setLabelFont(0,QFont('Sans',8))
#        self.meter3.setLabelColor(0,t_textcolor)
#        self.meter3.setMaximum(int(result[4]))
#        self.meter3.setValue(int(result[0]))
#        self.meter4 = Plasma.Meter(self.applet)
#        self.meter4.setMeterType(Plasma.Meter.BarMeterHorizontal)
#        self.meter4.setLabel(1, result[1] + 'MHz')
#        self.meter4.setLabel(0, 'Memory Clock')
#        self.meter4.setLabelFont(0,QFont('Sans',8))
#        self.meter4.setLabelColor(0,t_textcolor)
#        self.meter4.setMaximum(int(result[5]))
#        self.meter4.setValue(int(result[1]))

        #some kind bug in QColor.setAlpha(), need a workaround.
        plotcolor = t_textcolor.getRgb()
        plotcolor = QColor(plotcolor[0], plotcolor[1], plotcolor[2], 125)
        
        self.chart1 = Plasma.SignalPlotter(self.applet)
        self.chart1.setTitle('GPU Load')
        self.chart1.setUseAutoRange(1)
        self.chart1.setVerticalRange(0, 100)
        self.chart1.setShowHorizontalLines(0)
        self.chart1.setShowVerticalLines(0)
        self.chart1.setFontColor(t_textcolor)
        self.chart1.setFont(QFont('Sans',8))
        self.chart1.setShowLabels(1)
        self.chart1.setThinFrame(1)
        self.chart1.setUnit('%')
        self.chart1.addPlot(plotcolor)
        self.chart1.setSvgBackground('widgets/plot-background')
        load = (int(result[2]))
        samples = [load,]
        self.chart1.addSample(samples)
        self.chart2 = Plasma.SignalPlotter(self.applet)
        self.chart2.setTitle('GPU Temp')
        self.chart2.setUseAutoRange(0)
        self.chart2.setVerticalRange(0, 110)
        self.chart2.setShowVerticalLines(0)
        self.chart2.setShowHorizontalLines(0)
        self.chart2.setFontColor(t_textcolor)
        self.chart2.setFont(QFont('Sans',8))
        self.chart2.setShowLabels(1)
        self.chart2.setThinFrame(1)
        self.chart2.setUnit("C")
        self.chart2.addPlot(plotcolor)
        self.chart2.setSvgBackground('widgets/plot-background')
        temp = (int(result[3]))
        samples = [temp,]
        self.chart2.addSample(samples)
        self.chart3 = Plasma.SignalPlotter(self.applet)
        self.chart3.setTitle("Core Clock")
        self.chart3.setUseAutoRange(0)
        self.chart3.setVerticalRange(0, int(result[4]))
        self.chart3.setShowVerticalLines(0)
        self.chart3.setShowHorizontalLines(0)
        self.chart3.setFontColor(t_textcolor)
        self.chart3.setFont(QFont('Sans',8))
        self.chart3.setShowLabels(1)
        self.chart3.setThinFrame(1)
        self.chart3.setUnit("MHz")
        self.chart3.addPlot(plotcolor)
        self.chart3.setSvgBackground('widgets/plot-background')
        corecl = (int(result[0]))
        samples = [corecl,]
        self.chart3.addSample(samples)
        self.chart4 = Plasma.SignalPlotter(self.applet)
        self.chart4.setTitle("Memory Clock")
        self.chart4.setUseAutoRange(0)
        self.chart4.setVerticalRange(0, int(result[5]))
        self.chart4.setShowVerticalLines(0)
        self.chart4.setShowHorizontalLines(0)
        self.chart4.setFontColor(t_textcolor)
        self.chart4.setFont(QFont('Sans',8))
        self.chart4.setShowLabels(1)
        self.chart4.setThinFrame(1)
        self.chart4.setUnit("MHz")
        self.chart4.addPlot(plotcolor)
        self.chart4.setSvgBackground('widgets/plot-background')
        memcl = (result[1])
        samples = [memcl,]
        self.chart4.addSample(samples)
        self.layout.addItem(self.cardname)
#        self.layout.addItem(self.meter3)
#        self.layout.addItem(self.meter4)
#        self.layout.addItem(self.meter1)
#        self.layout.addItem(self.meter2)
        self.layout.addItem(self.chart1)
        self.layout.addItem(self.chart2)
        self.layout.addItem(self.chart3)
        self.layout.addItem(self.chart4)
        self.setLayout(self.layout)
        
        timer = QTimer(self)
        self.connect(timer, SIGNAL("timeout()"), self.updateTime)
        timer.start(d_refreshtime[0] * 1000) # update every x seconds
        
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
#        self.meter1.setLabel(1, result[2] + '%')
#        self.meter1.setValue(int(result[2]))
#        if self.d_tempUnit == 1:
#            tempUnit = u'℃'
#            self.meter2.setLabel(1,result[3] + tempUnit)
#        elif self.d_tempUnit == 2:
#            tempUnit = u'℉'
#            self.meter2.setLabel(1,self.c2f(result[3]) + tempUnit)
#        self.meter2.setValue(float(result[3]))
#        self.meter3.setLabel(1,result[0] + 'MHz')
#        self.meter3.setValue(int(result[0]))
#        self.meter4.setLabel(1,result[1] + 'MHz')
#        self.meter4.setValue(int(result[1]))
        load = (int(result[2]))
        samples = [load,]
        self.chart1.addSample(samples)
        
        temp = (int(result[3]))
        samples = [temp,]
        self.chart2.addSample(samples)

        corecl = (int(result[0]))
        samples = [corecl,]
        self.chart3.addSample(samples)

        memcl = (int(result[1]))
        samples = [memcl,]
        self.chart4.addSample(samples) 
        
    def themeChanged(self):
        theme = Plasma.Theme.defaultTheme()
        t_textcolor = theme.color(Plasma.Theme.TextColor)
        t_bgcolor = theme.color(Plasma.Theme.BackgroundColor) 
        self.chart1.setFontColor(t_textcolor)
        self.chart1.setBackgroundColor(t_textcolor)
        self.chart2.setFontColor(t_textcolor)
        self.chart2.setBackgroundColor(t_textcolor)
        self.chart3.setFontColor(t_textcolor)
        self.chart3.setBackgroundColor(t_textcolor)
        self.chart4.setFontColor(t_textcolor)
        self.chart4.setBackgroundColor(t_textcolor)
        #self.meter1.setLabelColor(0, t_textcolor)
        #self.meter2.setLabelColor(0, t_textcolor)
        #self.meter3.setLabelColor(0, t_textcolor)
        #self.meter4.setLabelColor(0, t_textcolor)
        
    def c2f(self, degree):
        #convert Celsius to Fahrenheit
        degree = float(degree) * 9 / 5 + 32
        return str(degree)
 
def CreateApplet(parent):
    return ATImon(parent)
