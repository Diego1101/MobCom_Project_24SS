/**
 * Header file for the implementation of the dynamic attacker model.
 *
 * @author  Julius Bächle (WS22/23)
 * @date    05.11.2022
 */

#ifndef MOBCOM_CASERVICE_H_
#define MOBCOM_CASERVICE_H_

#include "artery/application/ItsG5BaseService.h"
#include "artery/traci/VehicleController.h"
#include <vanetza/asn1/cam.hpp>
#include <omnetpp/simtime.h>
#include <vanetza/asn1/its/StationType.h>
#include <fstream>

/**
 * @brief Stores the parameters of a vehicle which
 *        remain static during the whole simulation.
 *
 */
struct StaticParams {
    int length = -1;
    int width = -1;
    StationType_t stationType = StationType_unknown;

    // compares to StaticParams-Objects
    bool operator== (const StaticParams& a_params1) const;
};

/**
 * @brief Stores the parameters of a vehicle which
 *        change with each received CAM.
 *
 */
struct DynamicParams {
    traci::TraCIGeoPosition position;
    long headingDg;
    long yawRateCdgs;
    long speedCms;
    long timestampMs;
};

/**
 * @brief Stores all data regarding the target.
 *
 */
struct Target {
    std::string id = "";
    uint32_t stationID = 0x0;
    uint32_t serviceId = 0;
    bool initialized = false;
    StaticParams staticParams;
    DynamicParams dynamicParams;
};

/**
 * @brief Class for the simulation of the dynamic attacker model.
 *
 */
class CaAttackerService : public artery::ItsG5BaseService {
    public:
        // Destructor
        ~CaAttackerService();

        // Called once when the attacker is spawning
        void initialize() override;

        // Called once every SUMO step
        void trigger() override;

        // Called when a CAM is received
        void indicate(const vanetza::btp::DataIndication&, std::unique_ptr<vanetza::UpPacket>) override;

    private:
        // Initialize the logfile
        void initializeLogfile();

        // Log a CAM
        void log(bool a_targetVisible, bool a_correctVehicle, int a_interventionCounter, uint32_t a_pseudonym,
                 const DynamicParams& a_targetParams, const DynamicParams& a_attackerParams);

        // Check whether the target is visible according to the artery environment model
        bool isTargetVisible() const;

        // Try to follow the target
        void followTarget() const;

        // Check whether two CAMs can belong to the same vehicle
        bool areMatching(const DynamicParams& a_params1, const DynamicParams& a_params2) const;

        // Initialize the static params of the target
        void initializeTarget(vanetza::asn1::Cam cam);

        // Extract the static params from a CAM
        StaticParams getStaticParamsFromCam(vanetza::asn1::Cam cam) const;

        // Extract the dynamic params from a CAM
        DynamicParams getDynamicParamsFromCam(vanetza::asn1::Cam cam) const;

        // Read the dynamic params via the TRACI interface of SUMO
        DynamicParams getDynamicParamsVisually(std::string a_vehicleId) const;

        // Convert a position to a traci-geoposition
        traci::TraCIGeoPosition toTraciGeoPosition(ReferencePosition a_position) const;

        // Get the distance from attacker to target
        double getDistanceToTarget() const;

        // Converts an octet string to a std::string
        std::string toString(OCTET_STRING a_octetString) const;

        // Gets the SUMO simulation time in milliseconds
        long millis() const;

    private:
        Target m_target;
        std::string m_vehicleId;
        std::ofstream m_file;
        int m_interventionCounter = 0;
};

#endif /* MOBCOM_CASERVICE_H_ */
