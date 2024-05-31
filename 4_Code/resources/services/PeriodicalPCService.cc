/**
 * Periodical Pseudonym Change Service 
 *
 * @file    PeriodicalPCService.cc
 * @author  Samuel Müller
 * @date    05.01.2022
 */

#include "PeriodicalPCService.h"
#include <omnetpp/simtime.h>


namespace artery
{
    using namespace omnetpp;
    
    Define_Module(PeriodicalPCService);

    void PeriodicalPCService::initialize()
    {
        BasePCService::initialize();
        _pseudonymLifetime = par("pseudonymLifetime");
        if(simTime().dbl() < 0){
            _lastPseudonymChange = 0;
        } else {
            _lastPseudonymChange = simTime().dbl();
        }
    }

    bool PeriodicalPCService::triggerConditionsAreMet()
    {
        //std::cout<<mVehicleDataProvider->getStationId()<<": "<<(_lastPseudonymChange - simTime())<<" >= "<<_pseudonymLifetime<<endl;
        if ((simTime() - _lastPseudonymChange).dbl() >= _pseudonymLifetime)
        {
            _lastPseudonymChange = simTime().dbl();
            return true;
        }
        return false;
    }
}
