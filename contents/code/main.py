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
import re, random
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
        self.d_tempUnit = cg.readEntry("tempUnit", 0)
        
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
        self.cardname = Plasma.Frame(self.applet)
        self.cardname.setText(result[6])

        #some kind bug in QColor.setAlpha(), need a workaround.
        plotcolor = t_textcolor.getRgb()
        plotcolor = QColor(plotcolor[0], plotcolor[1], plotcolor[2], 220)
        
        self.chart1 = Plasma.SignalPlotter(self.applet)
        self.chart1.setTitle('GPU Load')
        self.chart1.setUseAutoRange(0)
        self.chart1.setVerticalRange(0, 100)
        self.chart1.setShowHorizontalLines(0)
        self.chart1.setShowVerticalLines(0)
        self.chart1.setFontColor(t_textcolor)
        self.chart1.setFont(QFont('Sans',8))
        self.chart1.setShowLabels(0)
        self.chart1.setThinFrame(0)
        self.chart1.setUnit('%')
        self.chart1.addPlot(plotcolor)
        self.chart1.setSvgBackground('widgets/plot-background')
        load = (int(result[2]))
        samples = [load,]
        self.chart1.addSample(samples)
        self.valueLabel1 = Plasma.Frame(self.chart1)
        self.valueLabel1.setFont(QFont('Sans',8))
        self.chart1.setLayout(self.valueLabelLayout(self.valueLabel1))
        self.valueLabel1.setText(result[2] + '%')
        
        self.chart2 = Plasma.SignalPlotter(self.applet)
        self.chart2.setTitle('GPU Temp')
        if self.d_tempUnit == 0:
            self.tempunit = u'℃'
            self.chart2.setVerticalRange(0, 110)
            degree = result[3]
        elif self.d_tempUnit == 1:
            self.tempunit = 'F'
            self.chart2.setVerticalRange(0, 230)
            degree = self.c2f(result[3])
        else:
            self.tempunit = u'℃'
        self.chart2.setUseAutoRange(0)
        self.chart2.setShowVerticalLines(0)
        self.chart2.setShowHorizontalLines(0)
        self.chart2.setFontColor(t_textcolor)
        self.chart2.setFont(QFont('Sans',8))
        self.chart2.setShowLabels(0)
        self.chart2.setThinFrame(0)
        self.chart2.setUnit(self.tempunit)
        self.chart2.addPlot(plotcolor)
        self.chart2.setSvgBackground('widgets/plot-background')
        temp = (float(degree))
        samples = [temp,]
        self.chart2.addSample(samples)
        self.valueLabel2 = Plasma.Frame(self.chart2)
        self.valueLabel2.setFont(QFont('Sans',8))
        self.chart2.setLayout(self.valueLabelLayout(self.valueLabel2))
        self.valueLabel2.setText(degree + self.tempunit)
        
        self.chart3 = Plasma.SignalPlotter(self.applet)
        self.chart3.setTitle("Core Clock")
        self.chart3.setUseAutoRange(0)
        self.chart3.setVerticalRange(0, int(result[4]))
        self.chart3.setShowVerticalLines(0)
        self.chart3.setShowHorizontalLines(0)
        self.chart3.setFontColor(t_textcolor)
        self.chart3.setFont(QFont('Sans',8))
        self.chart3.setShowLabels(0)
        self.chart3.setThinFrame(0)
        self.chart3.setUnit("MHz")
        self.chart3.addPlot(plotcolor)
        self.chart3.setSvgBackground('widgets/plot-background')
        corecl = (int(result[0]))
        samples = [corecl,]
        self.chart3.addSample(samples)
        self.valueLabel3 = Plasma.Frame(self.chart3)
        self.valueLabel3.setFont(QFont('Sans',8))
        self.chart3.setLayout(self.valueLabelLayout(self.valueLabel3))
        self.valueLabel3.setText(result[0] + 'MHz')
        
        self.chart4 = Plasma.SignalPlotter(self.applet)
        self.chart4.setTitle("Memory Clock")
        self.chart4.setUseAutoRange(0)
        self.chart4.setVerticalRange(0, int(result[5]))
        self.chart4.setShowVerticalLines(0)
        self.chart4.setShowHorizontalLines(0)
        self.chart4.setFontColor(t_textcolor)
        self.chart4.setFont(QFont('Sans',8))
        self.chart4.setShowLabels(0)
        self.chart4.setThinFrame(0)
        self.chart4.setUnit("MHz")
        self.chart4.addPlot(plotcolor)
        self.chart4.setSvgBackground('widgets/plot-background')
        memcl = (int(result[1]))
        samples = [memcl,]
        self.chart4.addSample(samples)
        self.valueLabel4 = Plasma.Frame(self.chart4)
        self.valueLabel4.setFont(QFont('Sans',8))
        self.chart4.setLayout(self.valueLabelLayout(self.valueLabel4))
        self.valueLabel4.setText(result[1] + 'MHz')
        
        self.layout.addItem(self.cardname)
        self.layout.addItem(self.chart1)
        self.layout.addItem(self.chart2)
        self.layout.addItem(self.chart3)
        self.layout.addItem(self.chart4)
        self.setLayout(self.layout)
        
        timer = QTimer(self)
        self.connect(timer, SIGNAL("timeout()"), self.updateTime)
        timer.start(d_refreshtime[0] * 1000) # update every x seconds
        
    def getresult(self):
        try:
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
                    gt = ('%.1f' % float(gt[4])) # gpu temperature
            return ccc, ccr, gl, gt, cpc, cpr, dar
        except OSError:
            #fake data source for developing
            dar = 'Developing Mode'
            ccc = str(random.randrange(500,700,50))
            ccr = '993'
            cpc = '700'
            cpr = '993'
            gl = str(random.randint(0,100))
            gt = '%.1f' % random.uniform(30,70)
            return ccc, ccr, gl, gt, cpc, cpr, dar
    
    def updateTime(self):
        result = self.getresult()
        load = (int(result[2]))
        samples = [load,]
        self.chart1.addSample(samples)
        self.valueLabel1.setText(result[2] + '%')
        
        temp = (float(result[3]))
        samples = [temp,]
        self.chart2.addSample(samples)
        if self.d_tempUnit == 1:
            degree = self.c2f(result[3])
            self.valueLabel2.setText(degree + self.tempunit)
        else:
            self.valueLabel2.setText(result[3] + self.tempunit)

        corecl = (int(result[0]))
        samples = [corecl,]
        self.chart3.addSample(samples)
        self.valueLabel3.setText(result[0] + 'MHz')

        memcl = (int(result[1]))
        samples = [memcl,]
        self.chart4.addSample(samples)
        self.valueLabel4.setText(result[1] + 'MHz')
        
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
        
    def c2f(self, degree):
        #convert Celsius to Fahrenheit
        degree = float(degree) * 9 / 5 + 32
        return str(degree)
    
    def valueLabelLayout(self, valueLabel):
        hl = QGraphicsLinearLayout(Qt.Horizontal)
        hl.addStretch()
        hl.addItem(valueLabel)
        hl.addStretch()
        vl = QGraphicsLinearLayout(Qt.Vertical)
        vl.addStretch()
        vl.addItem(hl)
        return vl
 
def CreateApplet(parent):
    return ATImon(parent)
