# -*- coding: utf-8 -*-
from __future__ import division
''' Limit state checking according to structural concrete spanish standard EHE-08.'''

import math
import xc_base
import geom
from materials.ehe import EHE_materials
from materials.fiber_section import createFiberSets
from materials.fiber_section import fiberUtils
from materials import limit_state_checking_base as lscb
from postprocess import control_vars as cv
from miscUtils import LogMessages as lmsg
import scipy.interpolate

# Reinforced concrete section shear checking.

def getFcvEH91(fcd):
  '''
  Return fcv (concrete virtual shear strength)
   according to EH-91.

  :param fcd: design compressive strength of concrete.
  :param b: net width of the element according to clause 40.3.5.
  :param d: effective depth (meters).
  
  '''
  fcdKpcm2= fcd*9.81/1e6
  return 0.5*sqrt(fcdKpcm2)/9.81*1e6


def getVu1(fcd, Nd, Ac, b0, d, alpha, theta):
  '''
  Return value of Vu1 (shear strength por compresión oblicua del alma)
   according to clause 44.2.3.1 of EHE.

  :param fcd: Design compressive strength of concrete.
  :param Nd: axial force design value (positive if in tension).
  :param Ac: concrete section total area.
  :param b0: net width of the element according to clause 40.3.5.
  :param d: effective depth.
  :param alpha: angle between the shear rebars and the member axis (figure 44.2.3.1.a EHE).
  :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
  
  '''
  f1cd= 0.6*fcd
  sgpcd= (Nd/Ac)
  K= min(5/3*(1+sgpcd/fcd),1)
  ctgTheta= min(max(cotg(theta),0.5),2.0)
  return K*f1cd*b0*d*(ctgTheta+cotg(alpha))/(1+ctgTheta^2)

def getFcv(fact, fck, Nd, Ac, b0, d, AsPas, fyd, AsAct, fpd):
  '''
  Return the value of fcv (concrete virtual shear strength)
     for parts WITH or WITHOUT shear reinforcement, according to clauses 44.2.3.2.1 y  44.2.3.2.2 de EHE.
  
  :param fact: factor equal to 0.12 for parts WITHOUT shear reinforcement y 0.10 for parts WITH
  shear reinforcement.
  :param fck: concrete characteristic compressive strength.
  :param Nd: axial force design value (positive if in tension).
  :param Ac: concrete section total area.
  :param b0: net width of the element according to clause 40.3.5.
  :param d: effective depth (meters).
  :param AsPas: Area of tensioned longitudinal steel rebars anchored
  at a distance greater than the effective depth of the section.
  :param fyd: reinforcing steel design yield strength (clause 38.3 EHE).
  :param AsAct: Area of tensioned longitudinal prestressed steel anchored
  at a distance greater than the effective depth of the section.
  :param fpd: design value of prestressing steel strength (clause 38.6 EHE).    
  '''
  sgpcd= Nd/Ac
  chi= 1+sqrt(200/(d*1000)) # d MUST BE EXPRESSED IN METERS.
  rol= min((AsPas+AsAct*fpd/fyd)/(b0*d),0.02)
  return fact*chi*(rol*fck/1e4)^(1/3)*1e6-0.15*sgpcd


def getVu2SIN(fck, Nd, Ac, b0, d, AsPas, fyd, AsAct, fpd):
  '''
  Return the value of Vu2 (shear strength por tracción en el alma)
     for parts WITHOUT shear reinforcement, according to clause 44.2.3.2.1 de EHE.
  
  :param fck: concrete characteristic compressive strength.
  :param Nd: axial force design value (positive if in tension).
  :param Ac: concrete section total area.
  :param b0: net width of the element according to clause 40.3.5.
  :param d: effective depth (meters).
  :param AsPas: Area of tensioned longitudinal steel rebars anchored
  at a distance greater than the effective depth of the section.
  :param fyd: reinforcing steel design yield strength (clause 38.3 EHE).
  :param AsAct: Area of tensioned longitudinal prestressed steel anchored
  at a distance greater than the effective depth of the section.
  :param fpd: design value of prestressing steel strength (clause 38.6 EHE).
   
  '''
  return getFcv(0.12,fck,Nd,Ac,b0,d,AsPas,fyd,AsAct,fpd)*b0*d

def getVcu(fck, Nd, Ac, b0, d, theta, AsPas, fyd, AsAct, fpd, sgxd, sgyd):
  '''
  Return the value of Vcu (contribution of the concrete to shear strength) 
  for parts WITH shear reinforcement, according to clause 44.2.3.2.2 de EHE.

  :param fck: concrete characteristic compressive strength.
  :param Nd: axial force design value (positive if in tension).
  :param Ac: concrete section total area.
  :param b0: net width of the element according to clause 40.3.5.
  :param d: effective depth (meters).
  :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
  :param AsPas: Area of tensioned longitudinal steel rebars anchored
  at a distance greater than the effective depth of the section.
  :param fyd: reinforcing steel design yield strength (clause 38.3 EHE).
  :param AsAct: Area of tensioned longitudinal prestressed steel anchored
  at a distance greater than the effective depth of the section.
  :param fpd: design value of prestressing steel strength (clause 38.6 EHE).
  :param sgxd: design value of normal stress at the centre of gravity of the
  section parallel to the main axis of the member. Calculated assuming NON 
  CRACKED concrete (clause 44.2.3.2).
  :param sgyd: design value of normal stress at the centre of gravity of the
  section parallel to shear force Vd. Calculated assuming NON CRACKED 
   concrete (clause 44.2.3.2).
  '''
  fcv= getFcv(0.10,fck,Nd,Ac,b0,d,AsPas,fyd,AsAct,fpd) 
  fctm= fctMedEHE08(fck) 
  ctgThetaE= min(max(0.5,sqrt(fctm-sgxd/fctm-sgyd)),2.0)
  ctgTheta= min(max(cotg(theta),0.5),2.0)
  beta= 0.0
  if(ctgTheta<ctgThetaE):
    beta= (2*ctgTheta-1)/(2*ctgThetaE-1)
  else:
    beta= (ctgTheta-2)/(ctgThetaE-2)
  return fcv*b0*d*beta

def getVsu(z, alpha, theta, AsTrsv, fyd):
  '''
  Return the value of Vsu (contribución de la reinforcement transversal de alma a la resistencia a cortante)
   for parts WITH shear reinforcement, according to clause 44.2.3.2.2 de EHE.

  :param z: Lever arm.
  :param alpha: angle of the shear reinforcement with the part axis (figure 44.2.3.1.a EHE).
  :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
  :param AsTrsv: transverse reinforcement area.
  :param fyd: design yield strength of the transverse reinforcement.
  
  '''
  ctgTheta= min(max(cotg(theta),0.5),2.0)
  fyalphad= min(fyd,400e6) # comentario al clause 40.2 EHE
  return z*sin(alpha)*(cotg(alpha)+ctgTheta)*AsTrsv*fyalphad


def getVu2(fck, Nd, Ac, b0, d, z, alpha, theta, AsPas, fyd, AsAct, fpd, sgxd, sgyd, AsTrsv, fydTrsv):
  '''
  Return the value of Vu2 for parts WITH or WITHOUT shear reinforcement, according to clause 44.2.3.2.2 de EHE.

  :param fck: concrete characteristic compressive strength.
  :param Nd: axial force design value (positive if in tension).
  :param Ac: concrete section total area.
  :param b0: net width of the element according to clause 40.3.5.
  :param d: effective depth (meters).
  :param z: Lever arm.
  :param alpha: angle of the shear reinforcement with the part axis (figure 44.2.3.1.a EHE).
  :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
  :param AsPas: Area of tensioned longitudinal steel rebars anchored
  at a distance greater than the effective depth of the section.
  :param fyd: reinforcing steel design yield strength (clause 38.3 EHE).
  :param AsAct: Area of tensioned longitudinal prestressed steel anchored
  at a distance greater than the effective depth of the section.
  :param fpd: design value of prestressing steel strength (clause 38.6 EHE).
  :param sgxd: design value of normal stress at the centre of gravity of the
  section parallel to the main axis of the member. Calculated assuming NON 
  CRACKED concrete (clause 44.2.3.2).
  :param sgyd: design value of normal stress at the centre of gravity of the
  section parallel to shear force Vd. Calculated assuming NON CRACKED 
   concrete (clause 44.2.3.2).
  :param AsTrsv: transverse reinforcement area.
  :param fydTrsv: design yield strength of the transverse reinforcement.
  '''
  vcu= 0.0
  vsu= 0.0
  if(AsTrsv>0.0):
    vcu= getVcu(fck,Nd,Ac,b0,d,theta,AsPas,fyd,AsAct,fpd,sgxd,sgyd)
    vsu= getVsu(z,alpha,theta,AsTrsv,fydTrsv)
  else:
    vcu= getVu2SIN(fck,Nd,Ac,b0,d,AsPas,fyd,AsAct,fpd)
    vsu= 0.0
  return vcu+vsu

