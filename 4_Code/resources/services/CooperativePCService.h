/**
 * Cooperative Pseudonym Change Service 
 * based on the number of neighbors (CPN)
 *
 * @file    CooperativePCService.h
 * @author  Janis Latus
 * @date    27.12.2022
 */

#ifndef __VEINS_COOPERATIVEPC_H_
#define __VEINS_COOPERATIVEPC_H_

#include "BasePCService.h"
#include <vanetza/btp/data_interface.hpp>

namespace artery
{

    class CooperativePCService : public BasePCService
    {
    public:
        /**
         * Initialize the service 
         */
        void initialize() override;

        /**
         * Receive CAM messages from other vehicles 
         */
		void indicate(const vanetza::btp::DataIndication&, std::unique_ptr<vanetza::UpPacket>) override;

    protected:
        /**
         * Trigger for setting own ready flag to 1
         */
        uint16_t _neighborThreshold;

        /**
         * Counts how many CAM' are received within 1 time-slot 
         */
        uint16_t _neighborCount;

        /**
         * Two vehicles are considered as neighbors if there 
         * distance is smaller then _neighborRadius
         */
        double _neighborRadius;

        /**
         * Indicates if pseudonym change shall happen
         */
        bool _readyForPC;

        /**
         * Check if pseudonym change shall be performed
         * @return true if yes, otherwise false 
         */
        bool triggerConditionsAreMet() override;
        
    };
}

#endif