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
/*
//================================================================================
# COPYRIGHT (C):     :-))                                                        #
# PROJECT:           Object Oriented Finite XC::Element Program                      #
# PURPOSE:           General platform for elaso-plastic constitutive model       #
#                    implementation                                              #
# CLASS:             MDEvolutionLaw (evolution law for Manzari-Dafalias Model)   #
#                                                                                #
# VERSION:                                                                       #
# LANGUAGE:          C++.ver >= 2.0 ( Borland C++ ver=3.00, SUN C++ ver=2.1 )    #
# TARGET OS:         DOS || UNIX || . . .                                        #
# DESIGNER(S):       Boris Jeremic, Zhaohui Yang                                 #
# PROGRAMMER(S):     Boris Jeremic, Zhaohui Yang                                 #
#                                                                                #
#                                                                                #
# DATE:              08-03-2000                                                  #
# UPDATE HISTORY:                                                                #
#                                                                                #
#                                                                                #
#                                                                                #
#                                                                                #
# SHORT EXPLANATION: The goal is to create a platform for efficient and easy     #
#                    implemetation of any elasto-plastic constitutive model!     #
#                                                                                #
//================================================================================
*/

#ifndef MD_EL_CPP
#define MD_EL_CPP

#include "material/nD/Template3Dep/MD_EL.h"
#include <utility/matrix/nDarray/basics.h>
#include <iomanip>    

//================================================================================
// Copy constructor
//================================================================================

XC::MDEvolutionLaw::MDEvolutionLaw(const MDEvolutionLaw &MDE ) {

    this->Mc     = MDE.getMc();
    this->Me     = MDE.getMe();
    this->Lambda = MDE.getLambda();
    this->ec_ref = MDE.getec_ref();
    this->p_ref=  MDE.getp_ref();
    this->kc_b =  MDE.getkc_b();
    this->kc_d =  MDE.getkc_d();
    this->ke_b =  MDE.getke_b();
    this->ke_d =  MDE.getke_d();
    //this->h    =  MDE.geth();
    this->ho   =  MDE.getho();
    this->Cm   =  MDE.getCm();
    this->eo   =  MDE.geteo();
    //this->D    =  MDE.D;
    this->Ao   =  MDE.getAo();
    this->Fmax =  MDE.getFmax(); 
    this->Cf   =  MDE.getCf();
}


//================================================================================
//  Create a clone of itself 
//================================================================================
XC::MDEvolutionLaw *XC::MDEvolutionLaw::newObj() {
    
    MDEvolutionLaw *newEL = new MDEvolutionLaw( *this );
    
    return newEL;

}

//================================================================================
//  Initialize some  vars in XC::EPState				        
//  1. E_Young,  2. e						       	
//							       		
//  XC::Tensor vars store | 1. alpha,|  2. F  |  3. n              	        
//  Scalar vars store | 1. m,    |  2. D  |  3. void ratio(e)  	        
//							       	        
//================================================================================

void XC::MDEvolutionLaw::InitVars(EPState  *EPS) {

    // set initial E_Young corresponding to current stress state
    double p_atm = 100.0; //Kpa atmospheric pressure
    double p = EPS->getStress().p_hydrostatic();
    double E = EPS->getEo() * pow( (p/p_atm), geta());
    EPS->setE( E );
      
    //=========================================================================
    //set initial void ratio from hardening scalar var  (third one)
    double eo = EPS->getScalarVar( 3 );
    seteo( eo );

    ////=========================================================================
    //// Update D 
    //   
    //double m = EPS->getScalarVar(1);
    //XC::stresstensor F = EPS->getTensorVar( 2 );   // getting  F_ij from XC::EPState
    //BJtensor temp_tensor = F("ij") * n("ij");
    //double temp = temp_tensor.trace();
    //
    //if (temp < 0)   temp = 0;
    //double A = getAo() * (1.0 + temp);
    //
    ////Calculating the lode angle theta
    //double J2_bar = r_bar.Jinvariant2();
    //double J3_bar = r_bar.Jinvariant3();
    //double theta = acos( 3.0*pow(3.0, 0.5)/2.0*J3_bar/ pow( J2_bar, 1.5) ) / 3.0;
    //
    //double c = getMe() / getMc();
    //double cd = getke_d() / getkc_d();
    //XC::stresstensor alpha_theta_d = n("ij") * (g_WW(theta, c) * Mc + g_WW(theta, cd) * kc_d * xi - m);
    //
    //temp_tensor = A*( alpha_theta_d - alpha );
    //temp_tensor.null_indices();
    //BJtensor temp1 = temp_tensor("ij") * n("ij");
    //double D = temp1.trace();
    //EPS->setScalarVar(2, D);
    
}   


