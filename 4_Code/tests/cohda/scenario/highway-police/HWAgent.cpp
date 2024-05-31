////////////////////////////////////////////////////////////////////////////////
// Main file for the HW agent class; representing an ITS vehicle service.     //
// This service behaves like a connector to external hardware: If the vehicle //
// receives any packets in the simulation, this service sends duplicates to   //
// an external endpoint via UDP (format: Cohda data request). Additionally,   //
// if packets arrive via UDP (format: Cohda data indication), they get        //
// broadcasted into the simulation.                                           //
//                                                                            //
// @file    HWAgent.cpp                                                       //
// @author  Manuel Haerer                                                     //
// @date    04.01.2022                                                        //
////////////////////////////////////////////////////////////////////////////////

#include "artery/application/Asn1PacketVisitor.h"
#include "artery/utility/AsioSchedulerUDP.hpp"
#include "vanetza/net/packet_variant.hpp"
#include "vanetza/asn1/camo.hpp"
#include "vanetza/asn1/cam.hpp"

#include "HWAgent.hpp"

Define_Module(HWAgent)

static const omnetpp::simsignal_t sumoInit =
    omnetpp::cComponent::registerSignal("traci.init");
static const omnetpp::simsignal_t sumoStep =
    omnetpp::cComponent::registerSignal("traci.step");

HWAgent::HWAgent()
{
}

HWAgent::~HWAgent()
{
}

// Special method of the promiscuous service: It gets called whenever the
// vehicle receives a packet. All packets are duplicated and sent via a Cohda
// data request.
void HWAgent::tap(
    const vanetza::btp::DataIndication& indication,
    const vanetza::UpPacket& packet,
    const artery::NetworkInterface& nwInterface)
{
    Enter_Method("tap");
    
    vanetza::UpPacket up(packet);
    
    // Convert to standard conforming CAM if necessary.
    auto bv = convertToCamo(up);
    auto drh = createCohdaDataReq(indication, bv.size());
    
    std::vector<boost::asio::const_buffer> bfs;
    auto& hdrSer = drh.serialize();
    
    bfs.push_back(boost::asio::const_buffer(hdrSer.data(), hdrSer.size()));
    bfs.push_back(boost::asio::const_buffer(bv.data(), bv.size()));

    try
    {
        asioTask->write(bfs);
    }
    catch(const std::exception& e)
    {
        EV_ERROR << "Failed to send UDP data request: " << e.what() << "\n";
    }
}

// For handling simulation level events (so called "signals"). Used for calling
// the "moveToXY" function (SUMO API) in EVERY simulation step.
void HWAgent::receiveSignal(
    omnetpp::cComponent* source,
    omnetpp::simsignal_t signalID,
    const omnetpp::SimTime& t,
    omnetpp::cObject* details)
{
    Enter_Method("receiveSignal");
    
    bool isSumoInit = signalID == sumoInit;
    bool isSumoStep = signalID == sumoStep;

    if (isSumoInit || isSumoStep)
    {
        try
        {
            auto vehicleId = controller->getVehicleId();
            auto traciApi = controller->getTraCI();
            auto& vehicleApi = traciApi->vehicle;

            if (isSumoInit)
            {
                currentState = HWPositionState();
            }

            // Force the vehicle to a specific position. For that, the "keep
            // route flag" should be set to 6. This function must be called
            // in EVERY simulation step in order to avoid unintended route
            // movement or vehicle removal. These calls set the vehicle 'on
            // rails' (also see https://github.com/eclipse/sumo/issues/3993).
            vehicleApi.moveToXY(
                vehicleId,
                "",
                -1,
                currentState.xPos,
                currentState.yPos,
                currentState.heading,
                keepRouteFlag);

            vehicleApi.setSpeed(vehicleId, currentState.speed);
        }
        catch(const std::exception& e)
        {
            EV_ERROR << "An error occured while updating the position of the "
                "\"HWAgent\"; details: " << e.what() << "\n";
        }
    }
}

