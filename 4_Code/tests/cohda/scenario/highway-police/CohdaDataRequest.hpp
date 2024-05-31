////////////////////////////////////////////////////////////////////////////////
// This header file defines a class representing a Cohda data request header. //
// The class provides according serialization and deserialization methods.    //
// Data requests are sent from the simulation to the Cohda hardware over UDP. //
//                                                                            //
// @file    CohdaDataRequest.hpp                                              //
// @author  Manuel Haerer                                                     //
// @date    27.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef COHDA_DATAREQUEST_H_
#define COHDA_DATAREQUEST_H_

#include <array>

#include "CohdaUtility.hpp"

namespace Cohda
{
    class DataRequestHeader
    {
    private:
        static const std::size_t headerSize;

    public:
        // The constructor initializes all fields to the value 0.
        DataRequestHeader();
        ~DataRequestHeader();

        const std::vector<uint8_t> serialize() const;
        bool deserialize(const std::vector<uint8_t>&);

        inline static std::size_t getHeaderSize() { return headerSize; };

        // The structure of a Cohda data request is defined in the document
        // "ETSI: Sending / receiving BTP packets through UDP" provided by the
        // Cohda support.

        BTPType type;
        GNPacketTransport packetTransport;
        GNTrafficClass trafficClass;
        uint8_t maxPacketLifetime;

        uint16_t destinationPort;
        uint16_t destinationPortInfo;
        GNDestination destination;

        GNCommsProfile commsProfile;
        uint8_t repeatInterval;
        GNSecurityProfile securityProfile;
        uint8_t secSSPBitsLength;
        GNSecurityITSAID securityITSAID;

        std::array<uint8_t, 6> secSSPBits;
        uint16_t dataLength;
    };
}

#endif