# -*- coding: utf-8 -*-
# Tomado del Ejemplo A47 del SOLVIA Verification Manual
import xc_base
import geom
import xc

from model import predefined_spaces
from solution import predefined_solutions
from materials import typical_materials
import math

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2014, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

L= 1 # Cantilever length in meters
b= 0.05 # Cross section width in meters
h= 0.10 # Cross section depth in meters
A= b*h # Cross section area en m2
I= 1/12.0*b*h**3 # Moment of inertia in m4
theta= math.radians(30)
E=2.0E11 # Elastic modulus in N/m2
dens= 7800 # Steel density in kg/m3
m= A*dens

NumDiv= 10
# Problem type
prueba= xc.ProblemaEF()
preprocessor=  prueba.getPreprocessor
nodes= preprocessor.getNodeLoader
modelSpace= predefined_spaces.StructuralMechanics2D(nodes)

# Define materials
scc= typical_materials.defElasticSection2d(preprocessor, "scc",A,E,I)


nodes.newSeedNode()

# Geometric transformation(s)
lin= modelSpace.newLinearCrdTransf("lin")

# Seed element definition
seedElemLoader= preprocessor.getElementLoader.seedElemLoader
seedElemLoader.defaultMaterial= "scc"
seedElemLoader.defaultTransformation= "lin"
seedElemLoader.defaultTag= 1 #Number for the next element will be 1.
beam2d= seedElemLoader.newElement("elastic_beam_2d",xc.ID([0,0]))
beam2d.h= h
beam2d.rho= m


points= preprocessor.getCad.getPoints
pt= points.newPntIDPos3d(1,geom.Pos3d(0.0,0.0,0.0))
pt= points.newPntIDPos3d(2,geom.Pos3d(L*math.cos(theta),L*math.sin(theta),0.0))
lines= preprocessor.getCad.getLines
lines.defaultTag= 1
l= lines.newLine(1,2)
l.nDiv= NumDiv


# Constraints
constraints= preprocessor.getConstraintLoader

#
spc= constraints.newSPConstraint(1,0,0.0) # Node 2,gdl 0
spc= constraints.newSPConstraint(1,1,0.0) # Node 2,gdl 1
spc= constraints.newSPConstraint(1,2,0.0) # Node 2,gdl 2


setTotal= preprocessor.getSets.getSet("total")
setTotal.genMesh(xc.meshDir.I)

# Solution procedure
import os
pth= os.path.dirname(__file__)
if(not pth):
  pth= "."
#print "pth= ", pth
execfile(pth+"/../../aux/sol_eigenmodes.py")


omega= eig1**0.5
T= 2*math.pi/omega
fcalc= 1/T


lambdaA= 1.87510407
fteor= lambdaA**2/(2*math.pi*L**2)*math.sqrt(E*I/m)
ratio1= abs(fcalc-fteor)/fteor

''' 
print "omega= ",(omega)
print "T= ",(T)
print "fcalc= ",(fcalc)
print "fteor= ",(fteor)
print "ratio1= ",(ratio1)
   '''

import os
from miscUtils import LogMessages as lmsg
fname= os.path.basename(__file__)
if (abs(ratio1)<5e-3):
  print "test ",fname,": ok."
else:
  lmsg.error(fname+' ERROR.')