void HWAgent::initialize()
{
    ItsG5PromiscuousService::initialize();

    controller = &getFacilities().get_mutable<traci::VehicleController>();
    keepRouteFlag = 6;

    try
    {
        auto& krfPar = par("keepRouteFlag");

        if (krfPar.getType() == omnetpp::cPar::Type::INT &&
            krfPar.intValue() >= 0 && krfPar.intValue() <= 7)
        {
            keepRouteFlag = krfPar.intValue();
        }
        else
        {
            EV_WARN << "The parameter \"keepRouteFlag\" has a wrong data type "
                "or a wrong value. Assuming default...\n";
        }
    }
    catch (const std::exception& e)
    {
        EV_WARN << "The parameter \"keepRouteFlag\" could not be obtained; "
            "reason: " << e.what() << " Assuming default...\n";
    }

    try
    {
        auto& cpcPar = par("useCohdaPortClassification");

        if (cpcPar.getType() == omnetpp::cPar::Type::BOOL)
        {
            useCohdaPortClassification = cpcPar.boolValue();
        }
        else
        {
            EV_WARN << "The parameter \"useCohdaPortClassification\" has a "
                "wrong data type. Assuming default...\n";
        }
    }
    catch (const std::exception& e)
    {
        EV_WARN << "The parameter \"useCohdaPortClassification\" could not be "
            "obtained; reason: " << e.what() << " Assuming default...\n";
    }

    // IMPORTANT: This service can only be used if the ASIO scheduler (UDP
    // version) is selected via the INI file.
    auto scheduler = omnetpp::check_and_cast<artery::AsioSchedulerUDP*>(
        getSimulation()->getScheduler());

    try
    {
        std::string lipStr = par("localIP").stringValue();
        boost::system::error_code ec;
        
        auto lip = boost::asio::ip::address_v4::from_string(lipStr, ec);

        if (ec)
        {
            throw omnetpp::cRuntimeError("The local IP address \"%s\" could not"
                " be parsed.", lipStr.c_str());
        }
        
        boost::asio::ip::udp::endpoint lep;
        lep.address(lip);
        lep.port(par("localPort").intValue());
        
        asioTask = scheduler->createTask(*this, &lep);
    }
    catch(const std::exception& e)
    {
        EV_WARN << "Could not use local binding data (IP, port); reason: " <<
            e.what() << " Using default...\n";

        asioTask = scheduler->createTask(*this);
    }

    boost::asio::ip::udp::endpoint rep;
    
    try
    {
        std::string ripStr = par("remoteIP").stringValue();
        boost::system::error_code ec;
        
        auto rip = boost::asio::ip::address_v4::from_string(ripStr, ec);

        if (ec)
        {
            throw omnetpp::cRuntimeError("The remote IP address \"%s\" could "
                "not be parsed.", ripStr.c_str());
        }

        rep.address(rip);
        rep.port(par("remotePort").intValue());
    }
    catch(const std::exception& e)
    {
        EV_WARN << "Could not use remote binding data (IP, port); reason: " <<
            e.what() << " Using default...\n";

        rep.address(boost::asio::ip::address_v4::from_string("127.0.0.1"));
        rep.port(4401);
    }
    
    try
    {
        asioTask->connect(rep);
    }
    catch(const std::exception& e)
    {
        throw omnetpp::cRuntimeError("\"HWAgent\" service failed to connect to "
            "remote endpoint; details: %s", e.what());
    }

    // Can't use internal "subscribe" because the TRACI signal would not get
    // forwarded to this module (signals are only propagated to superordinate
    // modules; this module is not a superordinate module of the TRACI module).
    omnetpp::getSimulation()->getSystemModule()->subscribe(sumoInit, this);
    omnetpp::getSimulation()->getSystemModule()->subscribe(sumoStep, this);
}

void HWAgent::finish()
{
    // Can't use internal "unsubscribe"; see reasoning for "subscribe".
    omnetpp::getSimulation()->getSystemModule()->unsubscribe(sumoInit, this);
    omnetpp::getSimulation()->getSystemModule()->unsubscribe(sumoStep, this);

    controller = nullptr;
    keepRouteFlag = 6;
    asioTask = nullptr;
    useCohdaPortClassification = false;

    ItsG5PromiscuousService::finish();
}

