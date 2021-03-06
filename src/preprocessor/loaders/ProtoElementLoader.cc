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
//ProtoElementLoader.cc

#include "ProtoElementLoader.h"
#include "create_elem.h"

#include "domain/mesh/element/truss_beam_column/truss/CorotTruss.h"
#include "domain/mesh/element/truss_beam_column/truss/CorotTrussSection.h"
#include "domain/mesh/element/truss_beam_column/truss/Truss.h"
#include "domain/mesh/element/truss_beam_column/truss/TrussSection.h"
#include "domain/mesh/element/truss_beam_column/truss/Spring.h"

#include "domain/mesh/element/truss_beam_column/beam2d/beam2d02.h"
#include "domain/mesh/element/truss_beam_column/beam2d/beam2d03.h"
#include "domain/mesh/element/truss_beam_column/beam2d/beam2d04.h"
#include "domain/mesh/element/truss_beam_column/beam3d/beam3d01.h"
#include "domain/mesh/element/truss_beam_column/beam3d/beam3d02.h"
#include "domain/mesh/element/truss_beam_column/beamWithHinges/BeamWithHinges2d.h"
#include "domain/mesh/element/truss_beam_column/beamWithHinges/BeamWithHinges3d.h"
#include "domain/mesh/element/truss_beam_column/elasticBeamColumn/ElasticBeam2d.h"
#include "domain/mesh/element/truss_beam_column/elasticBeamColumn/ElasticBeam3d.h"
#include "domain/mesh/element/truss_beam_column/forceBeamColumn/ForceBeamColumn2d.h"
#include "domain/mesh/element/truss_beam_column/forceBeamColumn/ForceBeamColumn3d.h"
#include "domain/mesh/element/truss_beam_column/dispBeamColumn/DispBeamColumn2d.h"
#include "domain/mesh/element/truss_beam_column/dispBeamColumn/DispBeamColumn3d.h"
#include "domain/mesh/element/truss_beam_column/nonlinearBeamColumn/element/NLBeamColumn2d.h"
#include "domain/mesh/element/truss_beam_column/nonlinearBeamColumn/element/NLBeamColumn3d.h"
#include "domain/mesh/element/truss_beam_column/updatedLagrangianBeamColumn/UpdatedLagrangianBeam2D.h"

#include "domain/mesh/element/plane/fourNodeQuad/ConstantPressureVolumeQuad.h"
#include "domain/mesh/element/plane/fourNodeQuad/EnhancedQuad.h"
#include "domain/mesh/element/plane/fourNodeQuad/FourNodeQuad.h"
#include "domain/mesh/element/plane/triangle/Tri31.h"
#include "domain/mesh/element/plane/fourNodeQuad/NineNodeMixedQuad.h"
#include "domain/mesh/element/plane/UP-ucsd/FourNodeQuadUP.h"
#include "domain/mesh/element/plane/UP-ucsd/NineFourNodeQuadUP.h"

#include "domain/mesh/element/volumen/brick/BbarBrick.h"
#include "domain/mesh/element/volumen/brick/Brick.h"
#include "domain/mesh/element/volumen/8nbrick/EightNodeBrick.h"
#include "domain/mesh/element/volumen/20nbrick/TwentyNodeBrick.h"
#include "domain/mesh/element/volumen/20nbrick/Twenty_Node_Brick.h"
#include "domain/mesh/element/volumen/27nbrick/TwentySevenNodeBrick.h"
#include "domain/mesh/element/volumen/TotalLagrangianFD20NodeBrick/TotalLagrangianFD20NodeBrick.h"
#include "domain/mesh/element/volumen/upU/EightNodeBrick_u_p_U.h"
#include "domain/mesh/element/volumen/upU/TwentyNodeBrick_u_p_U.h"
#include "domain/mesh/element/volumen/UP-ucsd/BrickUP.h"
#include "domain/mesh/element/volumen/UP-ucsd/TwentyEightNodeBrickUP.h"