//================================================================================
//  Set initial value of D once the current stress hit the yield surface     	
//      						       	        
//							       		
//  XC::Tensor vars store | 1. alpha,|  2. F  |  3. n              	        
//  Scalar vars store | 1. m,    |  2. D  |  3. void ratio(e)  	        
//							       	        
//================================================================================

void XC::MDEvolutionLaw::setInitD(EPState  *EPS) {

    //=========================================================================
    //calculate  n_ij
    XC::stresstensor S = EPS->getStress().deviator();
    double p = EPS->getStress().p_hydrostatic();
    XC::stresstensor alpha = EPS->getTensorVar( 1 );  // alpha_ij

    // Find the norm of alpha
    BJtensor norm_alphat = alpha("ij") * alpha("ij");
    double norm_alpha = sqrt( norm_alphat.trace() );
   
    XC::stresstensor r = S * (1.0 / p);
    //r.reportshort("r");
    XC::stresstensor r_bar = r - alpha;
    XC::stresstensor norm2 = r_bar("ij") * r_bar("ij");
    double norm = sqrt( norm2.trace() );
    
    XC::stresstensor n;
    if ( norm >= d_macheps() ){ 
      n = ( r  - alpha ) *(1.0 / norm );
    }
    else {
      ::printf(" \n\n n_ij not defined!!!! Program exits\n");
      exit(1);
    }

    //Calculate the state parameters xi 
    double e = EPS->getScalarVar(3);
    double ec = getec_ref() - getLambda() * log( p/getp_ref() );
    double xi = e - ec;

    //calculating A
    double m = EPS->getScalarVar(1);
    XC::stresstensor F = EPS->getTensorVar( 2 );   // getting  F_ij from XC::EPState
    BJtensor temp_tensor = F("ij") * n("ij");
    double temp = temp_tensor.trace();
    if (temp < 0)   temp = 0;
    double A = Ao*(1.0 + temp);

    //Calculating the lode angle theta
    double J2_bar = r_bar.Jinvariant2();
    double J3_bar = r_bar.Jinvariant3();
    double tempd = 3.0*pow(3.0, 0.5)/2.0*J3_bar/ pow( J2_bar, 1.5);

    if (tempd > 1.0 ) tempd = 1.0; //bug. if tempd = 1.00000000003, acos gives nan
    if (tempd < -1.0 ) tempd = -1.0;

    double theta = acos( tempd ) / 3.0;
    
    //=========================================================================
    //calculate the alpha_theta_b and alpha_theta_d
    double c = getMe() / getMc();

    double cd = getke_d() / getkc_d();
    double alpha_theta_dd = (g_WW(theta, c) * Mc + g_WW(theta, cd) * kc_d * xi - m);
    XC::stresstensor alpha_theta_d = n("ij") * alpha_theta_dd * pow(2.0/3.0, 0.5);

    XC::stresstensor d;
    d =  alpha_theta_d - alpha;
    d.null_indices();

    BJtensor temp1 = d("ij") * n("ij");
    temp1.null_indices();
    double D_new = temp1.trace() * A;
    //Check the restrictions on D
    if ( (xi > 0.0) && ( D_new < 0.0) )
       D_new = 0.0;  

    EPS->setScalarVar(2, D_new);  // Updating D
    
}   

//================================================================================
//  Updating all internal vars                                          
//							       		
//  XC::Tensor vars store | 1. alpha,|  2. F                   	        
//  Scalar vars store | 1. m,    |  2. D  |  3. void ratio(e)  	        
//							       	        
//  always use non-updated parameters to update vars, don't mix it up!!! ?? n_ij new? old?
//================================================================================