// OMNeT++ level method; for direct communication between modules (without the
// Artery stack). Used for receiving Cohda data indications.
void HWAgent::handleMessage(omnetpp::cMessage* dataMsg)
{
    Enter_Method("handleMessage");
    
    if (dataMsg == asioTask->getDataMessage())
    {
        auto udpDataMsg = (AsioDataUDP*)dataMsg;

        auto& buffer = udpDataMsg->getBuffer();
        auto length = udpDataMsg->getLength();

        Cohda::DataIndicationHeader dih;

        if (length < Cohda::DataIndicationHeader::getHeaderSize())
        {
            EV_ERROR << "\"HWAgent\" received an invalid data indication "
                "message; unexpected length (" << length << " byte).\n";
        }
        else
        {
            std::vector<uint8_t> hdrVec(
                buffer.begin(),
                buffer.begin() + Cohda::DataIndicationHeader::getHeaderSize());
            
            if (!dih.deserialize(hdrVec))
            {
                EV_ERROR << "\"HWAgent\" received an invalid data indication "
                    "message; parsing failed.\n";
            }
            else
            {
                std::vector<uint8_t> plVec(
                    buffer.begin() +
                        Cohda::DataIndicationHeader::getHeaderSize(),
                    buffer.begin() + length);

                EV_INFO << "\"HWAgent\" received a valid data indication "
                    "message (payload size: " << plVec.size() << " byte); "
                    "sending it into the simulation...\n";

                // Convert to simulation CAM if necessary.
                auto dp = convertToCam(std::move(plVec));

                vanetza::UpPacket up(*dp);
                updateAgentPosition(up);
                
                request(createVanetzaDataReq(dih), std::move(dp));
            }
        }

        // Signal scheduler that we are ready to handle further data.
        asioTask->handleNext();
    }
}

