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
//Edge.cc

#include "Edge.h"
#include "Face.h"
#include "Pnt.h"
#include "domain/mesh/node/Node.h"
#include "utility/matrix/util_matrix.h"
#include "xc_basic/src/matrices/m_int.h"
#include "xc_utils/src/geom/d3/BND3d.h"
#include "xc_utils/src/geom/pos_vec/MatrizPos3d.h"
#include "preprocessor/Preprocessor.h"
#include "preprocessor/set_mgmt/Set.h"


#include "boost/any.hpp"
#include "domain/mesh/element/Element.h"

//! @brief Constructor.
XC::Edge::Edge(Preprocessor *m,const size_t &nd)
  : EntMdlr(m), ndiv(nd) {}

//! @brief Constructor.
//! @param nombre: Object identifier.
//! @param m: Pointer to preprocessor.
//! @param nd: Number of divisions.
XC::Edge::Edge(const std::string &nombre,Preprocessor *m,const size_t &nd)
  : EntMdlr(nombre,0,m), ndiv(nd) {}

//! @brief Insert a surface in contact with the line (neighbour).
void XC::Edge::inserta_surf(Face *s)
  { sups_linea.insert(s); }

//! @brief Update topology.
void XC::Edge::actualiza_topologia(void)
  {
    if(P1()) P1()->inserta_linea(this);
    if(P2()) P2()->inserta_linea(this);
  }

//! @brief Return a pointer to the edge's start point.
XC::Pnt *XC::Edge::P1(void)
  {
    std::cerr << "Edge::P1; this function must be redefined on"
              << " derived classes, nullptr returned;" << std::endl;
    return nullptr;
  }

//! @brief Return a constant pointer to the edge's start point.
const XC::Pnt *XC::Edge::P1(void) const
  {
    std::cerr << "Edge::P1; this function must be redefined on"
              << " derived classes, nullptr returned;" << std::endl;
    return nullptr;
  }

//! @brief Return a pointer to the edge's start point.
XC::Pnt *XC::Edge::P2(void)
  {
    std::cerr << "Edge::P2; this function must be redefined on"
              << " derived classes, nullptr returned;" << std::endl;
    return nullptr;
  }

//! @brief Return a constant pointer to the edge's end point.
const XC::Pnt *XC::Edge::P2(void) const
  {
    std::cerr << "Edge::P2; this function must be redefined on"
              << " derived classes, nullptr returned;" << std::endl;
    return nullptr;
  }

//! @brief Returns true if the points passed as parameters
//! are the ends of the edge.
bool XC::Edge::ExtremosEn(const Pnt *p1,const Pnt *p2) const
  {
    bool retval= false;
    const Pnt *e1= P1();
    const Pnt *e2= P2();
    if(p1==e1)
      retval= (p2==e2);
    else if(p1==e2)
      retval= (p2==e1);
    return retval;
  }

//! @brief Returns true if the line lies inside the
//! geometric object.
bool XC::Edge::In(const GeomObj3d &geomObj, const double &tol) const
  {
    bool retval= false;
    const Pnt *p1= P1();
    const Pnt *p2= P2();
    if(p1)
      retval= p1->In(geomObj,tol);
    else
      std::cerr << nombre_clase() << "::" << __FUNCTION__
	        << "; p1 not defined." << std::endl;
    if(p2)
      retval= retval && p2->In(geomObj,tol);
    else
      std::cerr << nombre_clase() << "::" << __FUNCTION__
	        << "; p2 not defined." << std::endl;
    return retval;
  }

//! @brief Returns true if the line lies outside the
//! geometric object.
bool XC::Edge::Out(const GeomObj3d &geomObj, const double &tol) const
  {
    bool retval= false;
    const Pnt *p1= P1();
    const Pnt *p2= P2();
    if(p1)
      retval= p1->Out(geomObj,tol);
    else
      std::cerr << nombre_clase() << "::" << __FUNCTION__
	        << "; p1 not defined." << std::endl;
    if(p2)
      retval= retval && p2->Out(geomObj,tol);
    else
      std::cerr << nombre_clase() << "::" << __FUNCTION__
	        << "; p2 not defined." << std::endl;
    return retval;
  }