void XC::MDEvolutionLaw::UpdateAllVars( EPState *EPS, double dlamda) {
   
    //=========================================================================
    //calculate  n_ij
    XC::stresstensor S = EPS->getStress().deviator();
    double p = EPS->getStress().p_hydrostatic();
    XC::stresstensor alpha = EPS->getTensorVar( 1 );  // alpha_ij

    // Find the norm of alpha
    BJtensor norm_alphat = alpha("ij") * alpha("ij");
    double norm_alpha = sqrt( norm_alphat.trace() );
   
    XC::stresstensor r = S * (1.0 / p);
    //r.reportshort("r");
    XC::stresstensor r_bar = r - alpha;
    XC::stresstensor norm2 = r_bar("ij") * r_bar("ij");
    double norm = sqrt( norm2.trace() );
    
    XC::stresstensor n;
    if ( norm >= d_macheps() ){ 
      n = ( r  - alpha ) *(1.0 / norm );
    }
    else {
      ::printf(" \n\n n_ij not defined!!!! Program exits\n");
      exit(1);
    }
    //EPS->setTensorVar( 3, n); //update n_ij//

    // Update E_Young corresponding to current stress state
    double p_atm = 100.0; //Kpa, atmospheric pressure
    double E = EPS->getE();  // old E_Young
    double E_new = EPS->getEo() * pow( (p/p_atm), geta() ); 
    EPS->setE( E_new );

    // Update void ratio
    
    double e = EPS->getScalarVar(3);
    double D = EPS->getScalarVar(2);
    double elastic_strain_vol = EPS->getdElasticStrain().Iinvariant1();
    double plastic_strain_vol = EPS->getdPlasticStrain().Iinvariant1();

    double de_p = -( 1.0 + e ) * plastic_strain_vol; // plastic change of void ratio ?? e or eo?
    double de_e = -( 1.0 + e ) * elastic_strain_vol; // elastic change of void ratio ????
    clog << "get dPlasticStrain-vol" << plastic_strain_vol << std::endl;
    clog << "get dElasticStrain-vol" << elastic_strain_vol << std::endl;

    clog << "^^^^^^^^^^^ de_e = " << de_e << " de_p = " << de_p << std::endl; 
    double new_e = e + de_p + de_e;

    EPS->setScalarVar( 3, new_e ); // Updating e


    //Calculate the state parameters xi 
    double ec = getec_ref() - getLambda() * log( p/getp_ref() );

    double xi = e - ec;

    // Update D 
       
    double m = EPS->getScalarVar(1);
    XC::stresstensor F = EPS->getTensorVar( 2 );   // getting  F_ij from XC::EPState
    BJtensor temp_tensor = F("ij") * n("ij");
    double temp = temp_tensor.trace();
    if (temp < 0)   temp = 0;
    double A = Ao*(1.0 + temp);

    //Calculating the lode angle theta
    double J2_bar = r_bar.Jinvariant2();
    double J3_bar = r_bar.Jinvariant3();
    double tempd = 3.0*pow(3.0, 0.5)/2.0*J3_bar/ pow( J2_bar, 1.5);

    if (tempd > 1.0 ) tempd = 1.0; //bug. if tempd = 1.00000000003, acos gives nan
    if (tempd < -1.0 ) tempd = -1.0;

    double theta = acos( tempd ) / 3.0;
    
    //=========================================================================
    //calculate the alpha_theta_b and alpha_theta_d
    double c = getMe() / getMc();

    double cd = getke_d() / getkc_d();
    double alpha_theta_dd = (g_WW(theta, c) * Mc + g_WW(theta, cd) * kc_d * xi - m);
    XC::stresstensor alpha_theta_d = n("ij") * alpha_theta_dd * pow(2.0/3.0, 0.5);

    double cb = getke_b() / getkc_b();
    if ( xi > 0 ) xi = 0.0;  // < -xi >
    double alpha_theta_bd = (g_WW(theta, c) * Mc + g_WW(theta, cb) * kc_b * (-xi) - m);
    XC::stresstensor alpha_theta_b = n("ij") *alpha_theta_bd * pow(2.0/3.0, 0.5);
    alpha_theta_b.null_indices();

    XC::stresstensor b;
    b =  alpha_theta_b - alpha;
    b.null_indices();
    XC::stresstensor d;
    d =  alpha_theta_d - alpha;
    d.null_indices();

    BJtensor temp1 = d("ij") * n("ij");
    temp1.null_indices();
    double D_new = temp1.trace() * A;
    //Check the restrictions on D
    if ( (xi > 0.0) && ( D_new < 0.0) )
       D_new = 0.0;  

    EPS->setScalarVar(2, D_new);  // Updating D
    //EPS->setScalarVar(2, 0.0);  // Updating D
    
 
    //=========================================================================
    // Update m
    double dm = dlamda * getCm() * ( 1.0 + e ) * D;
    EPS->setScalarVar(1, m + dm); // Updating m
    clog  << std::endl << "dm = " << dm << std::endl;

    //=========================================================================
    // Update alpha

    //calculate b_ref
    double alpha_c_b = g_WW(0.0, c) * Mc + g_WW(0.0, cb) * kc_b * (-xi) - m;
    double b_ref = 2.0 * pow(2.0/3.0, 0.5) * alpha_c_b;
    
    temp1 = b("ij") * n("ij");
    double bn = temp1.trace();
    clog << "xxxxxxxxxxxxxxxxxxx  bn " << bn << std::endl;


    double h = getho() * fabs(bn) / ( b_ref - fabs(bn) );
    //h = h + pow(2.0/3.0, 0.5) * getCm() * ( 1.0 + geteo() ) * A * bn;

    clog << " ||b|| " << (alpha_theta_bd - norm_alpha) << std::endl;
    clog << " dlamda " << dlamda << " h = " << h << std::endl;

    XC::stresstensor dalpha;
    dalpha = dlamda * h * b("ij");
    //dalpha.null_indices();
    clog << "delta alpha =" << dalpha << std::endl;
    
    //dalpha.reportshortpqtheta("\n dalpha ");
    alpha = alpha + dalpha;
    alpha.null_indices();
    //alpha.reportshort("Alpha");
    EPS->setTensorVar(1, alpha);

    //=========================================================================
    // Update F
    XC::stresstensor dF;
    if ( D > 0.0 ) D = 0.0;
    dF =  dlamda * getCf() * (-D) * ( getFmax() * n("ij") + F("ij") );
    //clog << "dF" << dF;
    
    F = F - dF;
    EPS->setTensorVar(2, F);

}