def getVu(fck, fcd, Nd, Ac, b0, d, z, alpha, theta, AsPas, fyd, AsAct, fpd, sgxd, sgyd, AsTrsv, fydTrsv):
  '''
  Return the value of Vu= max(Vu1,Vu2) for parts WITH or WITHOUT shear reinforcement, according to clause 44.2.3.2.2 de EHE.
  :param fck: concrete characteristic compressive strength.
  :param Nd: axial force design value (positive if in tension).
  :param Ac: concrete section total area.
  :param b0: net width of the element according to clause 40.3.5.
  :param d: effective depth (meters).
  :param z: Lever arm.
  :param alpha: angle of the shear reinforcement with the part axis (figure 44.2.3.1.a EHE).
  :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
  :param AsPas: Area of tensioned longitudinal steel rebars anchored
  at a distance greater than the effective depth of the section.
  :param fyd: reinforcing steel design yield strength (clause 38.3 EHE).
  :param AsAct: Area of tensioned longitudinal prestressed steel anchored
  at a distance greater than the effective depth of the section.
  :param fpd: design value of prestressing steel strength (clause 38.6 EHE).
  :param sgxd: design value of normal stress at the centre of gravity of the
  section parallel to the main axis of the member. Calculated assuming NON 
  CRACKED concrete (clause 44.2.3.2).
  :param sgyd: design value of normal stress at the centre of gravity of the
  section parallel to shear force Vd. Calculated assuming NON CRACKED 
   concrete (clause 44.2.3.2).
  :param AsTrsv: transverse reinforcement area.
  :param fydTrsv: design yield strength of the transverse reinforcement.
  '''
  vu1= getVu1(fcd,Nd,Ac,b0,d,alpha,theta)
  vu2= getVu2(fck,Nd,Ac,b0,d,z,alpha,theta,AsPas,fyd,AsAct,fpd,sgxd,sgyd,AsTrsv,fydTrsv)
  return min(vu1,vu2)

def cumpleCortante(fck, fcd, Nd, Ac, b0, d, z, alpha, theta, AsPas, fyd, AsAct, fpd, sgxd, sgyd, AsTrsv, fydTrsv, Vrd):
  '''Check shear.'''
  vu= getVu(fck,fcd,Nd,Ac,b0,d,z,alpha,theta,AsPas,fyd,AsAct,fpd,sgxd,sgyd,AsTrsv,fydTrsv)
  if(Vrd<=vu):
    return True
  else:
    return False

def aprovCortante(fck, fcd, Nd, Ac, b0, d, z, alpha, theta, AsPas, fyd, AsAct, fpd, sgxd, sgyd, AsTrsv, fydTrsv, Vrd):
  '''Aprovechamiento a cortante.'''
  vu= getVu(fck,fcd,Nd,Ac,b0,d,z,alpha,theta,AsPas,fyd,AsAct,fpd,sgxd,sgyd,AsTrsv,fydTrsv)
  return Vrd/vu

class ParamsCortante(object):
  '''Defines shear design parameters.'''
  def __init__(self):
    self.concreteArea= 0.0 # Concrete section total area.
    self.widthMin= 0.0 # net width of the element according to clause 40.3.5.
    self.depthUtil= 0.0 # effective depth (meters).
    self.brazoMecanico= 0.0 # Lever arm (meters).
    self.areaRebarTracc= 0.0 # Area of tensioned longitudinal steel rebars anchored at a distance greater than the effective depth of the section.
    self.areaTendonesTracc= 0.0 # Area of tensioned longitudinal prestressed steel anchored at a distance greater than the effective depth of the section.
    self.areaShReinfBranchsTrsv= 0.0 # transverse reinforcement area.
    self.sigmaXD= 0.0 # design value of normal stress at the centre of gravity of the section parallel to the main axis of the member. Calculated assuming NON CRACKED concrete (clause 44.2.3.2).
    self.sigmaYD= 0.0 # design value of normal stress at the centre of gravity of the section parallel to shear force Vd. Calculated assuming NON CRACKED concrete (clause 44.2.3.2).
    self.angAlpha= math.pi/2 # angle of the shear reinforcement with the part axis (figure 44.2.3.1.a EHE).
    self.angTheta= math.pi/6 # Angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
    self.cortanteUltimo= 0.0

  def calcCortanteUltimo(self, concreteFibersSet, rebarFibersSet,tensionedRebarsFiberSet, fck, fcd, fyd, fpd, fydTrsv):
    '''Compute section shear strength.'''
    self.concreteArea= concreteFibersSet.getArea()
    self.widthMin= concreteFibersSet.getAnchoMecanico() # Enhance (not valid with non-convex sections).
    self.depthUtil= concreteFibersSet.getCantoUtil()
    self.brazoMecanico= concreteFibersSet.getBrazoMecanico()
    self.areaRebarTracc= tensionedRebarsFiberSet.getArea
    # areaTendonesTracc= 

    self.sigmaXD= N/area+Mz/Iz*yCdg+My/Iy*zCdg
    self.cortanteUltimo= getVu(fck,fcd,N,self.concreteArea,self.widthMin,self.depthUtil,self.brazoMecanico,self.angAlpha,self.angTheta,self.areaRebarTracc,fyd,self.areaTendonesTracc,fpd,self.sigmaXD,self.sigmaYD,AsTrsv,self.areaShReinfBranchsTrsv,fydTrsv)

  def printParams(self):
    '''Print shear checking values.'''
    print "Area de las reinforcement traccionadas; As= ",self.areaRebarTracc*1e4," cm2"
    print "transverse reinforcement area; AsTrsv= ",self.areaShReinfBranchsTrsv*1e4," cm2"
    print "design value of normal stress; sigmaXD= ",self.sigmaXD/1e6," MPa"
    print "effective depth; d= ",self.depthUtil," m"
    print "minimal width; b0= ",self.widthMin," m"
    print "Lever arm; z= ",self.brazoMecanico," m"
    print "cortanteUltimo; Vu= ",self.cortanteUltimo/1e3," kN"

def getF1cdEHE08(fck,fcd):
    '''getF1cdEHE08(fck,fcd)

    :param fck: concrete characteristic compressive strength (Pa).
    :param fcd: design value of concrete compressive strength (N/m2).

    Returns the value of f1cd (design value of the concrete strut strength)
    according to clause 44.2.3.1 of EHE-08.
    '''
    retval=0.6
    if fck>60e6:
      retval=max(0.9-fck/200.e6,0.5)
    retval= retval*fcd
    return retval



def getKEHE08(sgpcd,fcd):
    '''getKEHE08(sgpcd,fcd)
    :param sgpcd: Tensión axil efectiva en el hormigón Ncd/Ac.
    :param fcd: design value of concrete compressive strength (N/m2).

    Return the value of K (coeficiente que depende del esfuerzo axil)
    according to clause 44.2.3.1 de la EHE-08
    '''
    s=-sgpcd/fcd #Positive when compressed
    if s>1:
        print "getKEHE08; tensión excesiva en el hormigón: (",sgpcd,"<",-fcd,")\n"
    if s<=0:
        retval=1.0
    elif s<=0.25:
        retval=1+s
    elif s<=0.5:
        retval=1.25
    else:
        retval=2.5*(1-s)
    return retval



def getVu1EHE08(fck,fcd,Ncd,Ac,b0,d,alpha,theta):
    '''getVu1EHE08(fck,fcd,Ncd,Ac,b0,d,alpha,theta) [uds: N, m, rad]

    :param fck: concrete characteristic compressive strength.
    :param fcd: design value of concrete compressive strength (N/m2).
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth.
    :param alpha: angle of the shear reinforcement with the part axis (figure 44.2.3.1 EHE-08).
    :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).

    Return the value of Vu1 (shear strength por compresión oblicua del alma)
    according to clause 44.2.3.1 de EHE-08.
    '''
    f1cd=getF1cdEHE08(fck,fcd)
    sgpcd=min(Ncd/Ac,0)
    K=getKEHE08(sgpcd,fcd)
    ctgTheta=min(max(1/math.tan(theta),0.5),2.0)
    return K*f1cd*b0*d*(ctgTheta+1/math.tan(alpha))/(1+ctgTheta**2)

