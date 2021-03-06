# -*- coding: utf-8 -*-
from __future__ import division

# Functions to compute centrifugal forces according to IAPF.


def CoefReductorCentrifugaIAPF(v, Lf):
  '''Returns the reduction factor of the centrifugal force
     (according to expr. 2.3. IAPF)

  :param v: speed (m/s).
  :param Lf: 
  '''
  vkmhIAPF= v*3.6
  coefFIAPF= 0.0
  if(vkmhIAPF<120):
    coefFIAPF= 1
  elif(vkmhIAPF<300):
    coefFIAPF= 1-(vkmhIAPF-120)/1000*(814/vkmhIAPF+1.75)*(1-sqrt(2.88/Lf)) 
  else:
   coefFIAPF= 0.197+0.803*(sqrt(2.88/Lf))
  coefFIAPF= max(coefFIAPF,0.35)
  return coefFIAPF
