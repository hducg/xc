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

// $Revision: 1.10 $
// $Date: 2005/11/29 23:36:47 $
// $Source: /usr/local/cvs/OpenSees/SRC/analysis/analysis/StaticAnalysis.cpp,v $


// Written: fmk
//
// Description: This file contains the implementation of XC::StaticAnalysis.
//
// What: "@(#) StaticAnalysis.C, revA"

#include <solution/analysis/analysis/StaticAnalysis.h>
#include <solution/analysis/algorithm/equiSolnAlgo/EquiSolnAlgo.h>
#include <solution/analysis/model/AnalysisModel.h>
#include <solution/system_of_eqn/linearSOE/LinearSOE.h>
#include <solution/analysis/numberer/DOF_Numberer.h>
#include <solution/analysis/handler/ConstraintHandler.h>
#include <solution/analysis/convergenceTest/ConvergenceTest.h>
#include <solution/analysis/integrator/StaticIntegrator.h>
#include <domain/domain/Domain.h>
#include "solution/SoluMethod.h"

// AddingSensitivity:BEGIN //////////////////////////////////
#ifdef _RELIABILITY
#include <reliability/FEsensitivity/SensitivityAlgorithm.h>
#endif
// AddingSensitivity:END ////////////////////////////////////

//! @brief Constructor.
XC::StaticAnalysis::StaticAnalysis(SoluMethod *metodo)
  :Analysis(metodo), domainStamp(0)
  {
    // AddingSensitivity:BEGIN ////////////////////////////////////
#ifdef _RELIABILITY
    theSensitivityAlgorithm= nullptr;
#endif
    // AddingSensitivity:END //////////////////////////////////////
  }

//! @brief Destructor.
XC::StaticAnalysis::~StaticAnalysis(void)
  {
  // we don't invoke the destructors in case user switching
  // from a static to a direct integration analysis
  // clearAll() must be invoked if user wishes to invoke destructor
  }

//! @brief Clears all object members (constraint handler, analysis model,...).
void XC::StaticAnalysis::clearAll(void)
  {
    // invoke the destructor on all the objects in the aggregation
    Analysis::clearAll();

    // AddingSensitivity:BEGIN ////////////////////////////////////
#ifdef _RELIABILITY
    delete theSensitivityAlgorithm;
    theSensitivityAlgorithm =0;
#endif
    // AddingSensitivity:END //////////////////////////////////////
  }

//! @brief Ask the domain to performa a new analysis step.
int XC::StaticAnalysis::new_domain_step(int num_step)
  {
    AnalysisModel *am= getAnalysisModelPtr();
    assert(am);
    int result= newStepDomain(am);
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
		  << "; the AnalysisModel failed"
                  << " at step: " << num_step << " with domain at load factor "
                  << getDomainPtr()->getTimeTracker().getCurrentTime()
		  << " after " << getConvergenceTest()->getCurrentIter()-1
		  << " iterations." << std::endl;
	if(num_step>1)
	  std::cerr << "In a static analysis, "
	            << " a number of steps greater than 1 is useless"
	            << " if the loads and constraints are constant";
        getDomainPtr()->revertToLastCommit();
        return -2;
      }
    return result;
  }

//! @brief Check if the domain has changed after the last analysis step.
//! It's used in run_analysis_step method.
int XC::StaticAnalysis::check_domain_change(int num_step,int numSteps)
  {
    int result= 0;
    int stamp= getDomainPtr()->hasDomainChanged();

    if(stamp != domainStamp)
      {
        domainStamp= stamp;
        result= domainChanged();

        if(result < 0)
          {
            std::cerr << nombre_clase() << "::" << __FUNCTION__
		      << "; domainChanged failed"
		      << " at step " << num_step << " of "
		      << numSteps << std::endl;
	    if(num_step>1)
    	      std::cerr << "In a static analysis, "
	                << " a number of steps greater than 1 is useless"
	                << " if the loads and constraints are constant";
            return -1;
          }
      }
    return result;
  }

//! @brief Ask the integrator to perform a new step in the analysis.
int XC::StaticAnalysis::new_integrator_step(int num_step)
  {
    const int result= getStaticIntegratorPtr()->newStep();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
		  << "; the Integrator failed"
                  << " at step: " << num_step << " with domain at load factor "
                  << getDomainPtr()->getTimeTracker().getCurrentTime()
		  << std::endl;
	if(num_step>1)
          std::cerr << "In a static analysis, "
                    << " a number of steps greater than 1 is useless"
                    << " if the loads and constraints are constant";
        getDomainPtr()->revertToLastCommit();
        return -2;
      }
    return result;
  }