//! @brief Assigns the number of of divisions.
void XC::Edge::SetNDiv(const size_t &nd)
  {
    if(ndiv!=nd) //If number of divisions changes
      {
        if(ttzNodes.empty()) //Not meshed.
          {
            const size_t ns= sups_linea.size();
            if(ns>1)
              {
// 	        std::clog << "Edge::SetNDiv; " << getName()
//                           << " is an edge of the surfaces: "
//                           << NombresSupsTocan()
//                           << ". Number of divisions"
//                           << " was " << ndiv
//                           << " we adopt: " << nd << std::endl;
                ndiv= std::max(ndiv,nd);
              }
            else
              ndiv= nd;
          }
        else
          std::cerr << "Edge::SetNDiv; " << getName()
                    << " edge is already meshed and keeps its number of divisions"
                    << " ndiv= " << ndiv << ".\n";
      }
  }

//! @brief Compute the number of divisions necessary to 
//! get the element size passed as parameter.
void XC::Edge::SetElemSize(const double &sz)
  {
    const double l= getLongitud();
    const size_t n= ceil(l/sz);
    SetNDiv(n);
  }

//! @brief Create points along the line.
void XC::Edge::divide(void)
  {
    const MatrizPos3d posiciones= get_posiciones();
    create_points(posiciones);
  }

//! @brief Return a pointer to node whose indices are passed as parameters.
XC::Node *XC::Edge::GetNodo(const size_t &i,const size_t &j,const size_t &k)
  { return EntMdlr::GetNodo(i,j,k); }

//! @brief Return a pointer to node whose indices are passed as parameters.
const XC::Node *XC::Edge::GetNodo(const size_t &i,const size_t &j,const size_t &k) const
  { return EntMdlr::GetNodo(i,j,k); }

//! @brief Return a pointer to node whose index is passed as parameter.
XC::Node *XC::Edge::GetNodo(const size_t &i)
  {  return const_cast<Node *>(static_cast<const Edge &>(*this).GetNodo(i)); }

//! @brief Return a pointer to node whose index is passed as parameter.
const XC::Node *XC::Edge::GetNodo(const size_t &i) const
  { return ttzNodes.getAtI(i); }

//! @brief Returns the node whose ordinal index is passed as parameter, starting from the beginning.
XC::Node *XC::Edge::GetNodoDir(const size_t &i)
  { return GetNodo(i); }

//! @brief Return the node whose ordinal index is passed as parameter, starting from the beginning.
const XC::Node *XC::Edge::GetNodoDir(const size_t &i) const
  { return GetNodo(i); }

//! @brief Return the node whose ordinal index is passed as parameter, starting from the end.
XC::Node *XC::Edge::GetNodoInv(const size_t &i)
  { return GetNodo(getNumberOfNodes()-i+1); }

//! @brief Return the node whose ordinal index is passed as parameter, starting from the end.
const XC::Node *XC::Edge::GetNodoInv(const size_t &i) const
  { return GetNodo(getNumberOfNodes()-i+1); }

//! @brief Return the first node of the line.
const XC::Node *XC::Edge::GetPrimerNodo(void) const
  { 
    const Node *retval= GetNodo(1);
    if(!retval)
      {
        const Pnt *p1= P1();
        if(p1)
          retval= p1->GetNodo();
      }
    return retval;
  }

//! @brief Return the first node of the line.
XC::Node *XC::Edge::GetPrimerNodo(void)
  { 
    Node *retval= GetNodo(1);
    if(!retval)
      {
        Pnt *p1= P1();
        if(p1)
          retval= p1->GetNodo();
      }
    return retval;
  }

//! @brief Return the last node of the line.
const XC::Node *XC::Edge::GetUltimoNodo(void) const
  { 
    const Node *retval= GetNodoInv(1);
    if(!retval)
      {
        const Pnt *p2= P2();
        if(p2)
          retval= p2->GetNodo();
      }
    return retval;
  }

//! @brief Return the last node of the line.
XC::Node *XC::Edge::GetUltimoNodo(void)
  { 
    Node *retval= GetNodoInv(1);
    if(!retval)
      {
        Pnt *p2= P2();
        if(p2)
          retval= p2->GetNodo();
      }
    return retval;
  }

//! @brief Return the IDs of the nodes in forward order.
std::vector<int> XC::Edge::GetTagsNodosDir(void) const
  {
    const size_t nn= getNumberOfNodes();
    std::vector<int> retval(nn);
    for(size_t i=1;i<=nn;i++)
      retval[i-1]= GetNodo(i)->getTag();
    return retval;
  }

//! @brief Return the IDs of the nodes in reverse order.
std::vector<int> XC::Edge::GetTagsNodosInv(void) const
  {
    const size_t nn= getNumberOfNodes();
    std::vector<int> retval(nn);
    for(size_t i=1;i<=nn;i++)
      retval[i-1]= GetNodo(nn-i+1)->getTag();
    return retval;
  }