//
//

//================================================================================
// calculating Kp 
//================================================================================

double XC::MDEvolutionLaw::getKp( EPState *EPS , double dummy) {

    //clog << "el-pl EPS: " <<  *EPS ;
    
    //=========================================================================
    //calculate  n_ij
    XC::stresstensor S = EPS->getStress().deviator();
    double p = EPS->getStress().p_hydrostatic();
    XC::stresstensor alpha = EPS->getTensorVar( 1 );  // alpha_ij
   
    XC::stresstensor r = S * (1.0 / p);
    //r.reportshort("r");
    XC::stresstensor r_bar = r - alpha;
    XC::stresstensor norm2 = r_bar("ij") * r_bar("ij");
    double norm = sqrt( norm2.trace() );
    
    XC::stresstensor n;
    if ( norm >= d_macheps() ){ 
      n = ( r  - alpha ) *(1.0 / norm );
    }
    else {
      ::printf(" \n\n n_ij not defined!!!! Program exits\n");
      exit(1);
    }
    
    //=========================================================================
    //calculating b_ij

    //Calculate the state parameters xi 
    double e = EPS->getScalarVar(3);
    double ec = getec_ref() - getLambda() * log( p/getp_ref() );
    double xi = e - ec;

    //Calculating the lode angle theta
    double J2_bar = r_bar.Jinvariant2();
    double J3_bar = r_bar.Jinvariant3();

    double tempd = 3.0*pow(3.0, 0.5)/2.0*J3_bar/ pow( J2_bar, 1.5);
    if (tempd > 1.0 ) tempd = 1.0; //bug. if tempd = 1.00000000003, acos gives nan
    if (tempd < -1.0 ) tempd = -1.0;
    double theta = acos( tempd ) / 3.0;

    
    //calculate the alpha_theta_b and alpha_theta_d
    double m = EPS->getScalarVar(1);
    double c = getMe() / getMc();

    double cd = getke_d() / getkc_d();
    XC::stresstensor alpha_theta_d = n("ij") * (g_WW(theta, c) * Mc + g_WW(theta, cd) * kc_d * xi - m) * pow(2.0/3.0, 0.5);


    double cb = getke_b() / getkc_b();
    if ( xi > 0.0 ) xi = 0.0;  // < -xi >
    XC::stresstensor alpha_theta_b = n("ij") * (g_WW(theta, c) * Mc - g_WW(theta, cb) * kc_b * xi - m) * pow(2.0/3.0, 0.5);
    alpha_theta_b.null_indices();

    //=========================================================================
    // calculating h
    XC::stresstensor b;
    b =  alpha_theta_b - alpha;
    b.null_indices();
    XC::stresstensor d;
    d =  alpha_theta_d - alpha;
    d.null_indices();

    double alpha_c_b = g_WW(0.0, c) * Mc + g_WW(0.0, cb) * kc_b * (-xi) - m;
    double b_ref = 2.0 * pow(2.0/3.0, 0.5) * alpha_c_b;
    

    BJtensor temp1 = b("ij") * n("ij");
    double bn = temp1.trace();

    temp1 = d("ij") * n("ij");
    double dn = temp1.trace();


    // Calculating A
    XC::stresstensor F = EPS->getTensorVar( 2 );   // getting  F_ij from XC::EPState
    temp1 = F("ij") * n("ij");
    double temp = temp1.trace();
    if (temp < 0)   temp = 0;
    double A = Ao*(1.0 + temp);

    double h = getho() * fabs(bn) / ( b_ref - fabs(bn) ); 
    clog << "ho =" << getho()  << "   h =" << h << std::endl;


    //=========================================================================

    double Kp = h * bn + pow(2.0/3.0, 0.5) * getCm() * ( 1.0 + geteo() ) * A * dn;
    //double Kp = pow(2.0/3.0, 0.5) * getCm() * ( 1.0 + geteo() ) * A * dn;
    Kp = Kp * p;

    return Kp;

}