def getVu2EHE08NoAtNoFis(fctd,I,S,b0,alphal,Ncd,Ac):
    '''getVu2EHE08NoAtNoFis(fctd,I,S,b0,alphal,Ncd,Ac) [uds: N, m, rad]

    :param fctd: Resistencia de cálculo del hormigón a tracción.
    :param I: Moment of inertia of the section with respect of its centroid.
    :param S: Momento estático de la parte de la sección que queda por encima del CDG.
    :param b0: net width of the element according to clause 40.3.5.
    :param alphal: coeficiente que, en su caso, introduce el efecto de la transferencia.
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    Return the value of Vu2 (shear strength por tracción en el alma)
    according to clause 44.2.3.2.1.1 de EHE-08.
    '''
    tmp= fctd
    if alphal!=1.0:
      sgpcd=min(Ncd/Ac,0)
      tmp=math.sqrt(fctd**2-alphal*sgpcd*fctd)
    return I*b0/S*tmp



def getFcvEHE08(fact,fcv,gammaC,b0,d,chi,sgpcd,AsPas,AsAct):
    '''getFcvEHE08(fact,fcv,gammaC,b0,d,chi,sgpcd,AsPas,AsAct)  [uds: N, m, rad]
    Return the value of fcv (concrete virtual shear strength)
    for parts WITH or WITHOUT shear reinforcement in cracked regions, according
    to clauses 44.2.3.2.1.2 y  44.2.3.2.2 de EHE-08.

    :param fact: Factor que toma el valor 0.18 for parts WITHOUT shear reinforcement y 0.15 for parts WITH shear reinforcement.
    :param fcv: Resistencia efectiva del hormigón a cortante. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param gammaC: Partial safety factor for concrete.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth (meters).
    :param chi: coefficient that takes into account the aggregate effect
     inside the effective depth.
    :param sgpcd: Tensión axial media en el alma (compresión positiva).
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    '''
    rol=min((AsPas+AsAct)/(b0*d),0.02)
    return fact/gammaC*chi*(rol*fcv/1e4)**(1/3)*1e6-0.15*sgpcd


def getFcvMinEHE08(fcv,gammaC,d,chi,sgpcd):
    '''getFcvMinEHE08(fcv,gammaC,d,chi,sgpcd)
    Devuelve el valor mínimo de fcv (concrete virtual shear strength)
    for parts WITHOUT shear reinforcement in cracked regions, according to
    clause 44.2.3.2.1.2 de EHE-08.

    :param fcv: Resistencia efectiva del hormigón a cortante. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param gammaC: Partial safety factor for concrete.
    :param d: effective depth (meters).
    :param chi: coefficient that takes into account the aggregate effect
     inside the effective depth.
    :param sgpcd: Tensión axial media en el alma (compresión positiva).

    '''
    return 0.075/gammaC*math.pow(chi,1.5)*math.sqrt(fcv)*1e3-0.15*sgpcd


def getVu2EHE08NoAtSiFis(fcv,fcd,gammaC,Ncd,Ac,b0,d,AsPas,AsAct):
    '''getVu2EHE08NoAtSiFis(fcv,fcd,gammaC,Ncd,Ac,b0,d,AsPas,AsAct) [uds: N, m]

    :param fcv: Resistencia efectiva del hormigón a cortante. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param fcd: design value of concrete compressive strength).
    :param gammaC: Partial safety factor for concrete.
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth (meters).
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.

    Return the value of Vu2 (shear strength por tracción en el alma)
    for parts WITHOUT shear reinforcement in cracked regions, according to clause 44.2.3.2.1.2 de EHE-08.
    '''
    chi=min(2,1+math.sqrt(200/(d*1000.))) #HA DE EXPRESARSE EN METROS.
    sgpcd=max(max(Ncd/Ac,-0.3*fcd),-12e6)
    fcvTmp=getFcvEHE08(0.18,fcv,gammaC,b0,d,chi,sgpcd,AsPas,AsAct)
    fcvMinTmp=getFcvMinEHE08(fcv,gammaC,d,chi,sgpcd)
    return max(fcvTmp,fcvMinTmp)*b0*d

def getVu2EHE08NoAt(M,Mfis,fcv,fck,gammaC,I,S,alphaL,Ncd,Ac,b0,d,AsPas,AsAct):
    '''getVu2EHE08NoAt(M,Mfis,fcv,fck,gammaC,I,S,alphaL,Ncd,Ac,b0,d,AsPas,AsAct)   [uds: N, m, rad]
    Return the value of Vu2 (shear strength por tracción en el alma)
    for parts WITHOUT shear reinforcement, according to clauses 
    44.2.3.2.1.1 y 44.2.3.2.1.2 of EHE-08.

    :param M: Momento que actúa sobre la sección.
    :param Mfis: Momento de fisuración de la sección correspondiente al mismo plano y sentido
    flexión que M.
    :param fcv: Resistencia efectiva del hormigón a cortante. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param fck: concrete characteristic compressive strength.
    :param gammaC: Partial safety factor for concrete.
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth (meters).
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    '''
    concrTmp= EHE_materials.EHEConcrete("HA",fck,gammaC)
    fctdTmp=concrTmp.fctkEHE08()/gammaC
    fcdTmp=fck/gammaC
    if M<=Mfis:
        retval=getVu2EHE08NoAtNoFis(fctdTmp,I,S,b0,alphaL,Ncd,Ac)
    else:
        retval=getVu2EHE08NoAtSiFis(fck,fcdTmp,1.5,Ncd,Ac,b0,d,AsPas,AsAct)
    return retval


def getVsuEHE08(z,alpha,theta,AsTrsv,fyd):
    '''getVsuEHE08(z,alpha,theta,AsTrsv,fyd)  [uds: N, m, rad]
    Return the value of Vsu (contribución de la reinforcement transversal de alma
    a la resistencia al esfuerzo cortante) for parts WITH shear reinforcement,
    according to clause 44.2.3.2.2 de EHE-08.

    :param z: Lever arm.
    :param alpha: angle of the transverse reinforcement with the axis of the part.
    :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
    :param AsTrsv: transverse reinforcement area cuya contribución se calcula.
    :param fyd: design yield strength of the transverse reinforcement.
    '''
    fyalphad=min(fyd,400e6)
    return z*math.sin(alpha)*(1/math.tan(alpha)+1/math.tan(theta))*AsTrsv*fyalphad



def getEpsilonXEHE08(Nd,Md,Vd,Td,z,AsPas,AsAct,Es,Ep,Fp,Ae,ue):
    '''getEpsilonXEHE08(Nd,Md,Vd,Td,z,AsPas,AsAct,Es,Ep,Fp,Ae,ue) [uds: N, m, rad]
    Devuelve la deformación de longitudinal en el alma according to
    expresión que figura en los comentarios al clause 44.2.3.2.2 de EHE-08.

    :param Nd: Design value of axial force (aquí positivo si es de tracción)
    :param Md: Absolute value of design value of bending moment.
    :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
    :param Td: Torsor de cálculo.
    :param z: Lever arm.
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    :param Es: reinforcing steel elastic modulus.
    :param Ep: prestressing steel elastic modulus.
    :param Fp: Prestressing force on the section (positive if in tension).
    :param Ae: Área encerrada por la línea media de la sección hueca eficaz.
    :param ue: Perímetro de la línea media de la sección hueca eficaz.
    '''
    denomEpsilonX=2*(Es*AsPas+Ep*AsAct) 
    Md= max(Md,Vd*z)
    assert z>0
    assert Ae>0
    if denomEpsilonX>0:
      retvalEpsilonX=(Md/z+math.sqrt(Vd**2+(ue*Td/2.0/Ae)**2)+Nd/2.+Fp)/denomEpsilonX  
    else:
      retvalEpsilonX=0
    retvalEpsilonX= max(0,retvalEpsilonX)
    return retvalEpsilonX
  


