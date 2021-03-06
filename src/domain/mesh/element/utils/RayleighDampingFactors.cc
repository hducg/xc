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
//RayleighDampingFactors.cpp

#include "RayleighDampingFactors.h"

#include "utility/matrix/Vector.h"
#include <domain/mesh/element/utils/Information.h>

//! @brief constructor
XC::RayleighDampingFactors::RayleighDampingFactors(void)
  :EntCmd(), MovableObject(0), alphaM(0.0), betaK(0.0), betaK0(0.0), betaKc(0.0) {}

//! @brief constructor
XC::RayleighDampingFactors::RayleighDampingFactors(const double &aM,const double &bK,const double &bK0,const double &bKc)
  :EntCmd(), MovableObject(0), alphaM(aM), betaK(bK), betaK0(bK0), betaKc(bKc) {}

//! @brief constructor
XC::RayleighDampingFactors::RayleighDampingFactors(const Vector &v)
  : EntCmd(), MovableObject(0), alphaM(v[0]), betaK(v[1]), betaK0(v[2]), betaKc(v[3]) {}

void XC::RayleighDampingFactors::Print(std::ostream &s, int flag) const
  {
    s << "rayleigh damping factors: alphaM: " << alphaM << " betaK: ";
    s << betaK << " betaK0: " << betaK0 << std::endl;
  }


int XC::RayleighDampingFactors::updateParameter(int parameterID, Information &info)
  {
    switch (parameterID)
      {
      case 1:
        alphaM= info.theDouble;
        return 0;
      case 2:
        betaK = info.theDouble;
        return 0;
      default:
        return 0;
      }
  }

//! @brief Send object members through the channel being passed as parameter.
int XC::RayleighDampingFactors::sendData(CommParameters &cp)
  {
    int res=cp.sendDoubles(alphaM,betaK,betaK0,betaKc,getDbTagData(),CommMetaData(1));
    return res;
  }

//! @brief Receives object members through the channel being passed as parameter.
int XC::RayleighDampingFactors::recvData(const CommParameters &cp)
  {
    int res= cp.receiveDoubles(alphaM,betaK,betaK0,betaKc,getDbTagData(),CommMetaData(1));
    return res;
  }

//! @brief Sends object through the channel being passed as parameter.
int XC::RayleighDampingFactors::sendSelf(CommParameters &cp)
  {
    setDbTag(cp);
    const int dataTag= getDbTag();
    inicComm(2);
    int res= sendData(cp);

    res+= cp.sendIdData(getDbTagData(),dataTag);
    if(res < 0)
      std::cerr << nombre_clase() << "sendSelf() - failed to send data\n";
    return res;
  }

//! @brief Receives object through the channel being passed as parameter.
int XC::RayleighDampingFactors::recvSelf(const CommParameters &cp)
  {
    inicComm(2);
    const int dataTag= getDbTag();
    int res= cp.receiveIdData(getDbTagData(),dataTag);

    if(res<0)
      std::cerr << nombre_clase() << "::recvSelf - failed to receive ids.\n";
    else
      {
        //setTag(getDbTagDataPos(0));
        res+= recvData(cp);
        if(res<0)
          std::cerr << nombre_clase() << "::recvSelf - failed to receive data.\n";
      }
    return res;
  }

std::ostream &XC::operator<<(std::ostream &os,const XC::RayleighDampingFactors &rF)
  {
    rF.Print(os);
    return os;
  }
