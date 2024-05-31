/**
 * SLOW Pseudonym Change Service
 *
 * @file    SLOWPCService.cc
 * @author  Samuel Müller
 * @author  Kevin Ehling
 * @date    14.12.2022
 */

#include "SLOWPCService.h"
#include "BasePCService.h"
#include "artery/application/VehicleDataProvider.h"
#include "artery/application/CaService.h"
#include <omnetpp/simtime.h>

namespace artery
{
    using namespace omnetpp;

    Define_Module(SLOWPCService);

    bool SLOWPCService::triggerConditionsAreMet()
    {
        double lastChangeDiff = (simTime() - _lastPseudonymChange).dbl();
        if(isSlow() && lastChangeDiff >= _pseudonymLifetime){
            _lastPseudonymChange = simTime();
            //std::cout<<"SLOW data for "<<mVehicleDataProvider->getStationId()<<"("<<simTime()<<") - currentSpeed: "<<mVehicleDataProvider->speed().value()<<" lastChangeDiff: "<<lastChangeDiff<<endl;
            return true;
        }
        return false;
    }

    void SLOWPCService::indicate(const vanetza::btp::DataIndication& ind, std::unique_ptr<vanetza::UpPacket> packet)
    {
        if (sendCamConditionsAreMet())
        {
            return;
        }
        CaService::indicate(ind, std::move(packet));
    }

    bool SLOWPCService::sendCamConditionsAreMet()
    {
        return !isSlow();
    }

    void SLOWPCService::initialize()
    {
        BasePCService::initialize();
        _pseudonymLifetime = par("pseudonymLifetime");
        _slowThreshold = par("slowThreshold");
        _slowThreshold = _slowThreshold / 3.6;  // Convert km/h to m/s
        _lastPseudonymChange = simTime();
    }

    bool SLOWPCService::isSlow()
    {
        const vanetza::units::Velocity speed = mVehicleDataProvider->speed();
        return speed.value() <= _slowThreshold;
    }
}
