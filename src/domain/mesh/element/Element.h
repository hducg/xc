//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  This program derives from OpenSees <http://opensees.berkeley.edu>
//  developed by the  «Pacific earthquake engineering research center».
//
//  Except for the restrictions that may arise from the copyright
//  of the original program (see copyright_opensees.txt)
//  XC is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or 
//  (at your option) any later version.
//
//  This software is distributed in the hope that it will be useful, but 
//  WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details. 
//
//
// You should have received a copy of the GNU General Public License 
// along with this program.
// If not, see <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
/* ****************************************************************** **
**    OpenSees - Open System for Earthquake Engineering Simulation    **
**          Pacific Earthquake Engineering Research Center            **
**                                                                    **
**                                                                    **
** (C) Copyright 1999, The Regents of the University of California    **
** All Rights Reserved.                                               **
**                                                                    **
** Commercial use of this program without express permission of the   **
** University of California, Berkeley, is strictly prohibited.  See   **
** file 'COPYRIGHT'  in main directory for information on usage and   **
** redistribution,  and for a DISCLAIMER OF ALL WARRANTIES.           **
**                                                                    **
** Developed by:                                                      **
**   Frank McKenna (fmckenna@ce.berkeley.edu)                         **
**   Gregory L. Fenves (fenves@ce.berkeley.edu)                       **
**   Filip C. Filippou (filippou@ce.berkeley.edu)                     **
**                                                                    **
** ****************************************************************** */

// $Revision: 1.12 $
// $Date: 2005/02/17 22:29:54 $
// $Source: /usr/local/cvs/OpenSees/SRC/element/Element.h,v $


// Written: fmk
// Created: 11/96
// Revision: A
//
// Description: This file contains the class definition for Element.
// Element is an abstract base class and thus no objects of it's type
// can be instantiated. It has pure virtual functions which must be
// implemented in it's derived classes.
//
// What: "@(#) Element.h, revA"

#ifndef Element_h
#define Element_h

#include "domain/mesh/MeshComponent.h"
#include "preprocessor/MeshingParams.h"
#include "domain/mesh/element/utils/RayleighDampingFactors.h"
#include "utility/matrix/Matrix.h"
#include "domain/mesh/node/NodeTopology.h"

class TritrizPos3d;
class Pos2d;
class Pos3d;
class SisCooRect3d3d;
class GeomObj2d;
class GeomObj3d;

namespace XC {
class Vector;
class Renderer;
class Info;
class Information;
class Parameter;
class Response;
class ElementalLoad;
class Node;
class TritrizPtrNod;
class TritrizPtrElem;
class SetBase;
class SetEstruct;
class NodePtrsWithIDs;
class Material;
class DqVectors;
class DqMatrices;
class DefaultTag;
class GaussModel;
class MEDGaussModel;
class ParticlePos3d;

//! \ingroup Mesh
//
//! @defgroup Elem Finite elements.
//
//! \ingroup Elem
//! @brief Base calass for the finite elements.
class Element: public MeshComponent
  {
  public:
    static double dead_srf;//!< Stress reduction factor for foozen elements.
    typedef std::vector<const Node *> NodesEdge; //!< Nodes on an element edge.
    //! @brief Assigns Stress Reduction Factor for element deactivation.
    inline static void setDeadSRF(const double &d)
      { dead_srf= d; }
  private:
    int nodeIndex;

    static std::deque<Matrix> theMatrices;
    static std::deque<Vector> theVectors1;
    static std::deque<Vector> theVectors2;

    void compute_damping_matrix(Matrix &) const;
    static DefaultTag defaultTag; //<! default tag for next new element.
  protected:
    friend class EntMdlr;
    friend class Preprocessor;
    virtual TritrizPtrElem put_on_mesh(const TritrizPtrNod &,meshing_dir) const;
    virtual TritrizPtrElem cose(const SetEstruct &f1,const SetEstruct &f2) const;

    const Vector &getRayleighDampingForces(void) const;

    Vector load;//!< vector for applying loads
    mutable RayleighDampingFactors rayFactors; //!< Rayleigh damping factors
                                             //(mutable para que getDamp pueda ser const).
    mutable Matrix Kc; //!< pointer to hold last committed matrix if needed for rayleigh damping
                        //(mutable para que getDamp pueda ser const).
    int sendData(CommParameters &cp);
    int recvData(const CommParameters &cp);

  public:
    Element(int tag, int classTag);
    virtual Element *getCopy(void) const= 0;

    static DefaultTag &getDefaultTag(void);

    // methods dealing with nodes and number of external dof
    virtual int getNumExternalNodes(void) const =0;
    virtual int getNumEdges(void) const;
    virtual NodePtrsWithIDs &getNodePtrs(void)= 0;	
    virtual const NodePtrsWithIDs &getNodePtrs(void) const= 0;	
    std::vector<int> getIdxNodes(void) const;
    virtual int getNumDOF(void) const= 0;
    virtual size_t getDimension(void) const;
    virtual void setIdNodos(const std::vector<int> &inodos);
    virtual void setIdNodos(const ID &inodos);
    void setDomain(Domain *theDomain);

    // methods dealing with committed state and update
    virtual int commitState(void);
    virtual int revertToLastCommit(void) = 0;
    virtual int revertToStart(void);
    virtual int update(void);
    virtual bool isSubdomain(void);

    // methods to return the current linearized stiffness,
    // damping and mass matrices
    virtual const Matrix &getTangentStiff(void) const= 0;
    virtual const Matrix &getInitialStiff(void) const= 0;
    virtual const Matrix &getDamp(void) const;
    virtual const Matrix &getMass(void) const;