//void UpdateAllTensorVar( EPState *EPS ) = 0;  // Evolve all XC::BJtensor vars

//================================================================================
//  Interpolation function No.1  -- Agyris: g_A(theta, e) 
//================================================================================

double XC::MDEvolutionLaw::g_A(double theta, double e) {

    double temp = 2.0 * e;
    temp  = temp / ( (1.0 + e) - (1.0 - e) * cos(3.0*theta) ); 

    return temp;
}


//================================================================================
//  Interpolation function No.1  -- Willan-Warkne: g_WW(theta, e)
//================================================================================

double XC::MDEvolutionLaw::g_WW(double theta, double e) {


    double g1 = 4.0*( 1.0 - e*e ) * cos(theta) * cos(theta) + pow(2.0*e-1.0, 2.0);
    double d1 = 2.0*( 1.0 - e*e ) * cos( theta );
    double d2 = ( 2.0*e-1.0 ) * pow( (4.0*(1.0-e*e)*cos(theta)*cos(theta) + 5.0*e*e - 4.0*e), 0.5);
    double temp =( d1 + d2 ) / g1; 

    return temp;
}


//================================================================================
//  Print vars defined in MD Evolution Law
//================================================================================
void XC::MDEvolutionLaw::print()
  {
    clog << " Manzari-Dafalias Evolution Law's Parameters" << std::endl;
    clog << (*this);
  }

//================================================================================
double XC::MDEvolutionLaw::getMc() const 
  { return Mc; }

//================================================================================
double XC::MDEvolutionLaw::getMe() const 
  { return Me; }


//================================================================================
double XC::MDEvolutionLaw::getLambda() const
{
    return Lambda;
}

//================================================================================
double XC::MDEvolutionLaw::getec_ref() const
{
    return ec_ref;
}

//================================================================================
double XC::MDEvolutionLaw::getp_ref() const 
{
    return p_ref;
}

//================================================================================
double XC::MDEvolutionLaw::getkc_b() const
{
    return kc_b;
}

//================================================================================
double XC::MDEvolutionLaw::getkc_d() const  
{
    return kc_d;
}

//================================================================================
double XC::MDEvolutionLaw::getke_b() const
{
    return ke_b;
}

//================================================================================
double XC::MDEvolutionLaw::getke_d() const
{
    return ke_d;
}

//================================================================================
//double XC::MDEvolutionLaw::geth() const
//{       
//    return h;
//}

//================================================================================
double XC::MDEvolutionLaw::getho() const
{      
    return ho;
}

//================================================================================
double XC::MDEvolutionLaw::getCm() const
{       
    return Cm;
}

//================================================================================
double XC::MDEvolutionLaw::geteo() const
{       
    return eo;
}

//================================================================================
void XC::MDEvolutionLaw::seteo( double eod) 
{       
    eo = eod;
}

//================================================================================
double XC::MDEvolutionLaw::getAo() const
{       
    return Ao;
}

//================================================================================
double XC::MDEvolutionLaw::getFmax() const
{       
    return Fmax;
}

//================================================================================
double XC::MDEvolutionLaw::getCf() const
{       
    return Cf;
}

//================================================================================
double XC::MDEvolutionLaw::geta() const
{       
    return a;
}


#endif