Cohda::DataRequestHeader HWAgent::createCohdaDataReq(
    const vanetza::btp::DataIndication& indication,
    uint16_t payloadSize) const
{
    Cohda::DataRequestHeader dataRequest;

    dataRequest.type = Cohda::BTPType::TP_B;
    
    if (indication.its_aid.is_initialized())
    {
        dataRequest.securityITSAID =
            (Cohda::GNSecurityITSAID)indication.its_aid.get();
    }
    else if (useCohdaPortClassification)
    {
        // Get ITS-AID from well-known service-ports according to ETSI TS 103
        // 248 V2.1.1 because no ITS-AID is provided.
        switch (indication.destination_port.host())
        {
        case 2001:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_CAM;
            break;

        case 2002:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_DENM;
            break;

        case 2003:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_MAP;
            break;

        case 2004:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_SPAT;
            break;

        case 2005:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_SAEM;
            break;

        case 2006:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_IVI;
            break;

        case 2009:
            dataRequest.securityITSAID = Cohda::GNSecurityITSAID::AID_CPM;
            break;
        
        default:
            EV_WARN << "Creating a Cohda data request which contains an invalid"
                " ITS-AID (the default value 0 is used; unhandled application "
                "port).\n";
            
            break;
        }
    }
    else
    {
        EV_WARN << "Creating a Cohda data request which contains an invalid "
            "ITS-AID (the default value 0 is used; unknown application).\n";
    }
    
    switch (dataRequest.securityITSAID)
    {
        // Note that for e. g. CPM, no packet transport mode was found in
        // according standards. Thus, this mapping is not complete.

        case Cohda::GNSecurityITSAID::AID_CAM:
        case Cohda::GNSecurityITSAID::AID_SAEM:
            dataRequest.packetTransport =
                Cohda::GNPacketTransport::PT_SingleHopBroadcast;
            break;

        case Cohda::GNSecurityITSAID::AID_DENM:
        case Cohda::GNSecurityITSAID::AID_MAP:
        case Cohda::GNSecurityITSAID::AID_SPAT:
        case Cohda::GNSecurityITSAID::AID_IVI:
            dataRequest.packetTransport =
                Cohda::GNPacketTransport::PT_GeoBroadCast;
            break;

        default:
            EV_WARN << "Creating a Cohda data request which contains an invalid"
                " packet transport value (the default value 0 is used). This "
                "might also be caused by the fact that the packet transport "
                "value is not mapped for every service (not implemented).\n";
    }

    dataRequest.trafficClass =
        (Cohda::GNTrafficClass)indication.traffic_class.raw();

    if (indication.remaining_packet_lifetime.is_initialized())
    {
        dataRequest.maxPacketLifetime =
            indication.remaining_packet_lifetime.get().decode() /
                vanetza::units::si::seconds;
    }

    dataRequest.destinationPort = indication.destination_port.host();

    if (indication.destination_port_info.is_initialized())
    {
        dataRequest.destinationPortInfo =
            indication.destination_port_info.get().host();
    }

    vanetza::geonet::DestinationVariant dest;

    if (dest.type() == typeid(vanetza::geonet::Area))
    {
        auto& area = boost::get<vanetza::geonet::Area>(dest);
        
        // Unit: 1/10 Microdegrees.
        dataRequest.destination.latitude =
            area.position.latitude.value() * 1000000.0 * 10.0;

        // Unit: 1/10 Microdegrees.
        dataRequest.destination.longitude =
            area.position.longitude.value() * 1000000.0 * 10.0;

        dataRequest.destination.angle = area.angle.value();

        if (area.shape.type() == typeid(vanetza::geonet::Rectangle))
        {
            auto& rect = boost::get<vanetza::geonet::Rectangle>(area.shape);

            dataRequest.destination.distanceA = rect.a.value();
            dataRequest.destination.distanceB = rect.b.value();
            dataRequest.destination.shape = Cohda::GNShape::SH_Rectangle;

        }
        else if (area.shape.type() == typeid(vanetza::geonet::Ellipse))
        {
            auto& ell = boost::get<vanetza::geonet::Ellipse>(area.shape);

            dataRequest.destination.distanceA = ell.a.value();
            dataRequest.destination.distanceB = ell.b.value();
            dataRequest.destination.shape = Cohda::GNShape::SH_Ellipse;
        }
        else if (area.shape.type() == typeid(vanetza::geonet::Circle))
        {
            auto& cir = boost::get<vanetza::geonet::Circle>(area.shape);

            dataRequest.destination.distanceA = cir.r.value();
            dataRequest.destination.distanceB = 0;
            dataRequest.destination.shape = Cohda::GNShape::SH_Circle;
        }
        else
        {
            EV_WARN << "Creating a Cohda data request which contains a default "
                "GeoNet destination header (0 values are used; found invalid"
                "shape value).\n";
        }
    }
    else
    {
        EV_WARN << "Creating a Cohda data request which contains a default "
            "GeoNet header (0 values are used; found no GeoNet header).\n";
    }

    dataRequest.commsProfile = Cohda::GNCommsProfile::CP_G5;
    dataRequest.repeatInterval = 0;

    if (indication.permissions.is_initialized())
    {
        dataRequest.securityProfile = Cohda::GNSecurityProfile::SP_Enabled;
        
        if (indication.permissions.get().size() > dataRequest.secSSPBits.size())
        {
            EV_WARN << "Creating a Cohda data request which contains a default "
                "SSP array (0 values are used; permission bit array is larger "
                "than expected).\n";
        }
        else
        {
            dataRequest.secSSPBitsLength = indication.permissions.get().size();

            std::copy_n(
                indication.permissions.get().begin(),
                indication.permissions.get().size(),
                dataRequest.secSSPBits.begin());
        }
    }
    
    dataRequest.dataLength = payloadSize;

    return std::move(dataRequest);
}