#include "domain/mesh/element/special/joint/BeamColumnJoint2d.h"
#include "domain/mesh/element/special/joint/BeamColumnJoint3d.h"
#include "domain/mesh/element/special/joint/Joint2D.h"
#include "domain/mesh/element/special/joint/Joint3D.h"

#include "domain/mesh/element/plane/shell/ShellMITC4.h"
#include "domain/mesh/element/plane/shell/CorotShellMITC4.h"
#include "domain/mesh/element/plane/shell/ShellNL.h"

#include "domain/mesh/element/zeroLength/ZeroLength.h"
#include "domain/mesh/element/zeroLength/ZeroLengthSection.h"
#include "domain/mesh/element/zeroLength/ZeroLengthContact2D.h"
#include "domain/mesh/element/zeroLength/ZeroLengthContact3D.h"

#include "preprocessor/Preprocessor.h"


//! @brief Default constructor.
XC::ProtoElementLoader::ProtoElementLoader(Preprocessor *preprocessor)
  : Loader(preprocessor), nmb_mat("nil"), num_sec(3), dim_elem(0), nmb_transf("nil"), nmb_integ("Lobatto"), dir(0)
 {}

//! @brief Returns a reference to the material handler.
const XC::MaterialLoader &XC::ProtoElementLoader::get_material_loader(void) const
  { return getPreprocessor()->getMaterialLoader(); }

//! @brief Returns an iterator al material que se especifica en nmb_mat.
XC::MaterialLoader::const_iterator XC::ProtoElementLoader::get_iter_material(void) const
  { return getPreprocessor()->getMaterialLoader().find(nmb_mat); }

//! @brief Returns a pointer to material que se especifica en nmb_mat.
const XC::Material *XC::ProtoElementLoader::get_ptr_material(void) const
  {
    Material *retval= nullptr;
    MaterialLoader::const_iterator imat= get_iter_material();
    if(imat!= get_material_loader().end())
      retval= imat->second;
    else 
      std::cerr << "ProtoElementLoader - material: '" 
                << nmb_mat << "' not found.\n";
    return retval;
  }

//! @brief Returns a reference to de integrator handler.
const XC::BeamIntegratorLoader &XC::ProtoElementLoader::get_beam_integrator_loader(void) const
  { return getPreprocessor()->getBeamIntegratorLoader(); }

//! @brief Returns an iterator al integrator que se especifica en nmb_integ.
XC::BeamIntegratorLoader::const_iterator XC::ProtoElementLoader::get_iter_beam_integrator(void) const
  { return getPreprocessor()->getBeamIntegratorLoader().find(nmb_integ); }


//! @brief Returns a pointer to integrator que se especifica en nmb_integ.
const XC::BeamIntegration *XC::ProtoElementLoader::get_ptr_beam_integrator(void) const
  {
    BeamIntegration *retval= nullptr;
    BeamIntegratorLoader::const_iterator iInteg= get_iter_beam_integrator();
    if(iInteg!= get_beam_integrator_loader().end())
      retval= iInteg->second;
    else
      if(verbosity>0)
        std::cerr << nombre_clase() << "::" << __FUNCTION__
	          << "; integrator named: '" 
                  << nmb_integ << "' not found.\n";
    return retval;
  }

//! @brief Returns a reference to the coordinate transformation loader.
const XC::TransfCooLoader &XC::ProtoElementLoader::get_transf_coo_loader(void) const
  { return getPreprocessor()->getTransfCooLoader(); }

//! @brief Returns an iterator to the coordinate transformation with the name being passed as parameter.
XC::TransfCooLoader::const_iterator XC::ProtoElementLoader::get_iter_transf_coo(void) const
  { return getPreprocessor()->getTransfCooLoader().find(nmb_transf); }

//! @brief Returns a pointer to the coordinate transformation with the name being passed as parameter (nullptr if not found).
const XC::CrdTransf *XC::ProtoElementLoader::get_ptr_transf_coo(void) const
  {
    CrdTransf *retval= nullptr;
    TransfCooLoader::const_iterator itrf= get_iter_transf_coo();
    if(itrf!= this->get_transf_coo_loader().end())
      retval= itrf->second;
    else
      if(verbosity>0)
        std::cerr << nombre_clase() << "::" << __FUNCTION__
	          << "; coordinate transformation named: '" 
                  << nmb_transf << "' not found.\n";
    return retval;
  }

