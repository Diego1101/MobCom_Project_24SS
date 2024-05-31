////////////////////////////////////////////////////////////////////////////////
// Header file for the HW agent class; representing an ITS vehicle service.   //
// This service behaves like a connector to external hardware: If the vehicle //
// receives any packets in the simulation, this service sends duplicates to   //
// an external endpoint via UDP (format: Cohda data request). Additionally,   //
// if packets arrive via UDP (format: Cohda data indication), they get        //
// broadcasted into the simulation.                                           //
//                                                                            //
// @file    HWAgent.hpp                                                       //
// @author  Manuel Haerer                                                     //
// @date    04.01.2022                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef __HWAGENT_H_
#define __HWAGENT_H_

#include "artery/application/ItsG5PromiscuousService.h"
#include "artery/traci/VehicleController.h"
#include "artery/utility/AsioTaskUDP.hpp"

#include "CohdaDataRequest.hpp"
#include "CohdaDataIndication.hpp"

#include <tuple>

class HWAgent : public artery::ItsG5PromiscuousService
{
public:
    HWAgent();
    virtual ~HWAgent();

    // Special method of the promiscuous service: It gets called whenever the
    // vehicle receives a packet. All packets are duplicated and sent via a
    // Cohda data request.
    virtual void tap(
        const vanetza::btp::DataIndication&,
        const vanetza::UpPacket&,
        const artery::NetworkInterface&) override;

    // For handling simulation level events (so called "signals"). Used for
    // calling the "moveToXY" function (SUMO API) in EVERY simulation step.
    virtual void receiveSignal(
        omnetpp::cComponent*,
        omnetpp::simsignal_t,
        const omnetpp::SimTime&,
        omnetpp::cObject*) override;

protected:
    virtual void initialize() override;
    virtual void finish() override;

    // OMNeT++ level method; for direct communication between modules (without
    // the Artery stack). Used for receiving Cohda data indications.
    virtual void handleMessage(omnetpp::cMessage*) override;

private:
    Cohda::DataRequestHeader createCohdaDataReq(
        const vanetza::btp::DataIndication&,
        uint16_t) const;

    vanetza::btp::DataRequestB createVanetzaDataReq(
        const Cohda::DataIndicationHeader&) const;

    void updateAgentPosition(vanetza::UpPacket&);
    std::tuple<double, double> convertGeoToCart(double, double) const;

    std::unique_ptr<vanetza::geonet::DownPacket> convertToCam(
        vanetza::ByteBufferConvertible) const;

    vanetza::byte_view_range convertToCamo(vanetza::UpPacket&) const;

    traci::VehicleController* controller = nullptr;

    // Flag for the call "moveToXY" (SUMO API); see SUMO documentation.
    int keepRouteFlag = 6;

    struct HWPositionState
    {
        double xPos = 0.0;
        double yPos = 0.0;
        double heading = 0.0;
        double elevation = 0.0;
        double speed = 0.0;
    } currentState;

    std::unique_ptr<artery::AsioTaskUDP> asioTask;

    // If true, the ITS-AID will get set from the destination port (assuming
    // the usage of well-known service ports) if the ITS-AID is not available
    // from the data indication; used for Cohda data requests.
    bool useCohdaPortClassification = false;
};

#endif