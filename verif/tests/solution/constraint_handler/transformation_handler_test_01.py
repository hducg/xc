# -*- coding: utf-8 -*-
# Test from Ansys manual
# Reference:  Strength of Material, Part I, Elementary Theory & Problems, pg. 26, problem 10

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2014, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

E= 30e6 # Young modulus (psi)
l= 10 # Bar length in inches
a= 0.3*l # Length of tranche a
b= 0.3*l # Length of tranche b
F1= 1000 # Force magnitude 1 (pounds)
F2= 1000/2 # Force magnitude 2 (pounds)

import xc_base
import geom
import xc
from model import predefined_spaces
from solution import predefined_solutions
from materials import typical_materials


# Model definition
prueba= xc.ProblemaEF()
preprocessor=  prueba.getPreprocessor
nodes= preprocessor.getNodeLoader
# Problem type
modelSpace= predefined_spaces.SolidMechanics2D(nodes)

nodes.defaultTag= 1 #First node number.
nod= nodes.newNodeXY(0,0)
nod= nodes.newNodeXY(0.0,l-a-b)
nod= nodes.newNodeXY(0.0,l-a)
nod= nodes.newNodeXY(0.0,l)

# Materials definition
elast= typical_materials.defElasticMaterial(preprocessor, "elast",E)
    
''' We define nodes at the points where loads will be applied.
    We will not compute stresses so we can use an arbitrary
    cross section of unit area.'''
    
# Elements definition
elements= preprocessor.getElementLoader
elements.defaultMaterial= "elast"
elements.dimElem= 2 # Dimension of element space
#  sintaxis: truss[<tag>] 
elements.defaultTag= 1 #Tag for the next element.
truss= elements.newElement("truss",xc.ID([1,2]));
truss.area= 1
truss= elements.newElement("truss",xc.ID([2,3]));
truss.area= 1
truss= elements.newElement("truss",xc.ID([3,4]));
truss.area= 1
    
# Constraints
constraints= preprocessor.getConstraintLoader
#
spc= constraints.newSPConstraint(1,0,0.0) # Node 1
spc= constraints.newSPConstraint(1,1,0.0)
spc= constraints.newSPConstraint(4,0,0.0) # Node 4
spc= constraints.newSPConstraint(4,1,0.0)
spc= constraints.newSPConstraint(2,0,0.0) # Node 2
spc= constraints.newSPConstraint(3,0,0.0) # Node 3


# Loads definition
cargas= preprocessor.getLoadLoader
casos= cargas.getLoadPatterns
#Load modulation.
ts= casos.newTimeSeries("constant_ts","ts")
casos.currentTimeSeries= "ts"
lp0= casos.newLoadPattern("default","0")
lp0.newNodalLoad(2,xc.Vector([0,-F2]))
lp0.newNodalLoad(3,xc.Vector([0,-F1]))
#We add the load case to domain.
casos.addToDomain("0")

# Solution procedure
import os
pth= os.path.dirname(__file__)
#print "pth= ", pth
if(not pth):
  pth= "."
execfile(pth+"/../../aux/solu_transf_handler.py")




nodes.calculateNodalReactions(True)
nodes= preprocessor.getNodeLoader
R1= nodes.getNode(4).getReaction[1] 
R2= nodes.getNode(1).getReaction[1] 


ratio1= R1/900
ratio2= R2/600
    
''' 
print "R1= ",R1
print "R2= ",R2
print "ratio1= ",(ratio1)
print "ratio2= ",(ratio2)
'''
    
import os
from miscUtils import LogMessages as lmsg
fname= os.path.basename(__file__)
if (abs(ratio1-1.0)<1e-5) & (abs(ratio2-1.0)<1e-5):
  print "test ",fname,": ok."
else:
  lmsg.error(fname+' ERROR.')
