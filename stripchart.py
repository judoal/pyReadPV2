# (c) MIT License Copyright 2014 Ronald H Longo
# Please reuse, modify or distribute freely.
# http://code.activestate.com/recipes/578871-simple-tkinter-strip-chart-python-3/ 

from collections import OrderedDict
import tkinter as tk
import time
import logging
import readpvthread1 as rpt
import threading as Thread
import socket


class StripChart(tk.Frame):

   def __init__(self, parent, scale, historySize, trackColors, *args, **opts):
      # Initialize
      super().__init__(parent, *args, **opts)
      self._trackHist = OrderedDict()  # Map: TrackName -> list of canvas objID 
      self._trackColor = trackColors  # Map: Track Name -> color
      
      self._chartHeight = scale + 1
      self._chartLength = historySize * 2  # Stretch for readability

      self._canvas = tk.Canvas(self, height=self._chartHeight + 17,
                                width=self._chartLength, background='black')
      self._canvas.grid(sticky=tk.N + tk.S + tk.E + tk.W)
      
      # Draw horizontal to divide plot from tick labels
      x=0
      y = self._chartHeight + 2
      x2, y2 = self._chartLength, y
      self._baseLine = self._canvas.create_line(x, y, x2, y2, fill='white')
      
      # Init track def and histories lists
      self._trackColor.update({ 'tick':'white', 'tickline':'white',
                                 'ticklabel':'white' })
      for trackName in self._trackColor.keys():
         self._trackHist[ trackName ] = [ None for x in range(historySize) ]
         


   def plotValues(self, **vals):
      for trackName, trackHistory in self._trackHist.items():
         # Scroll left-wards
         self._canvas.delete(trackHistory.pop(0))
              # Remove left-most canvas objs
         self._canvas.move(trackName, -2, 0)
              # Scroll canvas objs 2 pixels left
         
         # Plot the new values
         try:
            val = vals[ trackName ]
            print (val)
            x = self._chartLength
            y = self._chartHeight - val
            color = self._trackColor[ trackName ]
            
            objId = self._canvas.create_line(x, y, x + 1, y, fill=color,
                                              width=3, tags=trackName)
            trackHistory.append(objId)
         except:
            trackHistory.append(None)

   def drawTick(self, text=None, **lineOpts):
      # draw vertical tick line
      x = self._chartLength
      y = 1
      x2 = x
      y2 = self._chartHeight
      color = self._trackColor[ 'tickline' ]
      
      objId = self._canvas.create_line(x, y, x2, y2, fill=color,
                                        tags='tick', **lineOpts)
      self._trackHist[ 'tickline' ].append(objId)
      
      # draw tick label
      x = self._chartLength
      y = self._chartHeight + 10
      color = self._trackColor[ 'ticklabel' ]
         
      objId = self._canvas.create_text(x, y, text=text, fill=color, tags='tick')
      self._trackHist[ 'ticklabel' ].append(objId)

   def configTrackColors(self, **trackColors):
      # Change plotted data color
      for trackName, colorName in trackColors.items():
         self._canvas.itemconfigure(trackName, fill=colorName)
      
      # Change settings so future data has the new color
      self._trackColor.update(trackColors)

#******************************


if __name__ == '__main__':
    t = Thread.Thread(target=rpt.Reader.main)
    t.start()
    time.sleep(2)
    
    top = tk.Tk()
    graph = StripChart(top, 1000, 600, { 'A':'orange'})  # , 'B':'green', 'C':'red' })
    graph.grid()
    
    val_A = 0
#    val_B = 0
#    val_C = 0
#    delta = [ -3, -2, -1, 0, 1, 2, 3 ]  # randomly vary the values by one of these
    tickCount = 0
#    current = "" 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 8001))

    def nextVal(current, lowerBound, upperBound):
     
 #       from random import choice      
 #       current += choice(delta) 
        s.sendall("Hello".encode('utf-8'))
        val = int(s.recv(1024))
#        val=current * 2
        print(val)
        val /= 10
        if val < lowerBound:   
            print("lbound: " + str(lowerBound))       
            return lowerBound
        elif val > upperBound:
           print("ubound: " + str(upperBound))
           return upperBound
        else:
           return val

    def plotNextVals():
        global val_A, tickCount#, val_B, val_C, 
    
        if tickCount % 50 == 0:
          graph.drawTick(text=str(tickCount), dash=(1, 4))
        tickCount += 1
       
        val_A = nextVal(val_A, 0, 5000) 
 #      val_B = nextVal(val_B, 0, 99)
 #      val_C = nextVal(val_C, 0, 99)
        graph.plotValues(A=val_A)  # , B=val_B, C=val_C)
       
       # changeColor = { 800: 'black',
         # 1200: 'yellow',
         # 1600: 'orange',
         # 2000: 'white',
         # 2400: 'brown',
         # 2800: 'blue' }
       # if tickCount in changeColor:
          # graph.configTrackColors( A=changeColor[tickCount] )
       
        top.after(500, plotNextVals)
    
    top.after(500, plotNextVals)   
    top.mainloop()

