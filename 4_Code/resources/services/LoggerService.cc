/**
 * Implementation of logger service.
 *
 * @author  Martin Dell (WS22/23)
 * @date    06.02.2023
 */

#include "LoggerService.h"

#include "artery/application/VehicleDataProvider.h"
#include <fstream>

namespace mobcom
{

/**
 * @brief Class for writing vehicle data to a log file.
 * @details The logging of this data is not done in the LoggerService class
 *          because for each vehicle an LoggerService object is created.
 *          To handle file operations cleanly we need some kind of static object to write to.
 * @author Martin Dell (WS22/23)
 *
 */
class LogWriter {
public:
    /**
     * @brief Initializes the log writer by opening the log file and writing the CSV header to it.
     * @author Martin Dell (WS22/23)
     *
     * @param log_filename The file name of the log file.
     */
    LogWriter(const std::string& log_filename)
    {
        std::cout << "Writing vehicle data to: " << log_filename << std::endl;

        m_file.open(log_filename, std::ios::trunc);
        m_file << "Timestamp,ServiceID,SumoID,Pseudonym,Longitude,Latitude,Speed,Heading" << std::endl;
    }

    /**
     * @brief Writes the @p vehicleData as an entry to the CSV log.
     * @author Martin Dell (WS22/23)
     *
     * @param vehicleData The CSV line to write.
     */
    void log(const VehicleData& vehicleData)
    {
        m_file  << vehicleData.timestamp << ","
                << vehicleData.serviceId << ","
                << vehicleData.sumoId << ","
                << vehicleData.pseudonym << ","
                << (long)(vehicleData.position.longitude * 10000000) << ","
                << (long)(vehicleData.position.latitude * 10000000) << ","
                << vehicleData.speed << ","
                << vehicleData.heading
                << "\n";
    }

    /**
     * @brief Deconstructs the log writer by closing the log file.
     * @author Martin Dell (WS22/23)
     *
     */
    ~LogWriter()
    {
        m_file.close();
    }

private:

    /**
     * @brief Write stream to the CSV log file.
     * @author Martin Dell (WS22/23)
     *
     */
    std::ofstream m_file;
};



Define_Module(LoggerService);

/**
 * @brief Initializes the vehicle logger service for one vehicle.
 * @author Martin Dell (WS22/23)
 *
 */
void LoggerService::initialize()
{
    artery::ItsG5BaseService::initialize();

    // Retrieve the necessary data providers to get the relevant vehicle data.
    m_vehicleDataProvider = &getFacilities().get_const<artery::VehicleDataProvider>();
	m_vehicleController = &getFacilities().get_const<traci::VehicleController>();
    m_traciApi = getFacilities().get_const<traci::VehicleController>().getTraCI();

    // Get the static artery and SUMO ids of the vehicle.
    m_serviceId = getId();
    m_vehicleId = m_vehicleController->getVehicleId();

    m_logfile = par("logfile").stringValue();
}

/**
 * @brief Called on each simulation step.
 *        Logs the static and dynamic parameters of the vehicle in this simulation step.
 * @author Martin Dell (WS22/23)
 *
 */
void LoggerService::trigger()
{
    // Static log writer because LoggerService is instantiated for each vehicle.
    static mobcom::LogWriter logWriter(m_logfile);

    VehicleData data;
    data.timestamp = m_traciApi->simulation.getTime() * 1000;
    data.serviceId = m_serviceId;
    data.sumoId = m_vehicleId;
    data.pseudonym = m_vehicleDataProvider->getStationId();
    data.position = m_traciApi->convertGeo(m_traciApi->vehicle.getPosition(m_vehicleId));
    data.heading = (long) m_traciApi->vehicle.getAngle(m_vehicleId) * 10;
    data.speed = (long) m_traciApi->vehicle.getSpeed(m_vehicleId) * 100;

    logWriter.log(data);
}

} /* namespace mobcom */
