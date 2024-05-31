////////////////////////////////////////////////////////////////////////////////
// This header file defines a class representing a Cohda data indication      //
// header. The class provides according serialization and deserialization     //
// methods. Data indications are sent from the Cohda hardware to the          //
// simulation over UDP.                                                       //
//                                                                            //
// @file    CohdaDataIndication.hpp                                           //
// @author  Manuel Haerer                                                     //
// @date    27.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef COHDA_DATAINDICATION_H_
#define COHDA_DATAINDICATION_H_

#include <array>

#include "CohdaUtility.hpp"

namespace Cohda
{
    class DataIndicationHeader
    {
    private:
        static const std::size_t headerSize;

    public:
        // The constructor initializes all fields to the value 0.
        DataIndicationHeader();
        ~DataIndicationHeader();

        const std::vector<uint8_t> serialize() const;
        bool deserialize(const std::vector<uint8_t>&);

        inline static std::size_t getHeaderSize() { return headerSize; };

        // The structure of a Cohda data indication is defined in the document
        // "ETSI: Sending / receiving BTP packets through UDP" provided by the
        // Cohda support.

        BTPType type;
        GNPacketTransport packetTransport;
        GNTrafficClass trafficClass;
        uint8_t maxPacketLifetime;

        uint16_t destinationPort;
        uint16_t destinationPortInfo;
        GNDestination destination;

        GNSecurityProfile securityProfile;
        uint8_t secSSPBitsLength;
        GNSecurityITSAID securityITSAID;

        std::array<uint8_t, 6> secSSPBits;
        std::array<uint8_t, 8> secCertId;
        uint16_t dataLength;
    };
}

#endif