/**
 * Logger for collecting driving data from vehicles.
 * This data is later used in the evaluation as the ground truth.
 *
 * @author  Martin Dell (WS22/23)
 * @date    06.02.2023
 */

#ifndef __MobCom_LoggerService_H_
#define __MobCom_LoggerService_H_

#include <memory>
#include "artery/application/ItsG5BaseService.h"
#include "artery/application/VehicleDataProvider.h"
#include "artery/traci/VehicleController.h"
#include "traci/API.h"

namespace mobcom
{
    /**
     * @brief Represents one entry in the log file
     *        containing dynamic and static data of a vehicle.
     *
     */
    struct VehicleData
    {
        long timestamp;                     // ms
        long serviceId;
        std::string sumoId;
        long pseudonym;
        traci::TraCIGeoPosition position;
        long heading;                       // deg * 10
        long speed;                         // cm/s
    };

    /**
     * @brief A service which logs on each simulation step the
     *        dynamic and static data of a vehicle to a file.
     *
     */
    class LoggerService : public artery::ItsG5BaseService
    {
    public:
        void initialize() override;
        void trigger() override;

    private:
        const artery::VehicleDataProvider* m_vehicleDataProvider = nullptr;
        const traci::VehicleController* m_vehicleController = nullptr;
        std::shared_ptr<const traci::API> m_traciApi;
        int m_serviceId;
        std::string m_vehicleId;

        std::string m_logfile;
    };
}

#endif /* __MobCom_LoggerService_H_ */
