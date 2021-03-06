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
                                                                        
// $Revision: 1.11 $
// $Date: 2006/01/10 18:41:34 $
// $Source: /usr/local/cvs/OpenSees/SRC/element/brick/Brick.h,v $

// Ed "C++" Love
//
// Eight node Brick element 
//

#include <domain/mesh/element/volumen/BrickBase.h>
#include "domain/mesh/element/utils/body_forces/BodyForces3D.h"

namespace XC {
//! \ingroup ElemVol
//
//! @brief Hexaedro de ocho nodos.
class Brick : public BrickBase
  {
  private : 
    BodyForces3D bf; //!< Body forces
    mutable Matrix *Ki;

    //
    // static attributes
    //

    static Matrix stiff;
    static Vector resid;
    static Matrix mass;
    static Matrix damping;

    //quadrature data
    static const double sg[2];
    static const double wg[8];
  
    //local nodal coordinates, three coordinates for each of eight nodes
    static double xl[3][8];

    //
    // private methods
    //

    //inertia terms
    void formInertiaTerms(int tangFlag) const;
    //form residual and tangent					  
    void formResidAndTangent(int tang_flag) const;

    //compute coordinate system
    void computeBasis(void) const;

    //compute B matrix
    const Matrix& computeB( int node, const double shp[4][8]) const;
  
    //Matrix transpose
    Matrix transpose( int dim1, int dim2, const Matrix &M );
    static size_t getVectorIndex(const size_t &,const size_t &);
  protected:
    int sendData(CommParameters &cp);
    int recvData(const CommParameters &cp);
  public :
    
    //null constructor
    Brick(void);
    Brick(int tag,const NDMaterial *ptr_mat);
  
    //full constructor
    Brick( int tag, int node1,int node2,int node3,int node4,int node5,int node6,int node7,int node8, NDMaterial &theMaterial, const BodyForces3D &bf= BodyForces3D());
    Element *getCopy(void) const;
    //destructor 
    virtual ~Brick(void);

    //set domain
    void setDomain( Domain *theDomain );

    //return number of dofs
    int getNumDOF(void) const;

    // update
    int update(void);

    //return stiffness matrix 
    const Matrix &getTangentStiff() const;
    const Matrix &getInitialStiff() const;    
    const Matrix &getMass() const;    

    Vector getAvgStress(void) const;
    double getAvgStress(const size_t &,const size_t &) const;
    Vector getAvgStrain(void) const;
    double getAvgStrain(const size_t &,const size_t &) const;

    int addLoad(ElementalLoad *theLoad, double loadFactor);
    int addInertiaLoadToUnbalance(const Vector &accel);

    //get residual
    const Vector &getResistingForce(void) const;
    
    //get residual with inertia terms
    const Vector &getResistingForceIncInertia(void) const;

    // public methods for element output
    virtual int sendSelf(CommParameters &);
    virtual int recvSelf(const CommParameters &);
      
    //print out element data
    void Print( std::ostream &s, int flag );

    Response *setResponse(const std::vector<std::string> &argv, Information &eleInformation);
    int getResponse(int responseID, Information &eleInformation);
  }; 

} // end of XC namespace
