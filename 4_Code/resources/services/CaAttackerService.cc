/**
 * Implementation of the dynamic attacker model.
 *
 * @author  Julius Bächle (WS22/23)
 * @date    02.01.2023
 */

#include "CaAttackerService.h"
#include "artery/application/Asn1PacketVisitor.h"
#include "artery/envmod/LocalEnvironmentModel.h"
#include "artery/envmod/sensor/FovSensor.h"
#include "artery/traci/VehicleController.h"
#include "vanetza/facilities/cam_functions.hpp"

using namespace artery;
using namespace omnetpp;

Define_Module(CaAttackerService)

/**
 * @brief Computes the square of a value.
 * @author Julius Bächle (WS22/23)
 *
 * @param a Value to square.
 * @returns Square of @p a.
 */
inline double sq(double a) { return a * a; }

/**
 * @brief Destructor used to close open log file.
 * @author Julius Bächle (WS22/23)
 *
 */
CaAttackerService::~CaAttackerService() {
    m_file.close();
}

/**
 * @brief Initializes the dynamic attacker model.
 * @author Julius Bächle (WS22/23)
 *
 */
void CaAttackerService::initialize() {
    ItsG5BaseService::initialize();
    m_vehicleId = getFacilities().get_mutable<traci::VehicleController>().getVehicleId();
    auto& environmentModel = getFacilities().get_const<LocalEnvironmentModel>();
    m_target.id = par("targetId").stringValue();
    initializeLogfile();
}

/**
 * @brief Called on every SUMO simulation step.
 *        The attacker follows the target as long as its still visible.
 * @author Julius Bächle (WS22/23)
 *
 */
void CaAttackerService::trigger() {
    if(isTargetVisible()) {
        log(true, true, m_interventionCounter, m_target.stationID, getDynamicParamsVisually(m_target.id), getDynamicParamsVisually(m_vehicleId));
        followTarget();
    }
}

/**
 * @brief Called when a CAM is received by the dynamic attacker.
 * @author Julius Bächle (WS22/23)
 *
 * @param ind Unused.
 * @param packet Contains the received CAM.
 */
void CaAttackerService::indicate(const vanetza::btp::DataIndication& ind, std::unique_ptr<vanetza::UpPacket> packet) {
    Asn1PacketVisitor<vanetza::asn1::Cam> visitor;
    vanetza::asn1::Cam cam = *boost::apply_visitor(visitor, *packet);
    if (cam->ncam.txRange < getDistanceToTarget())
        return;

    if(!m_target.initialized && toString(cam->ncam.vehicleId) == m_target.id)
        initializeTarget(cam);

    bool staticParamsMatching = m_target.staticParams == getStaticParamsFromCam(cam);
    bool stationIdMatching = m_target.stationID == cam->header.stationID;
    bool dynamicParamsMatching = areMatching(m_target.dynamicParams, getDynamicParamsFromCam(cam));
    bool vehicleMatching = staticParamsMatching && (stationIdMatching || dynamicParamsMatching);
    bool isCorrectVehicle = cam->ncam.serviceId == m_target.serviceId;

    if (isTargetVisible() && (vehicleMatching != isCorrectVehicle)) {
        vehicleMatching = isCorrectVehicle;
        m_interventionCounter++;
    }

    if (vehicleMatching) {
        m_target.stationID = cam->header.stationID;
        m_target.dynamicParams = getDynamicParamsFromCam(cam);

        if (!isTargetVisible()) {
            log(false, isCorrectVehicle, m_interventionCounter, m_target.stationID, m_target.dynamicParams, getDynamicParamsVisually(m_vehicleId));
            followTarget();
        }
    }
}

/**
 * @brief Checks whether the target is visible according to the artery environment model.
 * @author Julius Bächle (WS22/23)
 *
 * @returns True if target is visible; otherwise false.
 */
bool CaAttackerService::isTargetVisible() const {
    auto& environmentModel = getFacilities().get_const<LocalEnvironmentModel>();
    FovSensor* sight = (FovSensor*) environmentModel.getSensors()[0];
    auto objects = sight->detectObjects().objects;
    for (std::shared_ptr<EnvironmentModelObject> object : objects)
        if(object->getExternalId() == m_target.id)
            return true;
    return false;
}

/**
 * @brief Tries to follow the target by setting its road as destination.
 *        In case it cannot be set, it tries to set the next road (mainly in intersections).
 *        When we are driving on the same road as the target we also drive in the same lane.
 * @author Julius Bächle (WS22/23)
 */
void CaAttackerService::followTarget() const {
    auto& vehicle_api = getFacilities().get_mutable<traci::VehicleController>().getTraCI()->vehicle;
    auto targetRoad = vehicle_api.getRoadID(m_target.id);
    auto route = vehicle_api.getRoute(m_target.id);
    auto routeIdx = vehicle_api.getRouteIndex(m_target.id);

    try {
        if(std::find(route.begin(), route.end(), targetRoad) != route.end()) {
            vehicle_api.changeTarget(m_vehicleId, targetRoad);
        } else if(routeIdx + 1 < route.size()) {
            targetRoad = route[routeIdx + 1];
            vehicle_api.changeTarget(m_vehicleId, targetRoad);
        }
    } catch(...) {}

    if(targetRoad == vehicle_api.getRoadID(m_vehicleId))
        vehicle_api.changeLane(m_vehicleId, vehicle_api.getLaneIndex(m_target.id), 1.0);
}