//! @brief Return the positions of the nodes in forward order.
MatrizPos3d XC::Edge::GetPosNodosDir(void) const
  {
    const size_t nn= getNumberOfNodes();
    MatrizPos3d retval(nn);
    for(size_t i=1;i<=nn;i++)
      retval(i,1)= pos_node(*GetNodo(i));
    return retval;
  }

//! @brief Return the positions of the nodes in reverse order.
MatrizPos3d XC::Edge::GetPosNodosInv(void) const
  {
    const size_t nn= getNumberOfNodes();
    MatrizPos3d retval(nn);
    for(size_t i=1;i<=nn;i++)
      retval(i,1)= pos_node(*GetNodo(nn-i+1));
    return retval;
  }

//! @brief Return the surface names that touch the line (neighbors).
const std::string &XC::Edge::NombresSupsTocan(void) const
  {
    static std::string retval;
    retval= "";
    if(!sups_linea.empty())
      {
        std::set<const Face *>::const_iterator i= sups_linea.begin();
        retval+= (*i)->getName();
        i++;
        for(;i!=sups_linea.end();i++)
          retval+= "," + (*i)->getName();
      }
    return retval;
  }

//! @brief Return the homologous sides to that passed as a parameter.
std::set<const XC::Edge *> XC::Edge::GetLadosHomologos(const std::set<const XC::Edge *> &lh) const
  {
    std::set<const Edge *> retval;
    std::set<const Edge *> new_adyacentes;

    if(!sups_linea.empty())
      {
        for(std::set<const Face *>::const_iterator i= sups_linea.begin();i!=sups_linea.end();i++)
          {
            const Edge *h= (*i)->get_lado_homologo(this);
            if(h!=this)
              {
                std::set<const XC::Edge *>::const_iterator k= lh.find(h);
                if(k==lh.end()) //Not already added
                  new_adyacentes.insert(h);
              }
          }
      }
    for(std::set<const XC::Edge *>::const_iterator i= new_adyacentes.begin();i!=new_adyacentes.end();i++)
      retval.insert(*i);
    if(retval.size()>lh.size()) //There are new edges.
      {
        for(std::set<const XC::Edge *>::const_iterator i= new_adyacentes.begin();i!=new_adyacentes.end();i++)
          {
            std::set<const XC::Edge *> tmp= (*i)->GetLadosHomologos(retval);
            for(std::set<const XC::Edge *>::const_iterator j= tmp.begin();j!=tmp.end();j++)
              if(this!=*j) retval.insert(*j);
          }
        new_adyacentes.erase(new_adyacentes.begin(),new_adyacentes.end());
      }
    return retval;
  }

//! @brief Compute the number of divisions for each line
//! to make it compatible with adjacent surface meshing.
size_t XC::calcula_ndiv_lados(const std::set<const XC::Edge *> &lados)
  {
    size_t nd= 0;
    for(std::set<const XC::Edge *>::const_iterator i= lados.begin();i!=lados.end();i++)
      nd= std::max(nd,(*i)->NDiv());
    return nd;
  }

//! @brief Return true if the line touches the surface (neighbor).
bool XC::Edge::Toca(const Face &s) const
  {
    std::set<const Face *>::const_iterator i= sups_linea.find(&s);
    return (i!=sups_linea.end());
  }

//! @brief Return true if the line touches the body.
bool XC::Edge::Toca(const Body &b) const
  {
    for(std::set<const Face *>::const_iterator i= sups_linea.begin(); i!=sups_linea.end();i++)
      { if((*i)->Toca(b)) return true; }
    return false;
  }

//! @brief Return true if it is an end point of the line.
bool XC::Edge::Extremo(const Pnt &p) const
  { return ((&p == P1()) || (&p == P2()));  }

//! @brief Return the list of edges that have this point as starting or ending point.
std::set<const XC::Edge *> XC::GetLineasTocan(const Pnt &p)
  { return p.EdgesTocan(); }

//! @brief Return a matrix of positions along the line.
MatrizPos3d XC::Edge::get_pos_nodes(void) const
  { return get_posiciones(); }

//! @brief Create the nodes for both end points of the edge.
void XC::Edge::create_nodes_en_extremos(void)
  {
    if(verbosity>4)
      std::clog << "Creating nodes for '" << getName() << "' edge ends...";   
    if(!P1())
      {
	std::cerr << nombre_clase() << "::" << __FUNCTION__
	          << "; start point undefined." << std::endl;
        return;
      }
    else
      P1()->create_nodes();

    Node *node_p1= P1()->GetNodo(1,1,1);
    assert(node_p1);
    ttzNodes(1,1,1)= node_p1; //Nodo del start point.
      
    if(!P2())
      {
	std::cerr << nombre_clase() << "::" << __FUNCTION__
	          << "; end point undefined." << std::endl;
        return;
      }
    else
      P2()->create_nodes();

    Node *node_p2= P2()->GetNodo(1,1,1);
    assert(node_p2);
    const size_t filas= ttzNodes.getNumFilas();
    const size_t cols= ttzNodes.getNumCols();
    ttzNodes(1,filas,cols)= node_p2; //Node of end point.

    if(verbosity>4)
      std::cerr << nombre_clase() << "::" << __FUNCTION__
	        << "; creados." << std::endl;
  }

