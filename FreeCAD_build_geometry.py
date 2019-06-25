# -*- coding: utf-8 -*-
#copyright, GPL
# Qingfeng Xia  Oxford

from __future__ import print_function, division

"""
simple script to let FreeCAD generate CAD file by commandline

## use in FreeCAD GUI

FreeCAD GUI will boot up, but it is good to debug the script, see where the script stuck.
If everything goes well, this script will close the FreeCAD gui, as requested in batch mode automation

1. paste this into FreeCAD python console:
exec(open('/home/qxia/Documents/StepMultiphysics/fc_bool_fragments.py').read())

2. or make this script as FreeCAD Macro (*.FCMacro), but it takes extra step in GUI

3. or in terminal:  freecad this_script.py  (this script will be run in twice), it is recommended to run in Editor mode as below.
this script seems run twice in gui mode, The reason is not known yet.   run in GUI editor mode / console mode instead

4. or editor mode:  in FreeCAD GUI, File->Open... open this file into python editor windows and then run this script uisng Macro run toolbar
 in this mode, error or exception can show its occuring line number in console/status bar

## use in console mode

For some cases, long time computation will freeze the desktop in GUI mode
To be able to run in both GUI and console mode, using this conditioanal script
`if FreeCAD.GuiUp: `
to run in console mode without GUI:  `freecadcmd this_script.py` can avoid this situation

`python3 -m  this_script.py`  # uisng python2 if you FreeCAD is built with python2, 
this may fail because python files in each module are not loaded into search path!

"""


import sys
import os.path

## this section is needed only if called directly from `python3 -m  this_script.py`
if os.path.exists('/usr/lib/freecad/lib'):
    print('found FreeCAD stable  on system')
    sys.path.append('/usr/lib/freecad/lib')
elif os.path.exists('/usr/lib/freecad-daily/lib'):
    sys.path.append('/usr/lib/freecad-daily/lib')
    print('found FreeCAD-daily on system')
else:
    print('no FreeCAD stable or daily build is found on system, please install')

import FreeCAD
import FreeCAD as App
import Part
if FreeCAD.GuiUp:  # use this cond to enclosure all Gui commands
    import FreeCADGui as Gui  # it is better to keep the GUI
    #


###############copied from FreeCAD recorded macro file##############

App.newDocument("Unnamed")  # in GUI mode, setActiveDocument() is done automatically
if not FreeCAD.GuiUp:  
    App.setActiveDocument("Unnamed")
    App.ActiveDocument=App.getDocument("Unnamed")
    #Gui.ActiveDocument=Gui.getDocument("Unnamed")
else:
    Gui.activateWorkbench("PartWorkbench")

App.ActiveDocument.addObject("Part::Box","Box")
App.ActiveDocument.ActiveObject.Label = "Cube"
App.ActiveDocument.recompute()
#Gui.SendMsgToActiveView("ViewFit")

App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
App.ActiveDocument.ActiveObject.Label = "Cylinder"
App.ActiveDocument.recompute()
#Gui.SendMsgToActiveView("ViewFit")

# can not import this module, if this script is not called from FreeCAD
import BOPTools.SplitFeatures
j = BOPTools.SplitFeatures.makeBooleanFragments(name= 'BooleanFragments')
j.Objects = [App.ActiveDocument.Box, App.ActiveDocument.Cylinder]
j.Mode = 'Standard'
j.Proxy.execute(j)
j.purgeTouched()

__objs__=[]
__objs__.append(FreeCAD.getDocument("Unnamed").getObject("BooleanFragments"))
import Part
Part.export(__objs__,u"./a.brep")

del __objs__

print('this script complete sucessfully')
######################### end of paste ##############################
'''
# exit FreeCAD, only after you have done the debugging
FreeCAD.closeDocument('Unnamed')
if FreeCAD.GuiUp:
    Gui.doCommand('exit(0)')  # another way to exit
'''