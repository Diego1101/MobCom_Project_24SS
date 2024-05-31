/**
 * Distance Pseudonym Change Service 
 *
 * @file    DistancePCService.cc
 * @author  Janis Latus
 * @date    12.11.2022
 */

#include "DistancePCService.h"
#include "artery/application/VehicleDataProvider.h"


namespace artery
{
    using namespace omnetpp;
    
    Define_Module(DistancePCService);

    void DistancePCService::initialize()
    {
        BasePCService::initialize();

        //Get init value for pseudonym change distance
        this->_pseudonymChangeDistance = par("pseudonymChangeDistance");
        
        //Get initial position 
        this->_lastPosition = mVehicleDataProvider->position();
    }

    bool DistancePCService::triggerConditionsAreMet()
    {
        //Get current postion
        artery::Position newPosition = mVehicleDataProvider->position();
        
        //Calculate the distance driven since last cylcle
        vanetza::units::Length distanceDriven = distance(this->_lastPosition, newPosition);
#ifdef DEBUG
        std::cout << "Car Id:"<<mId<< ", Driven distance:"<< distanceDriven.value() << std::endl;
#endif
        //If distance crossed the threshold change the pseudonym
        if (distanceDriven >= (this->_pseudonymChangeDistance * vanetza::units::si::meter))
        {
            //Update last position
            this->_lastPosition = newPosition;
            return true;
        }

        return false;
    }
}