//! @brief Process the comands used to define
//! the elements of the finite element model. It interprets
//! the following commands (if the identifier (tag) is not
//! specified a default value will be assigned):
//!
//! - truss[tag]: Defines a truss element (Truss). 
//! - truss_section[tag]: Defines a truss element with section type material.
//! - corot_truss[tag]: Defines a truss element with corotational formulation. 
//! - corot_truss_section[tag]: Defines a truss element with corotational formulation and section type material.
//! - beam2d_02[tag]: Defines a beam-column element (beam2d02) for plane problems. 
//! - beam2d_03[tag]: Defines a beam-column element (beam2d03) for plane problems. 
//! - beam2d_04[tag]: Defines a beam-column element (beam2d04) for plane problems.
//! - beam3d_01[tag]: Defines a beam-column element (beam3d01) for 3D problems.
//! - beam3d_02[tag]: Defines a beam-column element (beam2d02) for 3D problems.
//! - elastic_beam2d[tag]: Defines a beam-column element (ElasticBeam2d) for plane problems.
//! - elastic_beam3d[tag]: Defines a beam-column element (ElasticBeam3d) for 3D problems.
//! - force_beam_column_2d[tag]: Defines a beam-column element (ForceBeamColumn2d) no lineal,
//!   for plane problems.
//! - force_beam_column_3d[tag]: Defines a beam-column element (ForceBeamColumn3d) no lineal,
//!   for 3D problems.
//! - shell_mitc4[tag]: Defines a shell element (ShellMITC4),
//! - shell_nl[tag]: Defines a shell element (ShellNL),
//!   for shell problems.
//! - quad4n[tag]: Defines a four node quad (FourNodeQuad),
//! - tri31[tag]: Defines a three node triangle with just a Gauss point (Tri31),
//!   for plane problems.
//! - brick[tag]: Defines an eight node hexahedron (Brick),
//!   para solid analysis.
//! - zero_length[tag]: Defines a zero length element (ZeroLength).
//! - zero_length_section[tag]: Defines a zero length element with section type material (ZeroLengthSection).
XC::Element *XC::ProtoElementLoader::create_element(const std::string &cmd,int tag_elem)
  {
    Element *retval= nullptr;
    if(cmd == "truss")
      retval= new_element_dim_gen_mat<Truss>(tag_elem, dim_elem, get_ptr_material());
    else if(cmd == "truss_section")
      retval= new_element_dim_gen_mat<TrussSection>(tag_elem, dim_elem, get_ptr_material());
    else if(cmd == "corot_truss")
      retval= new_element_dim_gen_mat<CorotTruss>(tag_elem, dim_elem, get_ptr_material());
    else if(cmd == "corot_truss_section")
      retval= new_element_dim_gen_mat<CorotTrussSection>(tag_elem, dim_elem, get_ptr_material());
    else if(cmd == "muelle")
      {
        std::cerr << "ProtoElementLoader::create_element; 'muelle' is DEPRECATED use 'spring'" << std::endl;
        retval= new_element_dim_gen_mat<Spring>(tag_elem, dim_elem, get_ptr_material());
      }
    else if(cmd == "spring")
      retval= new_element_dim_gen_mat<Spring>(tag_elem, dim_elem, get_ptr_material());
    else if(cmd == "beam2d_02")
      retval= new_element<beam2d02>(tag_elem);
    else if(cmd == "beam2d_03")
      retval= new_element<beam2d03>(tag_elem);
    else if(cmd == "beam2d_04")
      retval= new_element<beam2d04>(tag_elem);
    else if(cmd == "beam3d_01")
      retval= new_element<beam3d01>(tag_elem);
    else if(cmd == "beam3d_02")
      retval= new_element<beam3d02>(tag_elem);
    else if(cmd == "elastic_beam_2d")
      retval= new_element_mat_crd<ElasticBeam2d>(tag_elem, get_ptr_material(), get_ptr_transf_coo());
    else if(cmd == "elastic_beam_3d")
      retval= new_element_mat_crd<ElasticBeam3d>(tag_elem, get_ptr_material(), get_ptr_transf_coo());
    else if(cmd == "beam_with_hinges_2d")
      retval= new_element_gen_mat_crd<BeamWithHinges2d>(tag_elem, get_ptr_material(), get_ptr_transf_coo());
    else if(cmd == "beam_with_hinges_3d")
      retval= new_element_gen_mat_crd<BeamWithHinges3d>(tag_elem, get_ptr_material(), get_ptr_transf_coo());
    else if(cmd == "disp_beam_column_2d")
      retval= new_element_dim_gen_mat_crd<DispBeamColumn2d>(tag_elem, dim_elem, get_ptr_material(), get_ptr_transf_coo());
    else if(cmd == "disp_beam_column_3d")
      retval= new_element_dim_gen_mat_crd<DispBeamColumn3d>(tag_elem, dim_elem, get_ptr_material(), get_ptr_transf_coo());
    else if(cmd == "nl_beam_column_2d")
      retval= new_element_ns_gen_mat_crd<NLBeamColumn2d>(tag_elem, get_ptr_material(), num_sec, get_ptr_transf_coo());
    else if(cmd == "nl_beam_column_3d")
      retval= new_element_ns_gen_mat_crd<NLBeamColumn3d>(tag_elem, get_ptr_material(), num_sec, get_ptr_transf_coo());
    else if(cmd == "force_beam_column_2d")
      retval= new_element_ns_gen_mat_crd_integ<ForceBeamColumn2d>(tag_elem, get_ptr_material(), num_sec, get_ptr_transf_coo(),get_ptr_beam_integrator());
    else if(cmd == "force_beam_column_3d")
      retval= new_element_ns_gen_mat_crd_integ<ForceBeamColumn3d>(tag_elem, get_ptr_material(), num_sec, get_ptr_transf_coo(),get_ptr_beam_integrator());
    else if(cmd == "zero_length")
      retval= new_element_dim_gen_mat_dir<ZeroLength>(tag_elem, dim_elem, get_ptr_material(),dir);
    else if(cmd == "zero_length_contact_2d")
      retval= new_element<ZeroLengthContact2D>(tag_elem);
    else if(cmd == "zero_length_contact_3d")
      retval= new_element<ZeroLengthContact3D>(tag_elem);
    else if(cmd == "zero_length_section")
      retval= new_element_dim_gen_mat<ZeroLengthSection>(tag_elem, dim_elem, get_ptr_material());
    else if(cmd == "shell_mitc4")
      {
        retval= new_element_mat<ShellMITC4,SectionForceDeformation>(tag_elem, get_ptr_material());
        if(!retval)
          std::cerr << "Error in " << nombre_clase() << "::" << __FUNCTION__ << "; material: '"
                    << nmb_mat << "' has not a suitable type." << std::endl;
      }
    else if(cmd == "corot_shell_mitc4")
      {
        retval= new_element_mat<CorotShellMITC4,SectionForceDeformation>(tag_elem, get_ptr_material());
        if(!retval)
          std::cerr << "Error in " << nombre_clase() << "::" << __FUNCTION__
		    << "; material: '" << nmb_mat << "' is not suitable for "
		    << cmd << " elements." << std::endl;
      }
    else if(cmd == "shell_nl")
      {
        retval= new_element_mat<ShellNL,SectionForceDeformation>(tag_elem, get_ptr_material());
        if(!retval)
          std::cerr << "Error in " << nombre_clase() << "::" << __FUNCTION__
		    << "; material: '" << nmb_mat << "' is not suitable for "
		    << cmd << " elements." << std::endl;
      }
    else if(cmd == "quad4n")
      {
        retval= new_element_mat<FourNodeQuad,NDMaterial>(tag_elem, get_ptr_material());
        if(!retval)
          std::cerr << "Error in " << nombre_clase() << "::" << __FUNCTION__
		    << "; material: '" << nmb_mat << "' is not suitable for "
		    << cmd << " elements." << std::endl;
      }
    else if(cmd == "tri31")
      {
        retval= new_element_mat<Tri31,NDMaterial>(tag_elem, get_ptr_material());
        if(!retval)
          std::cerr << "Error in " << nombre_clase() << "::" << __FUNCTION__
		    << "; material: '" << nmb_mat << "' is not suitable for "
		    << cmd << " elements." << std::endl;
      }
    else if(cmd == "brick")
      {
        retval= new_element_mat<Brick,NDMaterial>(tag_elem, get_ptr_material());
        if(!retval)
          std::cerr << "Error in " << nombre_clase() << "::" << __FUNCTION__
		    << "; material: '" << nmb_mat << "' is not suitable for "
		    << cmd << " elements." << std::endl;
      }
    else
      std::cerr << "Element type: " << cmd << " unknown." << std::endl;
    return retval;
  }