    // methods for applying loads
    virtual void zeroLoad(void);	
    virtual int addLoad(ElementalLoad *theLoad, double loadFactor)=0;
    virtual int addInertiaLoadToUnbalance(const Vector &accel)=0;

    virtual int setRayleighDampingFactors(const RayleighDampingFactors &rF) const;

    // methods for obtaining resisting force (force includes elemental loads)
    virtual const Vector &getResistingForce(void) const= 0;
    virtual const Vector &getResistingForceIncInertia(void) const;
    const Vector &getNodeResistingComponents(const size_t &,const Vector &) const;
    const Vector &getNodeResistingForce(const size_t &iNod) const;
    const Vector &getNodeResistingForceIncInertia(const size_t &iNod) const;
    const Vector &getNodeResistingForce(const Node *) const;
    const Vector &getNodeResistingForceIncInertia(const Node *) const;
    Vector getEquivalentStaticLoad(int mode,const double &) const;
    Matrix getEquivalentStaticNodalLoads(int mode,const double &) const;

    // method for obtaining information specific to an element
    virtual Response *setResponse(const std::vector<std::string> &argv, Information &eleInformation);
    virtual int getResponse(int responseID, Information &eleInformation);
    Response *setMaterialResponse(Material *,const std::vector<std::string> &,const size_t &,Information &);

// AddingSensitivity:BEGIN //////////////////////////////////////////
    virtual int addInertiaLoadSensitivityToUnbalance(const Vector &accel, bool tag);
    virtual int setParameter(const std::vector<std::string> &argv, Parameter &param);
    int setMaterialParameter(Material *,const std::vector<std::string> &,const size_t &, Parameter &);
    virtual int updateParameter(int parameterID, Information &info);
    virtual int activateParameter(int parameterID);
    virtual const Vector &getResistingForceSensitivity(int gradNumber);
    virtual const Matrix &getInitialStiffSensitivity(int gradNumber);
    virtual const Matrix &getDampSensitivity(int gradNumber);
    virtual const Matrix &getMassSensitivity(int gradNumber);
    virtual int   commitSensitivity(int gradNumber, int numGrads);
// AddingSensitivity:END ///////////////////////////////////////////

    virtual int addResistingForceToNodalReaction(bool inclInertia);

    double MaxCooNod(int i) const;
    double MinCooNod(int i) const;
    const Matrix &getCooNodes(void) const;
    virtual Matrix getLocalAxes(bool initialGeometry= true) const;
    virtual Vector getBaseVector(size_t i,bool initialGeometry= true) const;
    virtual Vector3d getBaseVector3d(size_t i,bool initialGeometry= true) const;
    virtual Vector3d getIVector3d(bool initialGeometry= true) const;
    virtual Vector3d getJVector3d(bool initialGeometry= true) const;
    virtual Vector3d getKVector3d(bool initialGeometry= true) const;
    virtual SisCooRect3d3d getSisCoo(bool) const;    
    Pos3d getPosNode(const size_t &i,bool initialGeometry= true) const;
    std::list<Pos3d> getPosNodes(bool initialGeometry= true) const;
    virtual Pos3d getPosCdg(bool initialGeometry= true) const;
    Vector getCooCdg(bool initialGeometry= true) const;
    TritrizPos3d getPuntos(const size_t &ni,const size_t &nj,const size_t &nk,bool initialGeometry= true);
    bool In(const GeomObj3d &,const double &factor= 1.0, const double &tol= 0.0) const;
    bool Out(const GeomObj3d &,const double &factor= 1.0, const double &tol= 0.0) const;
    bool In(const GeomObj2d &,const double &factor= 1.0, const double &tol= 0.0) const;
    bool Out(const GeomObj2d &,const double &factor= 1.0, const double &tol= 0.0) const;
    virtual double getDist2(const Pos2d &p,bool initialGeometry= true) const;
    virtual double getDist(const Pos2d &p,bool initialGeometry= true) const;
    virtual double getDist2(const Pos3d &p,bool initialGeometry= true) const;
    virtual double getDist(const Pos3d &p,bool initialGeometry= true) const;

    void resetTributaries(void) const;
    void dumpTributaries(const std::vector<double> &) const;
    virtual void computeTributaryLengths(bool initialGeometry= true) const;
    virtual double getTributaryLength(const Node *) const;
    virtual double getTributaryLengthByTag(const int &) const;
    virtual void computeTributaryAreas(bool initialGeometry= true) const;
    virtual double getTributaryArea(const Node *) const;
    virtual double getTributaryAreaByTag(const int &) const;
    virtual void computeTributaryVolumes(bool initialGeometry= true) const;
    virtual double getTributaryVolume(const Node *) const;
    virtual double getTributaryVolumeByTag(const int &) const;

    virtual Vector getInterpolationFactors(const ParticlePos3d &) const;
    virtual Vector getInterpolationFactors(const Pos3d &) const;

    virtual int getVtkCellType(void) const;
    virtual int getMEDCellType(void) const;
    virtual const GaussModel &getGaussModel(void) const;
    MEDGaussModel getMEDGaussModel(void) const;
    virtual NodesEdge getNodesEdge(const size_t &) const;
    virtual int getEdgeNodes(const Node *,const Node *) const;
    int getEdgeNodes(const int &,const int &) const;
    virtual ID getEdgesNode(const Node *) const;
    std::set<int> getEdgesNodes(const NodePtrSet &) const;
    ID getEdgesNodeByTag(const int &) const;
    virtual ID getLocalIndexNodesEdge(const size_t &i) const;
    
    virtual std::set<std::string> getMaterialNames(void) const;
    boost::python::list getMaterialNamesPy(void) const;

    

    std::set<SetBase *> get_sets(void) const;
    void add_to_sets(std::set<SetBase *> &);

  };
} // end of XC namespace

#endif