def getCrackAngleEHE08(Nd,Md,Vd,Td,z,AsPas,AsAct,Es,Ep,Fp,Ae,ue):
    '''getCrackAngleEHE08(Nd,Md,Vd,Td,z,AsPas,AsAct,Es,Ep,Fp,Ae,ue) [uds: N, m, rad]
    Return the reference angle of inclination of cracks from
    la deformación longitudinal en el alma de la sección
    expresado en radianes. See clause 44.2.3.2.2 de EHE-08.

    :param Nd: Design value of axial force (aquí positivo si es de tracción)
    :param Md: Absolute value of design value of bending moment.
    :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
    :param Td: Torsor de cálculo.
    :param z: Lever arm.
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    :param Es: reinforcing steel elastic modulus.
    :param Ep: prestressing steel elastic modulus.
    :param Fp: Prestressing force on the section (positive if in tension).
    :param Ae: Área encerrada por la línea media de la sección hueca eficaz.
    :param ue: Perímetro de la línea media de la sección hueca eficaz.

    '''
    return math.radians(getEpsilonXEHE08(Nd,Md,Vd,Td,z,AsPas,AsAct,Es,Ep,Fp,Ae,ue)*7000+29) 



  
def getBetaVcuEHE08(theta,thetaE):
    '''getBetaVcuEHE08(theta,thetaE) [uds: N, m, rad]
    Return the value of «beta» for the expression
    of Vcu according to clause 44.2.3.2.2 of EHE-08.

    :param thetaE: Reference angle of inclination of cracks.
    :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).    
    '''
    cotgTheta=1/math.tan(theta)
    cotgThetaE=1/math.tan(thetaE)
    retval=0.0
    if cotgTheta<0.5:
        print "getBetaVcuEHE08; theta angle is too small."
    else:
        if(cotgTheta<cotgThetaE):
            retval= (2*cotgTheta-1)/(2*cotgThetaE-1)
        else:
            if cotgTheta<=2.0:
                retval= (cotgTheta-2)/(cotgThetaE-2)
            else:
                print"getBetaVcuEHE08; theta angle is too big."
    return retval
  

 
def getVcuEHE08(fcv,fcd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue):
    '''getVcuEHE08(fcv,fcd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue) [uds: N, m, rad]
    Return the value of Vcu (contribución del hormigón a la resistencia al esfuerzo cortante)
    for parts WITH shear reinforcement, according to clause 44.2.3.2.2 de EHE-08.

    :param fcv: effective concrete shear strength. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param fcd: design value of concrete compressive strength).
    :param gammaC: Partial safety factor for concrete.
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth (meters).
    :param z: Lever arm.
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE)
    :param Nd: Design value of axial force (positivo si es de tracción)
    :param Md: Absolute value of design value of bending moment.
    :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
    :param Td: Torsor de cálculo.
    :param Es: reinforcing steel elastic modulus.
    :param Ep: prestressing steel elastic modulus.
    :param Fp: Prestressing force on the section (positive if in tension).
    :param Ae: Área encerrada por la línea media de la sección hueca eficaz.
    :param ue: Perímetro de la línea media de la sección hueca eficaz.

    '''
  
    chi=min(2,1+math.sqrt(200/(d*1000.)))   #HA DE EXPRESARSE EN METROS.
    sgpcd=max(max(Ncd/Ac,-0.3*fcd),-12e6)
    FcvVcu=getFcvEHE08(0.15,fcv,gammaC,b0,d,chi,sgpcd,AsPas,AsAct)
    thetaEVcu=getCrackAngleEHE08(Nd,Md,Vd,Td,z,AsPas,AsAct,Es,Ep,Fp,Ae,ue)
    betaVcu=getBetaVcuEHE08(theta,thetaEVcu)
    return FcvVcu*betaVcu*b0*d
  


  
def getVu2EHE08SiAt(fcv,fcd,fyd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,AsTrsv, alpha, theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue):
    '''getVu2EHE08SiAt(fcv,fcd,fyd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,AsTrsv, alpha, theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue) [uds: N, m, rad]. Return the value of Vu2 (esfuerzo shear strength por tracción en el alma)
    for parts WITH shear reinforcement, according to clause 44.2.3.2.2 of EHE-08.

    :param fcv: effective concrete shear strength. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param fcd: design value of concrete compressive strength).
    :param fyd: design yield strength of the transverse reinforcement.
    :param gammaC: Partial safety factor for concrete.
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth (meters).
    :param z: Lever arm.
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    :param AsTrsv: transverse reinforcement area.
    :param alpha: angle of the transverse reinforcement with the axis of the part.
    :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
    :param Nd: Design value of axial force (positivo si es de tracción)
    :param Md: Absolute value of design value of bending moment.
    :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
    :param Td: Torsor de cálculo.
    :param Es: reinforcing steel elastic modulus.
    :param Ep: prestressing steel elastic modulus.
    :param Fp: Prestressing force on the section (positive if in tension).
    :param Ae: Área encerrada por la línea media de la sección hueca eficaz.
    :param ue: Perímetro de la línea media de la sección hueca eficaz.

    '''
    return getVcuEHE08(fcv,fcd,gammaC,Ncd,Ac,b0,d,AsPas,AsAct,theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue)+getVsuEHE08(z,alpha,theta,AsTrsv,fyd)

  
def getVuEHE08SiAt(fck,fcv,fcd,fyd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,AsTrsv, alpha, theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue):
    '''def getVuEHE08SiAt(fck,fcv,fcd,fyd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,AsTrsv, alpha, theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue) [uds: N, m, rad]
    Return the value of Vu (section shear strength)
    for parts WITH shear reinforcement, according to clause 44.2.3.2.2 de EHE-08.

    :param fck: concrete characteristic compressive strength.
    :param fcv: effective concrete shear strength. En piezas sin shear reinforcement
    será fcv= min(fck,60MPa). En piezas con shear reinforcement fcv= min(fck,100MPa).
    En ambos casos, si el control del hormigón es indirecto fcv=15MPa.
    :param fcd: design value of concrete compressive strength).
    :param fyd: design yield strength of the transverse reinforcement.
    :param gammaC: Partial safety factor for concrete.
    :param Ncd: axil de cálculo resistido por el hormigón (positivo si es de tracción).
    :param Ac: concrete section total area.
    :param b0: net width of the element according to clause 40.3.5.
    :param d: effective depth (meters).
    :param z: Lever arm.
    :param AsPas: Area of tensioned longitudinal steel rebars anchored
     at a distance greater than the effective depth of the section.
    :param AsAct: Area of tensioned longitudinal prestressed steel anchored
    at a distance greater than the effective depth of the section.
    :param AsTrsv: transverse reinforcement area.
    :param alpha: angle of the transverse reinforcement with the axis of the part.
    :param theta: angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
    :param Nd: Design value of axial force (positivo si es de tracción)
    :param Md: Absolute value of design value of bending moment.
    :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
    :param Td: Torsor de cálculo.
    :param Es: reinforcing steel elastic modulus.
    :param Ep: prestressing steel elastic modulus.
    :param Fp: Prestressing force on the section (positive if in tension).
    :param Ae: Área encerrada por la línea media de la sección hueca eficaz.
    :param ue: Perímetro de la línea media de la sección hueca eficaz.    
    '''
    return  min(getVu2EHE08(fcv,fcd,fyd,gammaC,Ncd,Ac,b0,d,z,AsPas,AsAct,AsTrsv,alpha,theta,Nd,Md,Vd,Td,Es,Ep,Fp,Ae,ue),getVu1EHE08(fck,fcd,Ncd,Ac,b0,d,alpha,theta))
  