//! @brief Solves for current step.
int XC::StaticAnalysis::solve_current_step(int num_step)
  {
    const int result= getEquiSolutionAlgorithmPtr()->solveCurrentStep();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
		  << "; the Algorithm failed"
                  << " at step: " << num_step << " with domain at load factor "
                  << getDomainPtr()->getTimeTracker().getCurrentTime()
		  << std::endl;
	if(num_step>1)
          std::cerr << "In a static analysis, "
                    << " a number of steps greater than 1 is useless"
                    << " if the loads and constraints are constant";	  
        getDomainPtr()->revertToLastCommit();
        getStaticIntegratorPtr()->revertToLastStep();
        return -3;
      }
    return result;
  }

//! @brief Computes sensitivities for the current analysis step.
int XC::StaticAnalysis::compute_sensitivities_step(int num_step)
  {
    int result= 0;
#ifdef _RELIABILITY
    if(theSensitivityAlgorithm)
      {
        result= theSensitivityAlgorithm->computeSensitivities();
        if(result < 0)
          {
            std::cerr << nombre_clase() << "::" << __FUNCTION__
		      << "; the XC::SensitivityAlgorithm failed"
		      << " at step: " << num_step
		      << " with domain at load factor "
		      << getDomainPtr()->getTimeTracker().getCurrentTime()
		      << std::endl;
	    if(num_step>1)
              std::cerr << "In a static analysis, "
                        << " a number of steps greater than 1 is useless"
                        << " if the loads and constraints are constant";
            getDomainPtr()->revertToLastCommit();
            getStaticIntegratorPtr()->revertToLastStep();
            return -5;
          }
      }
#endif
    return result;
  }

//! @brief Consuma el estado al final del paso.
int XC::StaticAnalysis::commit_step(int num_step)
  {
    int result= getStaticIntegratorPtr()->commit();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__ << "; "
                  << "the Integrator failed to commit"
                  << " at step: " << num_step << " with domain at load factor "
                  << getDomainPtr()->getTimeTracker().getCurrentTime()
		  << std::endl;
	if(num_step>1)
          std::cerr << "In a static analysis, "
                    << " a number of steps greater than 1 is useless"
                    << " if the loads and constraints are constant";	  
        getDomainPtr()->revertToLastCommit();
        getStaticIntegratorPtr()->revertToLastStep();
        return -4;
      } 
    return result;
  }

//! @brief Performs un paso of the analysis.
int XC::StaticAnalysis::run_analysis_step(int num_step,int numSteps)
  {
    int result= new_domain_step(num_step);
    if(result < 0) //Fallo en new_domain_step.
      return -2;

    result= check_domain_change(num_step,numSteps);
    if(result < 0) //Fallo en check_domain_change.
      return -1;

    result= new_integrator_step(num_step);
    if(result < 0) //Fallo en new_integrator_step.
      return -2;

    result= solve_current_step(num_step);
    if(result<0) //Fallo en solve_current_step.
      return -3;


// AddingSensitivity:BEGIN ////////////////////////////////////
#ifdef _RELIABILITY
    result= compute_sensitivities_step(num_step);
    if(result<0) //Fallo en compute_sensitivities_step.
      return -5;
#endif
// AddingSensitivity:END //////////////////////////////////////

    result= commit_step(num_step);
    if(result < 0) //Fallo en commit_step.
      return -4;

    return result;
  }

//! @brief Performs the analysis.
//!
//! @param numSteps: number of steps in the analysis
//! (for static analysis, if the loads are constant it's useless to
//! increase the number of steps so \p numSteps= 1)
int XC::StaticAnalysis::analyze(int numSteps)
  {
    assert(metodo_solu);
    EntCmd *old= metodo_solu->Owner();
    metodo_solu->set_owner(this);
    int result= 0;
    for(int i=0; i<numSteps; i++)
      {
        result= run_analysis_step(i,numSteps);
        if(result < 0) //Fallo en run_analysis_step.
          break;
      }
    metodo_solu->set_owner(old);
    return result;
  }

int XC::StaticAnalysis::initialize(void)
  {
    Domain *the_Domain= this->getDomainPtr();

    // check if domain has undergone change
    int stamp= the_Domain->hasDomainChanged();
    if(stamp != domainStamp)
      {
        domainStamp= stamp;
        if(this->domainChanged() < 0)
          {
            std::cerr << nombre_clase() << "::" << __FUNCTION__
		      << "; domainChanged() failed\n";
            return -1;
          }
      }
    if(getStaticIntegratorPtr()->initialize() < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
		  << "; integrator initialize() failed\n";
        return -2;
      }
    else
      getStaticIntegratorPtr()->commit();
    return 0;
  }

