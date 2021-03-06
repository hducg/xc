# -*- coding: utf-8 -*-
# Home made test
'''Obtaining «previous» combination and combination difference.'''

import xc_base
import geom
import xc

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

prueba= xc.ProblemaEF()
preprocessor=  prueba.getPreprocessor  

cargas= preprocessor.getLoadLoader
casos= cargas.getLoadPatterns
#Load modulation.
ts= casos.newTimeSeries("constant_ts","ts")
casos.currentTimeSeries= "ts"
lpG0= casos.newLoadPattern("default","G0")
lpG1= casos.newLoadPattern("default","G1")
lpTC1V1= casos.newLoadPattern("default","TC1V1")
lpTC1V2= casos.newLoadPattern("default","TC1V2")
lpTC2V1= casos.newLoadPattern("default","TC2V1")
lpTC2V2= casos.newLoadPattern("default","TC2V2")
lpTC3V1= casos.newLoadPattern("default","TC3V1")
lpTC3V2= casos.newLoadPattern("default","TC3V2")
lpFV1= casos.newLoadPattern("default","FV1")
lpFV2= casos.newLoadPattern("default","FV2")
lpARRV1= casos.newLoadPattern("default","ARRV1")
lpARRV2= casos.newLoadPattern("default","ARRV2")
lpLZV1= casos.newLoadPattern("default","LZV1")
lpLZV2= casos.newLoadPattern("default","LZV2")
lpVTRSV= casos.newLoadPattern("default","VTRSV")
lpVLONG= casos.newLoadPattern("default","VLONG")
lpNV= casos.newLoadPattern("default","NV")

combs= cargas.getLoadCombinations
comb= combs.newLoadCombination("ELSCP001","1.00*G1 + 0.70*TC1V1")
comb= combs.newLoadCombination("ELSCP002","1.00*G1 + 0.70*TC1V1 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP009","1.00*G1 + 0.70*TC1V1 + 0.70*TC3V2")
comb= combs.newLoadCombination("ELSCP010","1.00*G1 + 0.70*TC1V1 + 0.70*TC3V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP021","1.00*G1 + 0.70*TC1V1 + 0.70*TC2V2")
comb= combs.newLoadCombination("ELSCP022","1.00*G1 + 0.70*TC1V1 + 0.70*TC2V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP041","1.00*G1 + 0.70*TC1V1 + 0.70*TC1V2")
comb= combs.newLoadCombination("ELSCP042","1.00*G1 + 0.70*TC1V1 + 0.70*TC1V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP053","1.00*G1 + 0.70*TC1V2")
comb= combs.newLoadCombination("ELSCP054","1.00*G1 + 0.70*TC1V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP061","1.00*G1 + 0.70*TC1V2 + 0.70*TC3V1")
comb= combs.newLoadCombination("ELSCP062","1.00*G1 + 0.70*TC1V2 + 0.70*TC3V1 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP073","1.00*G1 + 0.70*TC1V2 + 0.70*TC2V1")
comb= combs.newLoadCombination("ELSCP074","1.00*G1 + 0.70*TC1V2 + 0.70*TC2V1 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP093","1.00*G1 + 0.70*TC2V1")
comb= combs.newLoadCombination("ELSCP094","1.00*G1 + 0.70*TC2V1 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP109","1.00*G1 + 0.70*TC2V1 + 0.70*TC3V2")
comb= combs.newLoadCombination("ELSCP110","1.00*G1 + 0.70*TC2V1 + 0.70*TC3V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP129","1.00*G1 + 0.70*TC2V1 + 0.70*TC2V2")
comb= combs.newLoadCombination("ELSCP130","1.00*G1 + 0.70*TC2V1 + 0.70*TC2V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP173","1.00*G1 + 0.70*TC2V2")
comb= combs.newLoadCombination("ELSCP174","1.00*G1 + 0.70*TC2V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP189","1.00*G1 + 0.70*TC2V2 + 0.70*TC3V1")
comb= combs.newLoadCombination("ELSCP190","1.00*G1 + 0.70*TC2V2 + 0.70*TC3V1 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP209","1.00*G1 + 0.70*TC3V1")
comb= combs.newLoadCombination("ELSCP210","1.00*G1 + 0.70*TC3V1 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP217","1.00*G1 + 0.70*TC3V1 + 0.70*TC3V2")
comb= combs.newLoadCombination("ELSCP218","1.00*G1 + 0.70*TC3V1 + 0.70*TC3V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP229","1.00*G1 + 0.70*TC3V2")
comb= combs.newLoadCombination("ELSCP230","1.00*G1 + 0.70*TC3V2 + 0.20*NV")
comb= combs.newLoadCombination("ELSCP453","1.00*G1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP454","1.00*G1 + 0.70*TC3V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP456","1.00*G1 + 0.70*TC3V1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP458","1.00*G1 + 0.70*TC3V1 + 0.70*TC3V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP461","1.00*G1 + 0.70*TC2V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP465","1.00*G1 + 0.70*TC2V2 + 0.70*TC3V1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP470","1.00*G1 + 0.70*TC2V1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP474","1.00*G1 + 0.70*TC2V1 + 0.70*TC3V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP479","1.00*G1 + 0.70*TC2V1 + 0.70*TC2V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP490","1.00*G1 + 0.70*TC1V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP492","1.00*G1 + 0.70*TC1V2 + 0.70*TC3V1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP495","1.00*G1 + 0.70*TC1V2 + 0.70*TC2V1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP500","1.00*G1 + 0.70*TC1V1 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP502","1.00*G1 + 0.70*TC1V1 + 0.70*TC3V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP505","1.00*G1 + 0.70*TC1V1 + 0.70*TC2V2 + 0.60*NV")
comb= combs.newLoadCombination("ELSCP510","1.00*G1 + 0.70*TC1V1 + 0.70*TC1V2 + 0.60*NV")

nombrePrevia=""
previa= combs.getCombPrevia(combs.getComb("ELSCP001"))
if previa!=None:
  nombrePrevia= previa.getName

resta= combs.newLoadCombination("RESTA","")
resta.asigna("ELSCP001")
resta.resta(nombrePrevia)
descompResta= resta.getDescomp("%3.1f")

ratio1= (nombrePrevia=="")
ratio2= (descompResta=="1.0*G1+0.7*TC1V1")


# print "nombrePrevia= ",nombrePrevia
# print "descompResta= ",descompResta
# print "ratio1= ",ratio1
# print "ratio2= ",ratio2


import os
from miscUtils import LogMessages as lmsg
fname= os.path.basename(__file__)
if ratio1 & ratio2 :
  print "test ",fname,": ok."
else:
  lmsg.error(fname+' ERROR.')