class ShearControllerEHE(lscb.LimitStateControllerBase):
  '''Shear control according to EHE-08.'''
  def __init__(self,limitStateLabel):
    super(ShearControllerEHE,self).__init__(limitStateLabel)
    self.concreteFibersSetName= "concrete" #Name of the concrete fibers set.
    self.rebarFibersSetName= "reinforcement" #Name of the rebar fibers set.
    self.tensionedRebarsFiberSetName= "reinforcementTraccion" #Name of the tensioned rebars set.
    self.hayMom= False # Verdadero si la sección está sometida a momento.
    self.fcvH= 0.0 # effective concrete shear strength.
    self.fckH= 0.0 #Valor característico de la resistencia del hormigón a compresión.
    self.fcdH= 0.0 #Valor de cálculo de la resistencia del hormigón a compresión.
    self.fctdH= 0.0 #Valor de cálculo de la resistencia del hormigón a tracción.
    self.gammaC= 0.0 # Partial safety factor for concrete.
    self.fydS= 0.0 #Design value of reinforcement steel strength.
    self.depthUtil= 0.0 #current effective depth
    self.brazoMecanico= 0.0 #Lever arm con el que está trabajando la sección.
    self.strutWidth= 0.0 #Compressed strut width «b0».
    self.I= 0.0 #Momento of inertia of the section with respect to the neutral axis in régimen elástico.
    self.S= 0.0 #First moment of area of the section with respect to the neutral axis in régimen elástico.
    self.concreteArea= 0.0 #Area de la sección de hormigón.
    self.numBarrasTraccion= 0 #Número de barras sometidas a tracción.
    self.areaRebarTracc= 0.0 #Area total de las barras traccionadas.
    self.eps1= 0.0 #Maximum strain in concrete.
    self.concreteAxialForce= 0.0 #Esfuerzo axil soportado por el hormigón.
    self.E0= 0.0 #Módulo de rigidez tangente del hormigón.

    self.alphaL= 1.0 #Factor que depende de la transferencia de pretensado.
    self.AsTrsv= 0.0 #Área de la shear reinforcement.
    self.alpha= math.radians(90) # angle of the shear reinforcement with the part axis (figure 44.2.3.1 EHE-08).
    self.theta= math.radians(45) #Angle between the concrete compressed struts and the member axis (figure 44.2.3.1.a EHE).
    self.thetaMin= math.atan(0.5) #Minimal value of the theta angle.
    self.thetaMax= math.atan(2) #Maximal value of the theta angle.

    self.thetaFisuras= 0.0 # angle of the cracks with the part axis.
    self.Vcu= 0.0 # Contribución del hormigón a la resistencia al esfuerzo cortante.
    self.Vsu= 0.0 # Contribución de las reinforcement a cortante a la resistencia al esfuerzo cortante.
    self.Vu1= 0.0 #Agotamiento por compresión oblicua del alma.
    self.Vu2= 0.0 #Agotamiento por tracción en el alma.
    self.Vu= 0.0 #Cortante último de la sección.

  def calcVuEHE08NoAt(self, preprocessor, scc, concrete, reinfSteel):
    ''' Calcula el cortante último de la sección sin shear reinforcement.
     XXX Falta considerar la reinforcement activa.

     :param reinfSteelMaterialTag: reinforcement steel material identifier.
     :param concrete: Parámetros para modelizar el hormigón.
     :param reinfSteel: parameters to modelize reinforcement steel.
    '''
    self.concreteMatTag= concrete.matTagD
    self.fckH= abs(concrete.fck)
    self.fcdH= abs(concrete.fcd())
    self.fctdH= concrete.fctd()
    self.gammaC= concrete.gmmC
    self.reinfSteelMaterialTag= reinfSteel.matTagD
    self.fydS= reinfSteel.fyd()

    if(not scc.hasProp("rcSets")):
      scc.setProp("rcSets", createFiberSets.fiberSectionSetupRC3Sets(scc,self.concreteMatTag,self.concreteFibersSetName,self.reinfSteelMaterialTag,self.rebarFibersSetName))
    rcSets= scc.getProp("rcSets")

    concrFibers= rcSets.concrFibers.fSet
    self.concreteArea= rcSets.getConcreteArea(1)
    if(self.concreteArea<1e-6):
      errMsg= "concrete area too smail; Ac= " + str(self.concreteArea) + " m2\n"
      lmsg.error(errMsg)
    else:
      reinfFibers= rcSets.reinfFibers.fSet
      reinforcementTraccion= rcSets.tensionFibers
      self.hayMom= scc.isSubjectedToBending(0.1)
      self.numBarrasTraccion= rcSets.getNumTensionRebars()
      if(self.hayMom):
        self.eps1= rcSets.getMaxConcreteStrain()
        self.E0= rcSets.getConcreteInitialTangent()
        self.concreteAxialForce= rcSets.getConcreteCompression()
        self.strutWidth= scc.getCompressedStrutWidth() # b0
        if((self.E0*self.eps1)<self.fctdH): # Sección no fisurada
          self.I= scc.getHomogenizedI(self.E0)
          self.S= scc.getSPosHomogeneizada(self.E0)
          self.Vu2= getVu2EHE08NoAtNoFis(self.fctdH,self.I,self.S,self.strutWidth,self.alphaL,self.concreteAxialForce,self.concreteArea)
        else: # Sección fisurada
          self.depthUtil= scc.getCantoUtil() # d
          if(self.numBarrasTraccion>0):
            self.areaRebarTracc= reinforcementTraccion.getArea(1)
          else:
            self.areaRebarTracc= 0.0
          self.Vu2= getVu2EHE08NoAtSiFis(self.fckH,self.fcdH,self.gammaC,self.concreteAxialForce,self.concreteArea,self.strutWidth,self.depthUtil,self.areaRebarTracc,0.0)
        self.Vcu= self.Vu2
        self.Vsu= 0.0
        self.Vu1= -1.0
        self.Vu= self.Vu2
      else: # Sección no fisurada
        axis= scc.getInternalForcesAxis()
        self.I= scc.getFibers().getHomogenizedSectionIRelToLine(self.E0,axis)
        self.S= scc.getFibers().getSPosHomogenizedSection(self.E0,geom.HalfPlane2d(axis))
        self.Vu2= getVu2EHE08NoAtNoFis(self.fctdH,self.I,self.S,self.strutWidth,self.alphaL,self.concreteAxialForce,self.concreteArea)

  def calcVuEHE08SiAt(self, preprocessor, scc, paramsTorsion, concrete, reinfSteel, Nd, Md, Vd, Td):
    ''' Calcula el cortante último de la sección WITH shear reinforcement.
     XXX Falta considerar la reinforcement activa.
     :param reinfSteelMaterialTag: reinforcement steel material identifier.
     :param concrete: Nombre del material empleado para modelizar el hormigón.
     :param reinfSteel: reinforcement steel material name.
     :param Nd: Design value of axial force (aquí positivo si es de tracción)
     :param Md: Absolute value of design value of bending moment.
     :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
     :param Td: Torsor de cálculo. '''
    self.VuAe= paramsTorsion.Ae()
    self.Vuue= paramsTorsion.ue()

    self.concreteMatTag= concrete.matTagD
    self.fckH= abs(concrete.fck)
    self.fcdH= abs(concrete.fcd())
    self.fctdH= abs(concrete.fctd())
    self.gammaC= abs(concrete.gmmC)
    self.reinfSteelMaterialTag= reinfSteel.matTagD
    self.fydS= reinfSteel.fyd()

    createFiberSets.fiberSectionSetupRC3Sets(scc,self.concreteMatTag,self.concreteFibersSetName,self.reinfSteelMaterialTag,self.rebarFibersSetName)
    concrFibers= scc.getFiberSets()[self.concreteFibersSetName]
    reinfFibers= scc.getFiberSets()[self.rebarFibersSetName]
    reinforcementTraccion= scc.getFiberSets()[self.tensionedRebarsFiberSetName]

    self.hayMom= scc.isSubjectedToBending(0.1)
    self.numBarrasTraccion= reinforcementTraccion.getNumFibers()
    self.concreteArea= concrFibers.getArea(1)
    if(self.concreteArea<1e-6):
      errMsg= "concrete area too smail; Ac= " + str(self.concreteArea) + " m2\n"
      lmsg.error(errMsg)
    else:
      if(self.hayMom):
        self.eps1= concrFibers.getStrainMax()
        self.E0= concrFibers[0].getMaterial().getInitialTangent()
        self.concreteAxialForce= concrFibers.ResultanteComp()
        self.modElastArmadura= reinfFibers[0].getMaterial().getInitialTangent()
        self.strutWidth= scc.getCompressedStrutWidth() # b0
        self.depthUtil= scc.getCantoUtil() # d
        self.brazoMecanico= scc.getBrazoMecanico() # z
        if(self.numBarrasTraccion>0):
          self.areaRebarTracc= reinforcementTraccion.getArea(1)
        else:
          self.areaRebarTracc= 0.0
        self.thetaFisuras= getCrackAngleEHE08(Nd,Md,Vd,Td,self.brazoMecanico,self.areaRebarTracc,0.0,self.modElastArmadura,0.0,0.0,self.VuAe,self.Vuue)
        self.Vcu= getVcuEHE08(self.fckH,self.fcdH,self.gammaC,self.concreteAxialForce,self.concreteArea,self.strutWidth,self.depthUtil,self.brazoMecanico,self.areaRebarTracc,0.0,self.theta,Nd,Md,Vd,Td,self.modElastArmadura,0.0,0.0,self.VuAe,self.Vuue)
        self.Vu1= getVu1EHE08(self.fckH,self.fcdH,self.concreteAxialForce,self.concreteArea,self.strutWidth,self.depthUtil,self.alpha,self.theta)
        self.Vsu= getVsuEHE08(self.brazoMecanico,self.alpha,self.theta,self.AsTrsv,self.fydS)
        self.Vu2= self.Vcu+self.Vsu
        self.Vu= min(self.Vu1,self.Vu2)
      else: # Sección no fisurada
        lmsg.error("La comprobación del cortante sin momento no está implementada.")

  def calcVuEHE08(self, preprocessor, scc, nmbParamsTorsion, concrete, reinfSteel, Nd, Md, Vd, Td):
    '''  Calcula el cortante último de la sección.
     XXX Falta considerar la reinforcement activa.
     :param concrete: parameters to model concrete.
     :param reinfSteel: parameters to model rebar's steel.
     :param Nd: Design value of axial force (aquí positivo si es de tracción)
     :param Md: Absolute value of design value of bending moment.
     :param Vd: Absolute value of cortante efectivo de cálculo (clause 42.2.2).
     :param Td: Torsor de cálculo.'''
    if(self.AsTrsv==0):
      self.calcVuEHE08NoAt(preprocessor,scc,concrete,reinfSteel)
    else:
      self.calcVuEHE08SiAt(preprocessor,scc,nmbParamsTorsion,concrete,reinfSteel,Nd,Md,Vd,Td)


  def check(self,elements,nmbComb):
    '''
    Comprobación de las secciones de hormigón frente a cortante.
       XXX Falta tener en cuenta la dirección de las barras de refuerzo
       a cortante.
    '''
    print "Postprocessing combination: ",nmbComb
    secHAParamsTorsion=  EHE_limit_state_checking.TorsionParameters()
    # XXX Ignore torsional deformation.
    secHAParamsTorsion.ue= 0
    secHAParamsTorsion.Ae= 1
    elementos= preprocessor.getSets.getSet("total").getElements
    for e in elementos:
      scc= e.getSection()
      idSection= e.getProp("idSection")
      section= scc.getProp("datosSecc")
      concreteCode= section.concrType
      codArmadura= section.reinfSteelType
      AsTrsv= section.shReinfY.getAs()
      alpha= section.shReinfY.angAlphaShReinf
      theta= section.shReinfY.angThetaConcrStruts
      NTmp= scc.getStressResultantComponent("N")
      MyTmp= scc.getStressResultantComponent("My")
      MzTmp= scc.getStressResultantComponent("Mz")
      MTmp= math.sqrt((MyTmp)**2+(MzTmp)**2)
      VyTmp= scc.getStressResultantComponent("Vy")
      VzTmp= scc.getStressResultantComponent("Vz")
      VTmp= math.sqrt((VyTmp)**2+(VzTmp)**2)
      TTmp= scc.getStressResultantComponent("Mx")
      secHAParamsCortante.calcVuEHE08(preprocessor,scc,secHAParamsTorsion,concreteCode,codArmadura,NTmp,MTmp,VTmp,TTmp)

      if(secHAParamsCortante.Vu<VTmp):
        theta= max(secHAParamsCortante.thetaMin,min(secHAParamsCortante.thetaMax,secHAParamsCortante.thetaFisuras))
        secHAParamsCortante.calcVuEHE08(preprocessor,scc,secHAParamsTorsion,concreteCode,codArmadura,NTmp,MTmp,VTmp,TTmp)
      if(secHAParamsCortante.Vu<VTmp):
        theta= (secHAParamsCortante.thetaMin+secHAParamsCortante.thetaMax)/2.0
        secHAParamsCortante.calcVuEHE08(preprocessor,scc,secHAParamsTorsion,concreteCode,codArmadura,NTmp,MTmp,VTmp,TTmp)
      if(secHAParamsCortante.Vu<VTmp):
        theta= 0.95*secHAParamsCortante.thetaMax
        secHAParamsCortante.calcVuEHE08(preprocessor,scc,secHAParamsTorsion,concreteCode,codArmadura,NTmp,MTmp,VTmp,TTmp)
      if(secHAParamsCortante.Vu<VTmp):
        theta= 1.05*secHAParamsCortante.thetaMin
        secHAParamsCortante.calcVuEHE08(preprocessor,scc,secHAParamsTorsion,concreteCode,codArmadura,NTmp,MTmp,VTmp,TTmp)
      VuTmp= secHAParamsCortante.Vu
      if(VuTmp!=0.0):
        FCtmp= VTmp/VuTmp
      else:
        FCtmp= 1e99
      if(FCtmp>=e.getProp("ULS_shear").CF):
        e.setProp("ULS_shear",cv.RCShearControlVars(idSection,nmbComb,FCtmp,NTmp,MyTmp,MzTmp,Mu,VyTmp,VzTmp,theta,secHAParamsCortante.Vcu,secHAParamsCortante.Vsu,VuTmp)) # Worst case


