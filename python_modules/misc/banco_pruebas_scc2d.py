# -*- coding: utf-8 -*-
# Defines a model to test a 2D fiber section.
import xc_base
import geom
import xc
from model import predefined_spaces

def sectionModel(preprocessor,sectionName):
  ''' Defines a model to test a 2D fiber section.'''
  nodes= preprocessor.getNodeLoader

  modelSpace= predefined_spaces.StructuralMechanics2D(nodes)
  nodes.defaultTag= 1 #El número del próximo nodo será 1.
  nodes.newNodeXY(1,0)
  nodes.newNodeXY(1,0)

  elementos= preprocessor.getElementLoader
  elementos.dimElem= 1
  elementos.defaultMaterial= sectionName
  elementos.defaultTag= 1 #Tag for the next element.
  zls= elementos.newElement("zero_length_section",xc.ID([1,2]));
  return zls