//! @brief Create a new element.
//! @param tipo: type of element. Available types:'truss','truss_section','corot_truss','corot_truss_section','muelle', 'spring', 'beam2d_02', 'beam2d_03',  'beam2d_04', 'beam3d_01', 'beam3d_02', 'elastic_beam2d', 'elastic_beam3d', 'beam_with_hinges_2d', 'beam_with_hinges_3d', 'nl_beam_column_2d', 'nl_beam_column_3d','force_beam_column_2d', 'force_beam_column_3d', 'shell_mitc4', ' shell_nl', 'quad4n', 'tri31', 'brick', 'zero_length', 'zero_length_contact_2d', 'zero_length_contact_3d', 'zero_length_section'.
//! @param iNodos: nodes ID, e.g. xc.ID([1,2]) to create a linear element from node 1 to node 2.

XC::Element *XC::ProtoElementLoader::newElement(const std::string &tipo,const ID &iNodos)
  {
    const int tag_elem= getDefaultTag();
    Element *retval= getPreprocessor()->getDomain()->getElement(tag_elem);
    if(!retval) //It doesn't already exists.
      {
        retval= create_element(tipo,tag_elem);
        if(retval)
          {
            retval->setIdNodos(iNodos);
            add(retval);
          }
      }
    else
      std::cerr << nombre_clase() << "::" << __FUNCTION__
	        << "; ERROR the element: "
                << tag_elem << " already exists.\n";
    return retval;
  }