class CrackControl(lscb.CrackControlBaseParameters):
  '''
  Define the properties that will be needed for crack control checking
  as in clause 49.2.4 of EHE-08.'''

  def __init__(self,limitStateLabel):
    super(CrackControl,self).__init__(limitStateLabel)
    self.concreteArea= 0.0 #Concrete section area.
    self.fctmFis= 0.0 #Resistencia media del hormigón a tracción.
    self.tensSRMediaBarrasTracc= 0.0 #Tensión media en las barras traccionadas en fisuración.
    self.iAreaMaxima= None #Barra traccionada de área máxima.
    self.diamMaxTracc= 0.0 #Diámetro de la reinforcement traccionada más gruesa.
    self.EsBarrasTracc= 0.0 #Longitudinal deformation Modulus tensioned rebars.
    self.eps1= 0.0 #Maximum strain in concrete.
    self.eps2= 0.0 #Minimum strain in concrete.
    self.k1= 0.0 #Coeficiente que representa la influencia del diagrama de tracciones.
    self.k2= 0.5 #Coeficiente de valor 1.0 para carga instantánea no repetida y 0.5 para el resto de los casos.
    self.depthMecanico= 0.0 #Canto con el que está trabajando la sección.
    self.widthMecanico= 0.0 #Ancho con el que está trabajando la sección.
    self.razonAspecto= 0.0 #Cociente entre width y depth.
    self.hEfMax= 0.0 #Canto máximo del área eficaz.
    self.AcEfBruta= 0.0 #Área eficaz bruta.
    self.AcEfNeta= 0.0 #Área eficaz neta.
    self.E0= 0.0 #Módulo de rigidez tangente del hormigón.
    self.beta= 1.7 #Coeficiente que relaciona el valor característico de la apertura de fisura con el valor medio y que vale 1.3 para fisuración producida exclusivamente por acciones indirectas y 1.7 en el resto de los casos.
    self.Wk= 0.0 #Apertura característica de fisuras.
    
  def printParams(self):
    # Imprime los parámetros de fisuración de la sección.
    print "Num. reinforcement a tracción: ",self.numBarrasTracc,"\n"
    print "Spacement of the tensioned bars; s= ",self.rebarsSpacingTracc," m\n"
    print "Area de las reinforcement traccionadas; As= ",self.areaRebarTracc*1e4," cm2\n"
    print "Area eficaz; AcEf= ",self.AcEfNeta*1e4," cm2\n"
    print "Centro de gravedad de las reinforcement traccionadas; CDG= (",self.yCDGBarrasTracc,",",self.zCDGBarrasTracc,") m\n"
    print "Tensión media en barras traccionadas= ",self.tensMediaBarrasTracc/1e6," MPa\n"
    print "Tensión media en fisuración en barras traccionadas= ",self.tensSRMediaBarrasTracc/1e6," MPa\n"
    print "Deformación máxima en la zona traccionada de hormigón; eps1= ",self.eps1*1e3," por mil.\n"
    print "Deformación mínima en la zona traccionada de hormigón; eps2= ",self.eps2*1e3," por mil.\n"
    print "Influencia del diagrama de tracciones; k1= ",self.k1,"\n"
    print "Canto mecánico; h= ",self.depthMecanico," m\n"
    print "Lever arm; z= ",self.brazoMecanico," m\n"
    print "Ancho mecánico; b= ",self.widthMecanico," m\n"
    print "Razón aspecto; r= ",self.razonAspecto,"\n"
    print "Canto máximo para el área eficaz; hEfMax= ",self.hEfMax," m\n"
    print "Resistencia media a tracción; fctm= ",self.fctmFis/1e6," MPa\n"
    print "Modulo de deformación longitudinal tangente; E0= ",self.E0/1e9," GPa\n"
    print "Apertura característica de fisuras; Wk= ",self.Wk*1e3," mm\n"



  # Calcula la apertura característica de fisura.
  def calcApertCaracFis(self, scc, concreteMatTag, reinfSteelMaterialTag, fctm):
    if(self.rcSets == None):
      self.rcSets= createFiberSets.fiberSectionSetupRC3Sets(scc,concreteMatTag,self.concreteFibersSetName,reinfSteelMaterialTag,self.rebarFibersSetName)
    concrFibers= self.rcSets.concrFibers.fSet
    reinfFibers= self.rcSets.reinfFibers.fSet
    reinforcementTraccion= self.rcSets.tensionFibers

    self.fctmFis= fctm
    self.claseEsfuerzo= scc.getStrClaseEsfuerzo(0.0)
    self.numBarrasTracc= self.rcSets.getNumTensionRebars()
    self.Wk= 0.0
    if(self.numBarrasTracc>0):
      scc.computeCovers(self.tensionedRebarsFiberSetName)
      scc.computeSpacement(self.tensionedRebarsFiberSetName)
      self.eps1= concrFibers.getStrainMax()
      self.eps2= max(concrFibers.getStrainMin(),0.0)
      self.k1= (self.eps1+self.eps2)/8/self.eps1
      self.E0= concrFibers[0].getMaterial().getInitialTangent()
      self.concreteArea= concrFibers.getSumaAreas(1)
      self.depthMecanico= scc.getLeverArm()
      self.brazoMecanico= scc.getBrazoMecanico() # z
      self.widthMecanico= scc.getAnchoMecanico()
      self.razonAspecto= self.widthMecanico/self.depthMecanico
      if(self.razonAspecto>1):
        self.hEfMax= self.depthMecanico/4.0 # Pieza tipo losa
      else:
        self.hEfMax= self.depthMecanico/2.0
      self.AcEfNeta= scc.computeFibersEffectiveConcreteArea(self.hEfMax,self.tensionedRebarsFiberSetName,15)

      self.rebarsSpacingTracc= reinforcementTraccion.getAverageDistanceBetweenFibers()
      self.areaRebarTracc= reinforcementTraccion.getArea(1)
      self.yCDGBarrasTracc= reinforcementTraccion.getCdgY()
      self.zCDGBarrasTracc= reinforcementTraccion.getCdgZ()
      self.tensMediaBarrasTracc= reinforcementTraccion.getStressMed()
      self.iAreaMaxima=  fiberUtils.getIMaxPropFiber(reinforcementTraccion,"getArea")
      self.diamMaxTracc= 2*math.sqrt(reinforcementTraccion[self.iAreaMaxima].getArea()/math.pi) 

      self.EsBarrasTracc= reinforcementTraccion[0].getMaterial().getInitialTangent()
      AsBarra= 0.0
      coverBarra= 0.0
      sepBarra= 0.0
      diamBarra= 0.0
      sigmaBarra= 0.0
      sigmaSRBarra= 0.0
      smFisurasBarra= 0.0
      alargMaxBarra= 0.0
      alargMedioBarra= 0.0
      tensSRMediaBarrasTracc= 0.0
      WkBarra= 0.0
      sz= len(reinforcementTraccion)
      for i in range(0,sz):
        barra= reinforcementTraccion[i]
        AsBarra= barra.getArea()
        posBarra= barra.getPos()
        yBarra= posBarra.x
        zBarra= posBarra.y
        sigmaBarra= barra.getMaterial().getStress()
        coverBarra= reinforcementTraccion.getFiberCover(i)
        diamBarra= reinforcementTraccion.getEquivalentDiameterOfFiber(i)
        sigmaSRBarra= reinforcementTraccion.getSigmaSRAtFiber(i,self.E0,self.EsBarrasTracc,self.fctmFis)
        tensSRMediaBarrasTracc+= AsBarra*sigmaSRBarra

        AcEfBarra= reinforcementTraccion.getFiberEffectiveConcreteArea(i)
        sepBarra= min(reinforcementTraccion.getFiberSpacing(i),15*diamBarra)
        smFisurasBarra= 2*coverBarra+0.2*sepBarra+0.4*self.k1*diamBarra*AcEfBarra/AsBarra
        alargMaxBarra= sigmaBarra/self.EsBarrasTracc
        alargMedioBarra= max(1.0-self.k2*(sigmaSRBarra/sigmaBarra)**2,0.4)*alargMaxBarra
        WkBarra=  self.beta*smFisurasBarra*alargMedioBarra
        self.Wk= max(self.Wk,WkBarra)
        # \printParamFisBarra()
      self.tensSRMediaBarrasTracc= self.tensSRMediaBarrasTracc/self.areaRebarTracc
  def check(self,elements,nmbComb):
    ''' Crack control of concrete sections.'''
    print "Postprocessing combination: ",nmbComb,"\n"

    defParamsFisuracion("secHAParamsFisuracion")
    materiales= preprocessor.getMaterialLoader
    concrete= materiales.getMaterial(concreteCode)
    concrTag= concrete.getProp("matTagK")
    concrFctm= concrete.getProp("fctm")
    reinforcement= materiales.getMaterial(codArmadura)
    for e in elements:
      scc= elements.getSeccion()
      Ntmp= scc.N
      MyTmp= scc.My
      MzTmp= scc.Mz
      secHAParamsFisuracion= calcApertCaracFis(concrTag,tagArmadura,concrFctm)
      Wk= secHAParamsFisuracion.Wk
      if(Wk>WkCP):
        WkCP= Wk # Caso pésimo
        HIPCP= nmbComb
        NCP= Ntmp
        MyCP= MyTmp
        MzCP= MzTmp

      

