/**
 * Distance Pseudonym Change Service 
 *
 * @file    DistancePCService.h
 * @author  Janis Latus
 * @date    12.11.2022
 */

#ifndef __VEINS_DistancePC_H_
#define __VEINS_DistancePC_H_

#include "BasePCService.h"

namespace artery
{
    /**
     *  This class implements a pseudonym change strategy 
     *  which changes the pseudonym after a defined driven distance
     */
    class DistancePCService : public BasePCService
    {

    public:
        /**
         * Initialize the service
         */
        void initialize() override;

    private:
        /**
         * Distance when pseudonym change shall happen
         */
        double _pseudonymChangeDistance;

        /**
         * Last position of the vehicle
         */
        artery::Position _lastPosition;
    
    protected:
        /*
         * Calculates distance between current and last position.
         * @Returns True if traveled distance is bigger then _pseudonymChangeDistance threshold; otherwise false.
         */
        bool triggerConditionsAreMet() override;
    };
}

#endif