vanetza::btp::DataRequestB HWAgent::createVanetzaDataReq(
        const Cohda::DataIndicationHeader& indication) const
{
    vanetza::btp::DataRequestB dataRequest;

    dataRequest.destination_port =
        vanetza::btp::port_type(indication.destinationPort);

    dataRequest.destination_port_info =
        vanetza::uint16be_t(indication.destinationPortInfo);

    dataRequest.gn.communication_profile =
        vanetza::geonet::CommunicationProfile::ITS_G5;

    vanetza::geonet::Area dv;

    // Unit: 1/10 Microdegrees.
    dv.position.latitude =
        vanetza::units::GeoAngle::from_value(
            ((double)indication.destination.latitude) / 1000000.0 / 10.0);

    // Unit: 1/10 Microdegrees.
    dv.position.longitude =
        vanetza::units::GeoAngle::from_value(
            ((double)indication.destination.longitude) / 1000000.0 / 10.0);

    dv.angle = vanetza::units::Angle::from_value(indication.destination.angle);

    switch (indication.destination.shape)
    {
        case Cohda::GNShape::SH_Circle:
        {
            vanetza::geonet::Circle cir;
            cir.r = vanetza::units::Length::from_value(
                indication.destination.distanceA);

            dv.shape = cir;
            break;
        }

        case Cohda::GNShape::SH_Ellipse:
        {
            vanetza::geonet::Ellipse ell;

            ell.a = vanetza::units::Length::from_value(
                indication.destination.distanceA);
            ell.b = vanetza::units::Length::from_value(
                indication.destination.distanceB);

            dv.shape = ell;
            break;
        }

        case Cohda::GNShape::SH_Rectangle:
        {
            vanetza::geonet::Rectangle rec;

            rec.a = vanetza::units::Length::from_value(
                indication.destination.distanceA);
            rec.b = vanetza::units::Length::from_value(
                indication.destination.distanceB);

            dv.shape = rec;
            break;
        }

        default:
            EV_WARN << "Creating a Vanetza data request which contains an "
                "uninitialized shape in the GeoNet header (found unexpected"
                " shape value in the Cohda data indication).\n";

            break;
    }

    dataRequest.gn.destination = dv;

    dataRequest.gn.its_aid = indication.securityITSAID;

    vanetza::geonet::Lifetime lt;
    lt.encode(vanetza::units::Duration::from_value(
        indication.maxPacketLifetime));

    dataRequest.gn.maximum_lifetime = lt;

    vanetza::geonet::TrafficClass tc(indication.trafficClass);

    dataRequest.gn.traffic_class = tc;

    // Note that this explicit mapping is necessary because Cohda seems to use
    // a different representation for the packet transport compared to Vanetza.
    switch (indication.packetTransport)
    {
    case Cohda::GNPacketTransport::PT_GeoBroadCast:
        dataRequest.gn.transport_type = vanetza::geonet::TransportType::GBC;
        break;

    case Cohda::GNPacketTransport::PT_GeoUniCast:
        dataRequest.gn.transport_type = vanetza::geonet::TransportType::GUC;
        break;
    
    default:
        EV_WARN << "Creating a Vanetza data request which contains a default "
            "transport type in the GeoNet header (found unexpected packet "
            "transport type in the Cohda data indication).\n";

    case Cohda::GNPacketTransport::PT_SingleHopBroadcast:
        dataRequest.gn.transport_type = vanetza::geonet::TransportType::SHB;
        break;
    }
    
    // Note that "dataRequest.gn.maximum_hop_limit" and
    // "dataRequest.gn.repetition" are optional and thus not set.

    return std::move(dataRequest);
}

void HWAgent::updateAgentPosition(vanetza::UpPacket& dp)
{
    artery::Asn1PacketVisitor<vanetza::asn1::Cam> visitor;
	const vanetza::asn1::Cam* cam = boost::apply_visitor(visitor, dp);

    if (cam && cam->validate())
    {
        auto& bc = (*cam)->cam.camParameters.basicContainer.referencePosition;
        auto& hfc = (*cam)->cam.camParameters.highFrequencyContainer.choice.
            basicVehicleContainerHighFrequency;

        // Units according to ETSI TS 102 637-3.

        auto lat = (double)bc.latitude / 1000000.0 / 10.0;
        auto lng = (double)bc.longitude / 1000000.0 / 10.0;

        auto alt = (double)bc.altitude.altitudeValue / 100.0;
        auto hd = (double)hfc.heading.headingValue / 10.0;
        auto spd = (double)hfc.speed.speedValue / 100.0;

        EV_INFO << "Update \"HWAgent\" position: LAT: " << lat << " / LNG: " <<
            lng << " / ALT: " << alt << " / HDG: " << hd << " / SPD: " << spd <<
            "\n";

        auto cart = convertGeoToCart(lat, lng);
        
        currentState.xPos = std::get<0>(cart);
        currentState.yPos = std::get<1>(cart);

        currentState.heading = hd;
        currentState.elevation = alt;
        currentState.speed = spd;
    }
    else
    {
        EV_WARN << "\"HWAgent\" could not update its position because the "
            "received payload is not a valid CAM.\n";
    }
}