/**
 * @brief   Checks whether two CAMs may belong to the same vehicle.
 * @details It is assumed that the vehicle drives half the difference time with the data of the
 *          first CAM and half the difference time with the data of the second CAM.
 *          The calculated position and heading are compared to the actual data in the second CAM.
 *          See the Wiki for an illustration.
 * @author Julius Bächle (WS22/23)
 *
 * @param a_params1 Dynamic parameters of the first CAM that is compared.
 * @param a_params2 Dynamic parameters of the second CAM that is compared.
 * @returns True if both CAMs belong to the same vehicle; otherwise false.
 */
bool CaAttackerService::areMatching(const DynamicParams& a_params1, const DynamicParams& a_params2) const {
    double timeDiffS = (a_params2.timestampMs - a_params1.timestampMs) / 1000.0;

    const double HEADING_TOLERANCE = 30.0;
    double yawDiff1 = 0.5 * timeDiffS * a_params1.yawRateCdgs / 100;
    double yawDiff2 = 0.5 * timeDiffS * a_params2.yawRateCdgs / 100;
    double estimatedYaw = -(a_params1.headingDg / 10) + yawDiff1 + yawDiff2;
    double actualYaw = -(a_params2.headingDg / 10);
    bool headingMatching = abs(estimatedYaw - actualYaw) < HEADING_TOLERANCE || abs(estimatedYaw - actualYaw) > 3600 - HEADING_TOLERANCE;

    const double DISTANCE_TOLERANCE = 2.0;
    double dist1 = 0.5 * timeDiffS * a_params1.speedCms / 100;
    double dist2 = 0.5 * timeDiffS * a_params2.speedCms / 100;
    double heading1 = (-a_params1.headingDg / 10.0) * (PI / 180.0) + (PI / 2);
    double heading2 = (-a_params2.headingDg / 10.0) * (PI / 180.0) + (PI / 2);

    auto traciApi = getFacilities().get_mutable<traci::VehicleController>().getTraCI();
    traci::TraCIPosition start = traciApi->convert2D(a_params1.position);
    traci::TraCIPosition end = traciApi->convert2D(a_params2.position);
    double estimatedPosX = start.x + cos(heading1) * dist1 + cos(heading2) * dist2;
    double estimatedPosY = start.y + sin(heading1) * dist1 + sin(heading2) * dist2;
    bool positionMatching = sq(estimatedPosX - end.x) + sq(estimatedPosY - end.y) <= sq(DISTANCE_TOLERANCE);

    return headingMatching && positionMatching;
}

/**
 * @brief Initializes the target (e.g. static parameters) with the first received CAM from the target.
 * @author Julius Bächle (WS22/23)
 *
 * @param cam CAM used to initialize the target.
 */
void CaAttackerService::initializeTarget(vanetza::asn1::Cam cam) {
    m_target.stationID = cam->header.stationID;
    m_target.serviceId = cam->ncam.serviceId;
    m_target.staticParams = getStaticParamsFromCam(cam);
    m_target.dynamicParams = getDynamicParamsFromCam(cam);
    m_target.initialized = true;
}

/**
 * @brief Returns the static parameters of a CAM.
 * @author Julius Bächle (WS22/23)
 *
 * @param cam The CAM which to get the static parameters from.
 * @returns Static parameters of @p cam.
 */
StaticParams CaAttackerService::getStaticParamsFromCam(vanetza::asn1::Cam cam) const {
    auto bvc = cam->cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency;
    StaticParams params;
    params.length = bvc.vehicleLength.vehicleLengthValue;
    params.width  = bvc.vehicleWidth;
    params.stationType = cam->cam.camParameters.basicContainer.stationType;
    return params;
}

/**
 * @brief Returns the dynamic parameters of a CAM.
 * @author Julius Bächle (WS22/23)
 *
 * @param cam The CAM which to get the dynamic parameters from.
 * @return Dynamic parameters of @p cam.
 */
DynamicParams CaAttackerService::getDynamicParamsFromCam(vanetza::asn1::Cam cam) const {
    auto bvc = cam->cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency;
    DynamicParams params;
    params.headingDg = bvc.heading.headingValue;
    params.speedCms = bvc.speed.speedValue;
    params.yawRateCdgs = bvc.yawRate.yawRateValue;
    params.position = toTraciGeoPosition(cam->cam.camParameters.basicContainer.referencePosition);
    params.timestampMs = millis();
    return params;
}

/**
 * @brief Converts a ReferencePosition of a CAM to a SUMO TraCIGeoPosition format.
 * @author Julius Bächle (WS22/23)
 *
 * @param a_position Position to convert.
 * @returns SUMO position format.
 */
traci::TraCIGeoPosition CaAttackerService::toTraciGeoPosition(ReferencePosition a_position) const {
    traci::TraCIGeoPosition geoPos;
    geoPos.latitude = a_position.latitude / (double) 10000000;
    geoPos.longitude = a_position.longitude / (double) 10000000;
    return geoPos;
}