//! @brief Hace los cambios que sean necesarios tras un cambio en el domain.
int XC::StaticAnalysis::domainChanged(void)
  {
    Domain *the_Domain= this->getDomainPtr();
    int stamp= the_Domain->hasDomainChanged();
    domainStamp= stamp;

    getAnalysisModelPtr()->clearAll();
    getConstraintHandlerPtr()->clearAll();

    // now we invoke handle() on the constraint handler which
    // causes the creation of FE_Element and DOF_Group objects
    // and their addition to the AnalysisModel.

    int result= getConstraintHandlerPtr()->handle();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
                  << "; ConstraintHandler::handle() failed." << std::endl;
        return -1;
      }

    // we now invoke number() on the numberer which causes
    // equation numbers to be assigned to all the DOFs in the
    // AnalysisModel.

    result= getDOF_NumbererPtr()->numberDOF();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
                  << "; DOF_Numberer::numberDOF() failed." << std::endl;
        return -2;
      }

    result= getConstraintHandlerPtr()->doneNumberingDOF();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
                  << "; constraintHandler::doneNumberingDOF() failed." << std::endl;
        return -3;
      }

    // we invoke setSize() on the LinearSOE which
    // causes that object to determine its size
    Graph &theGraph= getAnalysisModelPtr()->getDOFGraph();

    result= getLinearSOEPtr()->setSize(theGraph);
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
                  << "; LinearSOE::setSize() failed." << std::endl;
        return -4;
      }

    // finally we invoke domainChanged on the Integrator and Algorithm
    // objects .. informing them that the model has changed

    result= getStaticIntegratorPtr()->domainChanged();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
                  << "Integrator::domainChanged() failed." << std::endl;
        return -5;
      }

    result= getEquiSolutionAlgorithmPtr()->domainChanged();
    if(result < 0)
      {
        std::cerr << nombre_clase() << "::" << __FUNCTION__
                  << "; Algorithm::domainChanged() failed." << std::endl;
        return -6;
      }

    // if get here successfull
    return 0;
  }

// AddingSensitivity:BEGIN //////////////////////////////
#ifdef _RELIABILITY
int XC::StaticAnalysis::setSensitivityAlgorithm(SensitivityAlgorithm *passedSensitivityAlgorithm)
  {
    int result= 0;

    // invoke the destructor on the old one
    if(theSensitivityAlgorithm)
      { delete theSensitivityAlgorithm; }
    theSensitivityAlgorithm= passedSensitivityAlgorithm;
    return 0;
  }
#endif
// AddingSensitivity:END ///////////////////////////////

//! @brief Sets the renumerador to use in the analysis.
int XC::StaticAnalysis::setNumberer(DOF_Numberer &theNewNumberer)
  {
    Analysis::setNumberer(theNewNumberer);
    // invoke domainChanged() either indirectly or directly
    domainStamp= 0;
    return 0;
  }


//! @brief Sets the solution algorithm to use in the analysis.
int XC::StaticAnalysis::setAlgorithm(EquiSolnAlgo &theNewAlgorithm)
  {
    Analysis::setAlgorithm(theNewAlgorithm);

    // invoke domainChanged() either indirectly or directly
    domainStamp= 0;
    return 0;
  }

//! @brief Sets the integrator to use in the analysis.
int XC::StaticAnalysis::setIntegrator(StaticIntegrator &theNewIntegrator)
  {
    Analysis::setIntegrator(theNewIntegrator);
    // cause domainChanged to be invoked on next analyze
    domainStamp= 0;
    return 0;
  }

//! @brief Sets the linear system of equations to use in the analysis.
int XC::StaticAnalysis::setLinearSOE(LinearSOE &theNewSOE)
  {
    // invoke the destructor on the old one
    Analysis::setLinearSOE(theNewSOE);
    // cause domainChanged to be invoked on next analyze
    domainStamp= 0;
    return 0;
  }

//! @brief Sets the convergence test to use in the analysis.
int XC::StaticAnalysis::setConvergenceTest(ConvergenceTest &theNewTest)
  { return metodo_solu->setConvergenceTest(theNewTest); }



XC::ConvergenceTest *XC::StaticAnalysis::getConvergenceTest(void)
  {
    if(metodo_solu)
      return metodo_solu->getConvergenceTestPtr();
    else
      return nullptr;
  }