def printParamFisBarra():
# Imprime los parámetros de fisuración de una barra.
  print "\niBarra= ",iBarra,"\n"
  print "Área eficaz Acef= ",AcEfBarra*1e4," cm2\n"
  print "Área barra As= ",AsBarra*1e4," cm2\n"
  print "Pos barra: (",yBarra,",",zBarra,")\n"
  print "Cover c= ",coverBarra," m\n"
  print "diamBarra fi= ",diamBarra,"\n"
  print "sigmaBarra= ",sigmaBarra/1e6," MPa\n"
  print "sigmaSRBarra= ",sigmaSRBarra/1e6," MPa\n"
  print "Bar spacement s= ",sepBarra," m\n"
  print "k1= ",k1,"\n"
  print "smFisurasBarra= ",smFisurasBarra," m\n"
  print "alargMaxBarra= ",alargMaxBarra*1e3," por mil.\n"
  print "alargMedioBarra= ",alargMedioBarra*1e3," por mil.\n"
  print "WkBarra= ",WkBarra*1e3," mm\n\n"


class TorsionParameters(object):
  '''Methods for checking reinforced concrete section under torsion according to
     clause 45.1 or EHE-08.'''
  def __init__(self):
    self.h0= 0.0  # Real wall thickess.
    self.c= 0.0  # Longitudinal reinforcement concrete cover.

    self.crossSectionContour= geom.Poligono2d()  # Cross section contour.
    self.lineaMedia=  geom.Poligono2d() # Polygon defined by the midline of the effective hollow section.
    self.lineaInt=  geom.Poligono2d() # Polygon defined by the interior contour of the effective hollow section.
    self.seccionHuecaEficaz= geom.PoligonoConAgujeros2d() # Effective hollow section contour
  def A(self):
    return self.crossSectionContour.getArea()
  def u(self):
    return self.crossSectionContour.getPerimetro()
  def he(self):
    return max(2*self.c,min(self.A()/self.u(),self.h0))
  def Ae(self):
    return self.lineaMedia.getArea()
  def ue(self):
    return self.lineaMedia.getPerimetro()

def calcParamsSeccionHuecaEficaz(geomSeccion, h0, c):
  '''
  Calcula los parámetros de torsión que se deducen
   de la sección hueca eficaz. No es válido si la sección no es convexa.
  :param gmSectionName: Identificador de la definición geométrica de la sección.
  nmbParamsTorsión: Identificador del registro que contiene los parámetros de cálculo
                de la resistencia a torsión.
  :param h0: Real thickness of the section wall.
  :param c: cover of the longitudinal reinforcement.
  '''
  retval= TorsionParameters()
  retval.h0= h0
  retval.c= c
  retval.crossSectionContour= geomSeccion.getRegionsContour()
  he= retval.he()
  retval.lineaMedia= retval.crossSectionContour.offset(-he/2)
  retval.lineaInt= retval.crossSectionContour.offset(-he)
  retval.seccionHuecaEficaz.contour(retval.crossSectionContour)
  retval.seccionHuecaEficaz.addHole(retval.lineaInt)
  return retval