//! @brief Create nodes on objects.
void XC::Edge::create_nodes(void)
  {
    if(verbosity>4)
      std::clog << "Creating nodes for edge: '" << getName() << "'...";

 
    if(ttzNodes.Null())
      {
        if(!getPreprocessor())
          std::cerr << nombre_clase() << "::" << __FUNCTION__
	            << "; preprocessor undefined." << std::endl;
        else
          {
            const MatrizPos3d posiciones= get_pos_nodes();
            const size_t filas= posiciones.getNumFilas();
            const size_t cols= posiciones.getNumCols();
            ttzNodes= TritrizPtrNod(1,filas,cols);

            create_nodes_en_extremos();


            if((filas*cols)>2) //If it has intermediate nodes...
              {
                const size_t fila_fin= std::max(filas-1,size_t(1));
                const size_t fila_ini= (fila_fin == 1 ? 1 : 2);
                const size_t col_fin= std::max(cols-1,size_t(1));
                const size_t col_ini= (col_fin == 1 ? 1 : 2);
                for(register size_t j= fila_ini;j<=fila_fin;j++)
                  for(register size_t k= col_ini;k<=col_fin;k++)
                    create_node(posiciones(j,k),1,j,k);
              }
          }
        if(verbosity>4)
	  std::clog << nombre_clase() << "::" << __FUNCTION__
	            << "; created " << ttzNodes.NumPtrs()
		    << " node(s)." << std::endl;
      }
    else
      {
        if(verbosity>2)
          std::clog << nombre_clase() << "::" << __FUNCTION__
	            << "; nodes of the line: '" << getName() << "' already exist." << std::endl;
      }
    if(verbosity>4)
      std::clog << "created." << std::endl;
    const size_t numNodes= ttzNodes.NumPtrs();
    if(numNodes==0 && verbosity>0)
      std::clog << nombre_clase() << "::" << __FUNCTION__
	        << "; warning 0 nodes created for line: " << getName()
	        << std::endl;
  }

//! @brief Trigger mesh generation.
void XC::Edge::genMesh(meshing_dir dm)
  {
    if(verbosity>3)
      std::clog << "Meshing edge...(" << getName() << ")...";   
    create_nodes();
    create_elements(dm);
    if(verbosity>3)
      std::clog << "done." << std::endl;
  }

//! @brief Return a vector tangent to the line in point at parameter s.
const XC::Vector &XC::Edge::getTang(const double &s) const
  {
    static XC::Vector retval(1);
    std::cerr << "Edge::getTang; not implemented." << std::endl;
    return retval;
  }

//! @brief Return the sets to wich this edge belongs.
std::set<XC::SetBase *> XC::Edge::get_sets(void) const
  {
    std::set<SetBase *> retval;
    const Preprocessor *preprocessor= getPreprocessor();
    if(preprocessor)
      {
        MapSet &sets= const_cast<MapSet &>(preprocessor->get_sets());
        retval= sets.get_sets(this);
      }
    else
      std::cerr << nombre_clase() << __FUNCTION__
	        << "; preprocessor needed." << std::endl;
    return retval;
  }

//! @brief Add the «edge» to the sets passed as parameters.
void XC::Edge::add_to_sets(std::set<SetBase *> &sets)
  {
    for(std::set<SetBase *>::iterator i= sets.begin();i!= sets.end();i++)
      {
        Set *s= dynamic_cast<Set *>(*i);
        if(s) s->getLines().push_back(this);
      }
  }

//! Return indices of the vertices.
std::vector<int> XC::Edge::getIndicesVertices(void) const
  {
    const size_t nv= NumVertices();
    std::vector<int> retval(nv);
    if(nv>=1)
      {
        for(size_t i=0;i<nv;i++)
          retval[i]= GetVertice(i+1)->getIdx();
      }
    return retval;
  }

//! @brief Return k-points.
XC::ID XC::Edge::getKPoints(void) const
  {
    ID retval(2);
    retval[0]= P1()->GetTag();
    retval[1]= P2()->GetTag();
    return retval;
  }



