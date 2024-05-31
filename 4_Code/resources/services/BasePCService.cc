/**
 * Base class for all pseudonym change strategies.
 * Each pseudonym change strategy service class should implement
 * `triggerConditionsAreMet` function.
 *
 * @author  Samuel Müller (WS21/22)
 * @author  Martin Dell (WS22/23)
 * @date    24.01.2023
 */


#include "BasePCService.h"
#include "artery/application/CaService.h"
#include "artery/application/VehicleDataProvider.h"

#include <cstdlib>
#include <iostream>
#include <iomanip>

namespace artery
{
    using namespace omnetpp;

    Define_Module(BasePCService);

    static const simsignal_t scPseudonymChanged = cComponent::registerSignal("PseudonymChanged");

    void BasePCService::initialize()
    {
        Enter_Method("BasePCService initialize");

        CaService::initialize();
    }

    void BasePCService::trigger()
    {
        Enter_Method("BasePCService trigger");
        if (triggerConditionsAreMet())
        {
            changePseudonym();
        }
        if (sendCamConditionsAreMet())
        {
            CaService::trigger();
        }
    }

    void BasePCService::changePseudonym()
    {
        uint32_t pseudoRandomStationId = std::rand();
        uint32_t previousId = mVehicleDataProvider->getStationId();

        const_cast<VehicleDataProvider *>(mVehicleDataProvider)->setStationId(pseudoRandomStationId);

        logPseudonymChange(pseudoRandomStationId, previousId);

        emit(scPseudonymChanged, (double) pseudoRandomStationId);
    }

    void BasePCService::logPseudonymChange(uint32_t newPseudonym, uint32_t prevPseudonym) const
    {
        std::cout
            << "Pseudonym changed: "
            << "V#"
            << std::left << std::setw(6) << mId
            << " "
            << std::right << std::setw(10) << prevPseudonym
            << " -> "
            << std::setw(10) << newPseudonym
            << " at t="
            << simTime().inUnit(SimTimeUnit::SIMTIME_MS)
            << '\n';
    }
}