//! @brief Sets the default material name for new elements.
void XC::ProtoElementLoader::setDefaultMaterial(const std::string &nmb)
  { nmb_mat= nmb; }

//! @brief Returns the default material name for new elements.
const std::string &XC::ProtoElementLoader::getDefaultMaterial(void) const
  { return nmb_mat; }

//! @brief Default number of sections for new elements.
void XC::ProtoElementLoader::setNumSections(const int &ns)
  { num_sec= ns; }

//! @brief Returns the default number of sections for new elements.
int XC::ProtoElementLoader::getNumSections(void) const
  { return num_sec; }

//! @brief Sets the default dimension (0D,1D,2D or 3D) for new elements.
void XC::ProtoElementLoader::setDimElem(const int &dim)
  { dim_elem= dim; }

//! @brief Returns the default dimension (0D,1D,2D or 3D) for new elements.
int XC::ProtoElementLoader::getDimElem(void) const
  { return dim_elem; }

//! @brief Sets the name of the default coordinate transformation for new elements.
void XC::ProtoElementLoader::setDefaultTransf(const std::string &nmb)
  { nmb_transf= nmb; }

//! @brief Returns the name of the default coordinate transformation for new elements.
const std::string &XC::ProtoElementLoader::getDefaultTransf(void) const
  { return nmb_transf; }

//! @brief Sets the name of the default integrator for new elements.
void XC::ProtoElementLoader::setDefaultIntegrator(const std::string &nmb)
  { nmb_integ= nmb; }

//! @brief Returns the name of the default integrator for new elements.
const std::string &XC::ProtoElementLoader::getDefaultIntegrator(void) const
  { return nmb_integ; }

