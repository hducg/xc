# -*- coding: utf-8 -*-


__author__= "Ana Ortega (AO_O)"
__copyright__= "Copyright 2017, AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "ana.Ortega@ciccp.es"

import xc_base
import geom
import xc
from miscUtils import LogMessages as lmsg

class SetToMesh(object):
    '''Base for classes that mesh a primitive set.
    
    :ivar primitiveSet: set of lines/surfaces/blocks.
    :ivar elemSize: mean size of the elements (in elemSize= None don't 
                    change number of divisions).
    :ivar elemType: type of element for the mesh.
    '''
    def __init__(self,primitiveSet,elemSize,elemType):
        '''Constructor.'''
        self.primitiveSet= primitiveSet
        self.elemSize= elemSize
        self.elemType= elemType

class RawLineSetToMesh(SetToMesh):
    '''Define the parameters to mesh a set of lines. The method generateMesh
    meshes those lines and adds the nodes and elements created to the set .
    
    :ivar matSect: instance of the class BeamMaterialData that defines the 
          material-section to be applied to the set of lines.
    :ivar coordTransf: coordinate transformation for the elements.
    :ivar dimElemSpace: dimension of the element space (defaults to 3)
    '''
    def __init__(self,linSet,matSect,elemSize,coordTransf, elemType='elastic_beam_3d',dimElemSpace=3):
        super(RawLineSetToMesh,self).__init__(linSet,elemSize,elemType)
        self.matSect= matSect
        self.coordinateTransformation= coordTransf
        self.dimElemSpace=dimElemSpace

    def getSeedElement(self, preprocessor):
        '''Return the element that will be use to mesh the set.'''
        seedElemLoader= preprocessor.getElementLoader.seedElemLoader
        seedElemLoader.defaultMaterial= self.matSect.name
        seedElemLoader.dimElem= self.dimElemSpace
        #print 'name= ', self.coordinateTransformation.getName()
        seedElemLoader.defaultTransformation= self.coordinateTransformation.getName()
        return seedElemLoader.newElement(self.elemType,xc.ID([0,0]))

    def generateMesh(self, preprocessor):
        '''Generate the mesh for the line set. '''
        elem= self.getSeedElement(preprocessor)
        for l in self.primitiveSet.getLines:
            if(self.elemSize): #If elemSize==None don't touch the number of divisions.
                l.setElemSize(self.elemSize)
            l.genMesh(xc.meshDir.I)
        self.primitiveSet.fillDownwards()

def getDefaultCoordinateTransformation(preprocessor,coordTransfName,coordTransfType,vDir):
    '''Creates a default coordinate transformation.''' 
    trfs= preprocessor.getTransfCooLoader
    if coordTransfType.lower()=='pdelta':
        retval= trfs.newPDeltaCrdTransf3d(coordTransfName)
    elif coordTransfType.lower()=='corot':
        retval= trfs.newCorotCrdTransf3d(coordTransfName)
    else:
        retval= trfs.newLinearCrdTransf3d(coordTransfName)
    retval.xzVector= vDir
    '''   13.11.2017 
    retval= trfs.getCoordTransf(coordTransfName)
    if(retval==None):
      msg= "getDefaultCoordinateTransformation creates a PDelta"
      msg+= " 3D coordinate transformation which is not necessarily"
      msg+= " the best choice for your element."
      lmsg.warning(msg)
      retval= trfs.newPDeltaCrdTransf3d(coordTransfName) #XXX PDelta???
      retval.xzVector= vDir
    '''
    return retval


class LinSetToMesh(RawLineSetToMesh):
    '''Define the parameters to mesh a set of lines. The method generateMesh
    meshes those lines and adds the nodes and elements created to the set .
    
    :ivar matSect: instance of the class BeamMaterialData that defines the 
          material-section to be applied to the set of lines.
    :ivar vDirLAxZ: direction vector for the element local axis Z 
          defined as xc.Vector([x,y,z]). This is the direction in which
          the Z local axis of the sections will be
          oriented (i.e. in the case of rectangular sections this Z 
          local axis of the section is parallel to the dimension
          defined as width of the rectangle)
    :ivar dimElemSpace: dimension of the element space (defaults to 3)
    :ivar coordTransfType: type of coordinate transformation. Available 
                       types: 'linear', 'PDelta' and 'corot' (defaults to 
                       'linear') 
    '''
    def __init__(self,linSet,matSect,elemSize,vDirLAxZ, elemType='elastic_beam_3d',dimElemSpace=3,coordTransfType='linear'):
        self.vDirLAxZ= vDirLAxZ
        trfName= linSet.name+'trYGlobal'
        cTrf= getDefaultCoordinateTransformation(linSet.owner,trfName,coordTransfType,self.vDirLAxZ)
        super(LinSetToMesh,self).__init__(linSet,matSect,elemSize,cTrf,elemType,dimElemSpace)

   
class SurfSetToMesh(SetToMesh):
    '''Define the parameters to mesh a set of surfaces. The method generateMesh
    meshes those surfaces and adds the nodes and elements created to the set .
    
    :ivar surfSet: set of surfaces.
    :ivar matSect: instance of the class DeckMaterialData that defines the 
          material-section to be applied to the set of surfaces.
    :ivar elemType: type of element for the mesh (defaults to 'shell_mitc4')
    '''
    def __init__(self,surfSet,matSect,elemSize,elemType='shell_mitc4'):
        super(SurfSetToMesh,self).__init__(surfSet,elemSize,elemType)
        self.matSect= matSect

    def getSeedElement(self, preprocessor):
        '''Return the element that will be use to mesh the set.'''
        seedElemLoader= preprocessor.getElementLoader.seedElemLoader
        seedElemLoader.defaultMaterial= self.matSect.name
        return seedElemLoader.newElement(self.elemType,xc.ID([0,0,0,0]))

    def generateMesh(self, preprocessor):
        '''Generate the mesh for the surface set.'''
        for s in self.primitiveSet.getSurfaces:
            if(self.elemSize): #If elemSize= None don't touch the number of divisions.
                s.setElemSizeIJ(self.elemSize,self.elemSize)
        preprocessor.getCad.getSurfaces.conciliaNDivs()
        elem= self.getSeedElement(preprocessor)
        for s in self.primitiveSet.getSurfaces:
            s.genMesh(xc.meshDir.I)
        self.primitiveSet.fillDownwards()


def multi_mesh(preprocessor,lstMeshSets):
    '''Mesh all the mesh-sets included in lstMeshSets

    :param preprocessor: preprocessor
    :param lstMeshSets: list of instances of classes LinSetToMesh or 
           SurfSetToMesh to be meshed
    '''
    for ms in lstMeshSets:
        ms.generateMesh(preprocessor)