# Cuantía geométrica mínima en pilares.
def cuantiaGeomMinPilares(Ac):
  return 0.004*Ac 

# Cuantía mecánica mínima en pilares.
def cuantiaMecMinPilares(Nd, fyd):
  return 0.1*Nd/fyd 

# Cuantía máxima en pilares.
def cuantiaMaxPilares(Ac, fcd, fyd):
  return min((fcd*Ac)/fyd,0.08*Ac)
 
# Verificación de la cuantía de la reinforcement longitudinal en pilares.
def verifCuantiaPilar(Ac, As, fcd, fyd, Nd):
  ctMinGeom= cuantiaGeomMinPilares(Ac)
  if(As<ctMinGeom):
    print "Cuantía de reinforcement dispuesta: ",As*1e4," cm2, inferior a la mínima geométrica: ",ctMinGeom*1e4," cm2\n"
  ctMinMec= cuantiaMecMinPilares(Nd,fyd)
  if(As<ctMinMec):
    print "Cuantía de reinforcement dispuesta: ",As*1e4," cm2, inferior a la mínima mecánica: ",ctMinMec*1e4," cm2\n"
  ctMax= cuantiaMaxPilares(Ac,fcd,fyd)
  if(As>ctMax):
    print "Cuantía de reinforcement dispuesta: ",As*1e4," cm2, superior a la máxima: ",ctMax*1e4," cm2\n"


class ConcreteCorbel(object):
    '''Concrete corbel as in EHE-08 design code.'''
    def __init__(self,concrete, steel, jointType):
        '''
        Constructor.

        :param concrete: concrete material for corbel.
        :param concrete: steel material for corbel reinforcement.
        :param jointType: corbel to column joint quality
        ("monolitica", "junta" o "junta_debil").
        '''
        self.concrete= concrete
        self.steel= steel
        self.jointType= jointType
        
    def getCotgStrutAngle(self):
        '''getCotgStrutAngle()
 
          Return the cotangent of the angle between the concrete
          compressed strut an the vertical according to 
          clause 64.1.2.1 de EHE-08.
        '''
        if self.jointType=="monolitica":
            retval=1.4
        elif self.jointType=="junta":
            retval=1.0
        elif self.jointType=="junta_debil":
            retval=0.6
        return retval

    def getCantoUtilMinimo(self, a):
        '''getCantoUtilMinimo(self, a) return the minimal effective depth of
        the corbel according to clause 64.1.2.1 of EHE-08.

        :param a: Distancia (m) entre el eje de la carga aplicada y la sección
        de empotramiento de la ménsula (see figure 64.1.2 de EHE-08).
        '''
        return a*self.getCotgStrutAngle()/0.85

    def getTraccionMainReinforcement(self, Fv,Fh):
        '''getTraccionMainReinforcement(self, Fv,Fh)

        :param Fv: Vertical load on the corbel, positive downwards (N).
        :param Fh: Horizontal load on the corbel, positive outwards (N).

        Devuelve la tracción en la armadura principal de la ménsula according
        to clause 64.1.2.1.1 of EHE-08.
        '''
        return Fv/self.getCotgStrutAngle()+Fh

    def getAreaNecMainReinforcement(self, Fv,Fh):
        '''getAreaNecMainReinforcement(self, Fv,Fh)

        :param Fv: Vertical load on the corbel, positive downwards (N).
        :param Fh: Horizontal load on the corbel, positive outwards (N).

        Devuelve el área necesaria para la reinforcement principal de 
        la ménsula according to apartado 64.1.2.1.1 de EHE-08.
        '''
        return self.getTraccionMainReinforcement(Fv,Fh)/min(self.steel.fyd(),400e6)
    @staticmethod
    def getTraccionCercos(Fv):
        ''' getTraccionCercos(Fv)

        :param Fv: Vertical load on the corbel, positive downwards (N).

        Devuelve la tracción en los cercos according to apartado 64.1.2.1.1 
        de EHE-08.
        '''
        return 0.2*Fv

    def getAreaNecCercos(self,Fv):
        '''getAreaNecCercos(self,Fv)

        :param Fv: Vertical load on the corbel, positive downwards (N).

        Devuelve el área necesaria para los cercos de la ménsula according
        to clause 64.1.2.1.1 de EHE-08.
        '''
        return self.getTraccionCercos(Fv)/min(self.steel.fyd(),400e6)

    def getAreaNecApoyo(self,Fv):
        '''getAreaNecApoyo(self,Fv)

        :param Fv: Vertical load on the corbel, positive downwards (N).

        Devuelve el área necesaria para el apoyo according
        to clause 64.1.2.1.2 de EHE-08.
        '''
        return Fv/0.7/-self.concrete.fcd()

EC2table48_x= [12.0e6,16.0e6,20.0e6,25.0e6,30.0e6,35.0e6,40.0e6,45.0e6,50.0e6]
EC2table48_y= [0.18,0.22,0.26,0.30,0.34,0.37,0.41,0.44,0.48]
EC2table48= scipy.interpolate.interp1d(EC2table48_x,EC2table48_y)


def shearBetweenWebAndFlangesStrength(fck,gammac,hf,Asf,Sf,fyd):
    ''' Return the shear strength (kN/m) in the flage web contact by unit length
    according to clause 4.3.2.5 of Eurocode 2

    Parameters:
    :param fck: concrete characteristic compressive strength (Pa).
    :param gammac: Partial safety factor for concrete.
    :param hf: flange thickness (m)
    :param Asf: reinforcement that cross the section by unit length (m2)
    :param Sf: spacement of the rebars that cross the section (m)
    :param fyd: design yield strength (Pa)
    '''
    hf=hf*1000     #Flange thickness in mm
    #Oblique compression strength.
    fcd=fck/gammac
    VRd2=0.2*fcd*hf
    #Section tensile strength
    taoRd= EC2table48(fck)
    VRd3=2.5*taoRd*hf+Asf/Sf*fyd
    return min(VRd2,VRd3)

#Example:
#  esfRasMax= shearBetweenWebAndFlangesStrength(25e6,1.5,0.3,565e-6,0.2,500e6)


# Checking of solid block members under concentrated loads, according to clause
# 61 of EHE-08


class BlockMember(object):
  def __init__(self,a,b,a1,b1):
    '''
    Constructor.

    Parameters:
      :param a: side length.
      :param a1: lenght of the side of the loaded area parallel to a.
      :param b: side length.
      :param b1: lenght of the side of the loaded area parallel to b.
    '''
    self.a= a
    self.a1= a1
    self.b= b
    self.b1= b1
  def getAc(self):
    '''Return area of the block member.'''
    return self.a*self.b
  def getAc1(self):
    '''Return block member loaded area.'''
    return self.a1*self.b1
  def getF3cd(self, fcd):
    '''Return the value of f3cd.'''
    return min(sqrt(self.getAc()/self.Ac1()),3.3)*fcd
  def getNuConcentratedLoad(self, fcd):
    '''
    Return the the maximum compressive force that can be obtained in the
    Ultimate Limit State of on a restricted surface (see figure 61.1.a on
    page 302 of EHE-08), of area Ac1 , concentrically and homothetically 
    situated on another area, Ac.

    Parameters:
    :param fcd: design compressive strength of concrete.
    '''
    return self.getAc1()*self.getF3cd(fcd)
  def getUad(self, Nd):
      '''
      Return the design tension for the transverse reinforcement in
      a direction parallel to side a (see figure 61.1.a page 302 EHE-08).

      Parameters:
        :param Nd: concentrated load.
      '''
      return 0.25*((self.a-self.a1)/self.a)*Nd
  def getReinforcementAreaAd(self, Nd, fyd):
      '''
      Return the area of the reinforcement parallel to side a
      (see figure 61.1.a page 302 EHE-08)

        :param Nd: concentrated load.
        :param fyd: steel yield strength.
      '''
      return self.getUad(Nd)/min(fyd,400e6)
  def getUbd(self, Nd):
      '''
      Return the design tension for the transverse reinforcement in
      a direction parallel to side b (see figure 61.1.a page 302 EHE-08).

        :param Nd: concentrated load.

      '''
      return 0.25*((self.b-self.b1)/self.b)*Nd
  def getReinforcementAreaBd(Nd, fyd):
      '''
      Return the area of the reinforcement parallel to side b
      (see figure 61.1.a page 302 EHE-08)

        :param Nd: concentrated load.
        :param fyd: steel yield strength.

      '''
      return self.getUbd(Nd)/min(fyd,400e6)
