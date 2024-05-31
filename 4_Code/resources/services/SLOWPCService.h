/**
 * SLOW Pseudonym Change Service
 *
 * @file    SLOWPCService.h
 * @author  Samuel Müller
 * @date    05.01.2022
 */

#ifndef __VEINS_SLOWPC_H_
#define __VEINS_SLOWPC_H_

#include "BasePCService.h"
#include <omnetpp/simtime.h>
#include <vanetza/units/velocity.hpp>
#include <vanetza/btp/data_interface.hpp>

namespace artery
{

    class SLOWPCService : public BasePCService
    {
    public:
        void initialize() override;
		void indicate(const vanetza::btp::DataIndication&, std::unique_ptr<vanetza::UpPacket>) override;

    protected:
        /**
         * The time in seconds after which the pseudonym is changed.
         */
        double _pseudonymLifetime;
        /**
         * The max speed in m/s where a vehicle is considered slow.
         * Slow vehicles do not send CAMs.
         */
        double _slowThreshold;

        /**
         * Time of the last pseudonym change.
         */
        omnetpp::SimTime _lastPseudonymChange;

        bool triggerConditionsAreMet() override;
        bool sendCamConditionsAreMet() override;
        bool isSlow();
    };
}

#endif