/**
 * @brief Returns the dynamic parameters of a vehicle via the TraciApi out of SUMO.
 * @author Julius Bächle (WS22/23)
 *
 * @param a_vehicleId SUMO Id of vehicle from which to get the dynamic parameters from.
 * @return Dynamic parameters provided by SUMO.
 */
DynamicParams CaAttackerService::getDynamicParamsVisually(std::string a_vehicleId) const {
    auto traciApi = getFacilities().get_mutable<traci::VehicleController>().getTraCI();
    DynamicParams params;
    params.speedCms = traciApi->vehicle.getSpeed(a_vehicleId) * 100;
    params.headingDg = traciApi->vehicle.getAngle(a_vehicleId) * 10;
    params.yawRateCdgs = (long) ((100 * 180 / PI) * getFacilities().get_const<artery::VehicleDataProvider>().yaw_rate().value());
    params.position = traciApi->convertGeo(traciApi->vehicle.getPosition(a_vehicleId));
    params.timestampMs = millis();
    return params;
}

/**
 * @brief Calculates the distance from attacker to target.
 * @author Julius Bächle (WS22/23)
 *
 * @return Distance to target in meters.
 */
double CaAttackerService::getDistanceToTarget() const {
    auto traciApi = getFacilities().get_mutable<traci::VehicleController>().getTraCI();
    auto pos1 = traciApi->vehicle.getPosition(m_vehicleId);
    auto pos2 = traciApi->vehicle.getPosition(m_target.id);
    double dist = traciApi->simulation.getDistance2D(pos1.x, pos1.y, pos2.x, pos2.y);
    return dist;
}

/**
 * @brief Converts an octet string to C++ string.
 * @author Julius Bächle (WS22/23)
 *
 * @param a_octetString Octet string to convert.
 * @return Octet string as C++ string.
 */
std::string CaAttackerService::toString(OCTET_STRING a_octetString) const {
    char buffer [128];
    vanetza::facilities::print_octet_string(a_octetString, buffer, sizeof(buffer));
    return buffer;
}

/**
 * @brief Returns the SUMO simulation time.
 * @author Julius Bächle (WS22/23)
 *
 * @return SUMO simulation time in milliseconds.
 */
long CaAttackerService::millis() const {
    auto traciApi = getFacilities().get_mutable<traci::VehicleController>().getTraCI();
    return traciApi->simulation.getTime() * 1000;
}

/**
 * @brief Compares two static parameters with each other.
 * @author Julius Bächle (WS22/23)
 *
 * @param a_cmp
 * @returns True if static parameters are equal; otherwise false.
 */
bool StaticParams::operator== (const StaticParams& a_cmp) const {
    return length == a_cmp.length && width == a_cmp.width && stationType == a_cmp.stationType;
}

/**
 * @brief Opens a log file and writes CSV header to it.
 * @author Julius Bächle (WS22/23)
 *
 */
void CaAttackerService::initializeLogfile() {
    m_file.open(par("logfile").stringValue(), std::ios::trunc);
    m_file << "Timestamp,TargetVisible,CorrectVehicle,VisualInterventions,Pseudonym,"
              "TargetLatitude,TargetLongitude,TargetSpeed,TargetHeading,TargetYawRate,"
              "AttackerLatitude,AttackerLongitude,AttackerSpeed,AttackerHeading,AttackerYawRate";
    m_file << std::endl;
}

/**
 * @brief Writes en entry into the log file.
 * @author Julius Bächle (WS22/23)
 *
 * @param a_targetVisible Target visible is visible.
 * @param a_correctVehicle Attacker follows correct vehicle.
 * @param a_interventionCounter Number of corrections the algorithm needed to do.
 * @param a_pseudonym The pseudonym of the vehicle the attacker is following.
 * @param a_targetParams The dynamic parameters of the target.
 * @param a_attackerParams The dynamic parameters of the attacker.
 */
void CaAttackerService::log(bool a_targetVisible, bool a_correctVehicle, int a_interventionCounter, uint32_t a_pseudonym, const DynamicParams& a_targetParams, const DynamicParams& a_attackerParams) {
    m_file << millis() << ",";
    m_file << a_targetVisible << ",";
    m_file << a_correctVehicle << ",";
    m_file << a_interventionCounter << ",";
    m_file << a_pseudonym << ",";
    m_file << (long)(a_targetParams.position.latitude * 10000000) << ",";
    m_file << (long)(a_targetParams.position.longitude * 10000000) << ",";
    m_file << a_targetParams.speedCms << ",";
    m_file << a_targetParams.headingDg << ",";
    m_file << a_targetParams.yawRateCdgs << ",";
    m_file << (long)(a_attackerParams.position.latitude * 10000000) << ",";
    m_file << (long)(a_attackerParams.position.longitude * 10000000) << ",";
    m_file << a_attackerParams.speedCms << ",";
    m_file << a_attackerParams.headingDg << ",";
    m_file << a_attackerParams.yawRateCdgs << "\n";
}