std::tuple<double, double> HWAgent::convertGeoToCart(
    double lat,
    double lng) const
{
    auto traciApi = controller->getTraCI();
    auto& simulationApi = traciApi->simulation;
    
    // Note that x = longitude and y = latitude. Normally, one would expect the
    // order to be the other way around. Note that this is not documented
    // properly. It took me AGES of debugging to find this out... Also: This
    // only works if the SUMO NET-file provides valid location data (using the
    // tag "<location>"; see SUMO documentation)
    auto pos = simulationApi.convertGeo(lng, lat, true);
    
    auto boundary = simulationApi.getNetBoundary();
    
    if (pos.x < boundary.value[0].x)
    {
        EV_WARN << "Calculated \"HWAgent\" position is outside the boundary ("
            << pos.x << "); limiting to lower X-bound...\n";
        
        pos.x = boundary.value[0].x;
    }
    else if (pos.x > boundary.value[1].x)
    {
        EV_WARN << "Calculated \"HWAgent\" position is outside the boundary ("
            << pos.x << "); limiting to upper X-bound...\n";
        
        pos.x = boundary.value[1].x;
    }

    if (pos.y < boundary.value[0].y)
    {
        EV_WARN << "Calculated \"HWAgent\" position is outside the boundary ("
            << pos.y << "); limiting to lower Y-bound...\n";
        
        pos.y = boundary.value[0].y;
    }
    else if (pos.y > boundary.value[1].y)
    {
        EV_WARN << "Calculated \"HWAgent\" position is outside the boundary ("
            << pos.y << "); limiting to upper Y-bound...\n";
        
        pos.y = boundary.value[1].y;
    }

    return std::tuple<double, double>(pos.x, pos.y);
}

// This function is necessary to convert a standard conforming CAM, coming from
// external HW, to the CAM structure that is used in the simulation.
std::unique_ptr<vanetza::geonet::DownPacket> HWAgent::convertToCam(
    vanetza::ByteBufferConvertible bbc) const
{
    std::unique_ptr<vanetza::geonet::DownPacket> dp
        { new vanetza::geonet::DownPacket };
    
    dp->layer(vanetza::OsiLayer::Application) = bbc;
    vanetza::geonet::UpPacket up(*dp);

    artery::Asn1PacketVisitor<vanetza::asn1::Camo> visitor;
	const vanetza::asn1::Camo* camo = boost::apply_visitor(visitor, up);

    if (camo && camo->validate())
    {
        auto c1 = vanetza::asn1::copy(asn_DEF_ItsPduHeader, &((*camo)->header));
        auto c2 = vanetza::asn1::copy(asn_DEF_CoopAwareness, &((*camo)->cam));

        vanetza::asn1::Cam cam;

        cam->header = *(ItsPduHeader_t*)c1;
        cam->cam = *(CoopAwareness_t*)c2;

        // Just reset additional CAM data (not available from external HW).
        cam->ncam.serviceId = 0;
        cam->ncam.vehicleId.buf = nullptr;
        cam->ncam.vehicleId.size = 0;

        dp.reset(new vanetza::geonet::DownPacket);
        dp->layer(vanetza::OsiLayer::Application) = std::move(cam);
    }

    return dp;
}

// This function is necessary to convert a simulation CAM to a standard
// conforming CAM which will be sent to external HW.
vanetza::byte_view_range HWAgent::convertToCamo(vanetza::UpPacket& up) const
{
    artery::Asn1PacketVisitor<vanetza::asn1::Cam> visitor;
	const vanetza::asn1::Cam* cam = boost::apply_visitor(visitor, up);
    
    if (cam && cam->validate())
    {
        auto c1 = vanetza::asn1::copy(asn_DEF_ItsPduHeader, &((*cam)->header));
        auto c2 = vanetza::asn1::copy(asn_DEF_CoopAwareness, &((*cam)->cam));

        vanetza::asn1::Camo camo;

        camo->header = *(ItsPduHeader_t*)c1;
        camo->cam = *(CoopAwareness_t*)c2;

        std::unique_ptr<vanetza::geonet::DownPacket> dp
            { new vanetza::geonet::DownPacket };

        dp->layer(vanetza::OsiLayer::Application) = std::move(camo);
        up = *dp;
    }
    
    return boost::create_byte_view(up, vanetza::OsiLayer::Application);
}