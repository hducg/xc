# -*- coding: utf-8 -*-
''' Verification test of a rectangular fiber section with an
    elasto plastic material model.'''

#    written from "Nociones de cálculo plástico." Carlos Benito Hernández.
#    page 26 and following.
#    url={https://books.google.es/books?id=v7bbMwEACAAJ},

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

from materials import section_properties
from misc import banco_pruebas_scc3d
import xc_base
import geom
import xc
from solution import predefined_solutions
from model import predefined_spaces
from materials import typical_materials

# Section geometry
# creation
# Rectangular cross-section definition
b= 10 # Cross section width  [cm]
h= 20 # Cross section depth [cm]
scc10x20= section_properties.RectangularSection('scc10x20',b,h)
scc10x20.nDivIJ= 32 # number of cells in IJ direction  
scc10x20.nDivJK= 32 # number of cells in JK direction

import os
pth= os.path.dirname(__file__)
if(not pth):
  pth= "."
#print "pth= ", pth
execfile(pth+"/macros_test_fiber_section.py")


fy= 2600 # yield stress [kp/cm2]
E= 2.1e6 # initial elastic tangent [kp/cm2.

prueba= xc.ProblemaEF()
prueba.logFileName= "/tmp/borrar.log" # No warning messages
preprocessor=  prueba.getPreprocessor
# Materials definition
epp= typical_materials.defElasticPPMaterial(preprocessor, "epp",E,fy,-fy)
respT= typical_materials.defElasticMaterial(preprocessor, "respT",1e10) # Torsion response.
respVy= typical_materials.defElasticMaterial(preprocessor, "respVy",1e6) # Shear response in y direction.
respVz= typical_materials.defElasticMaterial(preprocessor, "respVz",1e3) # Shear response in y direction.

# Section geometry
#creation
geomRectang= preprocessor.getMaterialLoader.newSectionGeometry("geomRectang")

reg= scc10x20.getRegion(geomRectang,"epp")
rectang= preprocessor.getMaterialLoader.newMaterial("fiber_section_3d","rectang")
fiberSectionRepr= rectang.getFiberSectionRepr()
fiberSectionRepr.setGeomNamed("geomRectang")
rectang.setupFibers()
extractFiberSectionProperties(rectang,scc10x20)

materiales= preprocessor.getMaterialLoader
agg= materiales.newMaterial("section_aggregator","sa")
agg.setSection("rectang")
agg.setAdditions(["T","Vy","Vz"],["respT","respVy","respVz"])

banco_pruebas_scc3d.sectionModel(preprocessor, "sa")
# Constraints
modelSpace= predefined_spaces.getStructuralMechanics3DSpace(preprocessor)
modelSpace.fixNode000_000(1)

# Loads definition
cargas= preprocessor.getLoadLoader

casos= cargas.getLoadPatterns

#Load modulation.
ts= casos.newTimeSeries("constant_ts","ts")
casos.currentTimeSeries= "ts"
#Load case definition
lp0= casos.newLoadPattern("default","0")
#casos.currentLoadPattern= "0"
loadVy= 2e4
loadVz= 3e4
loadMx= 1e3
loadMz= 0.999*scc10x20.getPlasticMomentZ(fy)
lp0.newNodalLoad(2,xc.Vector([0,loadVy,loadVz,loadMx,0,loadMz]))

#We add the load case to domain.
casos.addToDomain("0")


# Solution procedure
solu= prueba.getSoluProc
solCtrl= solu.getSoluControl


solModels= solCtrl.getModelWrapperContainer
sm= solModels.newModelWrapper("sm")


cHandler= sm.newConstraintHandler("plain_handler")
numberer= sm.newNumberer("default_numberer")
numberer.useAlgorithm("simple")


solution= predefined_solutions.SolutionProcedure()
solution.convergenceTestTol= 1.0e-2
analysis= solution.simpleNewtonRaphsonBandGen(prueba)

analOk= analysis.analyze(1)

nodes= preprocessor.getNodeLoader
nodes.calculateNodalReactions(True)

RVy= nodes.getNode(1).getReaction[1] 
RVz= nodes.getNode(1).getReaction[2] 
RMx= nodes.getNode(1).getReaction[3] 
RMz= nodes.getNode(1).getReaction[5] 

elements= preprocessor.getElementLoader
ele1= elements.getElement(1)
scc= ele1.getSection()
esfVy= scc.getStressResultantComponent("Vy")
esfVz= scc.getStressResultantComponent("Vz")
esfMx= scc.getStressResultantComponent("T")
esfMz= scc.getStressResultantComponent("Mz")



yCdgTeor= 0.0
zCdgTeor= 0.0
ratio1= (sumAreas-scc10x20.A())/scc10x20.A()
ratio2= rectang.getCdgY()-yCdgTeor
ratio3= zCdg-zCdgTeor
ratio4= (I1-scc10x20.Iz())/scc10x20.Iz()
ratio5= (I2-scc10x20.Iy())/scc10x20.Iy()
ratio6= (i1-scc10x20.iz())/scc10x20.iz()
ratio7= (i2-scc10x20.iy())/scc10x20.iy()
ratio8= (Me1-scc10x20.getYieldMomentZ(fy))/scc10x20.getYieldMomentZ(fy)
ratio9= (Me2-scc10x20.getYieldMomentY(fy))/scc10x20.getYieldMomentY(fy)
ratio10= (SzPosG-scc10x20.getPlasticSectionModulusZ())/scc10x20.getPlasticSectionModulusZ()
ratio11= (SyPosG-scc10x20.getPlasticSectionModulusY())/scc10x20.getPlasticSectionModulusY()
ratio12= (RMz+loadMz)/loadMz
ratio13= (esfMz-loadMz)/loadMz

ratio14= (RMx+loadMx)/loadMx
ratio15= (esfMx-loadMx)/loadMx

ratio16= (RVy+loadVy)/loadVy
ratio17= (esfVy-loadVy)/loadVy

ratio18= (RVz+loadVz)/loadVz
ratio19= (esfVz-loadVz)/loadVz

''' 
print "RVy= ",(RVy)
print "esfVy= ",(esfVy)
print "loadVy= ",(loadVy)

print "RVz= ",(RVz)
print "esfVz= ",(esfVz)
print "loadVz= ",(loadVz)

print "RMx= ",(RMx)
print "esfMx= ",(esfMx)
print "loadMx= ",(loadMx)

print "RMz= ",(RMz)
print "esfMz= ",(esfMz)
print "loadMz= ",(loadMz)
'''

import os
from miscUtils import LogMessages as lmsg
fname= os.path.basename(__file__)
if (abs(ratio1)<1e-5) & (abs(ratio2)<1e-5) & (abs(ratio3)<1e-5) & (abs(ratio4)<1e-3) & (abs(ratio5)<1e-2) & (abs(ratio6)<1e-3) & (abs(ratio7)<1e-2) & (abs(ratio8)<1e-3) & (abs(ratio9)<1e-3) & (abs(ratio10)<1e-5) & (abs(ratio11)<1e-5) & (abs(ratio12)<1e-5) &  (abs(ratio13)<1e-5) & (abs(ratio14)<1e-5) & (abs(ratio15)<1e-5) & (abs(ratio16)<1e-5) & (abs(ratio17)<1e-5) & (abs(ratio18)<1e-5) & (abs(ratio19)<1e-5) & (analOk==0):
  print "test ",fname,": ok."
else:
  lmsg.error(fname+' ERROR.')
