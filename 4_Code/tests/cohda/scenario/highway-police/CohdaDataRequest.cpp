////////////////////////////////////////////////////////////////////////////////
// This file defines the methods for the class representing a Cohda data      //
// request header. Data requests are sent from the simulation to the Cohda    //
// hardware over UDP.                                                         //
//                                                                            //
// @file    CohdaDataRequest.cpp                                              //
// @author  Manuel Haerer                                                     //
// @date    27.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#include <algorithm>

#include "CohdaDataRequest.hpp"

using namespace Cohda;

const size_t DataRequestHeader::headerSize = 40;

// The constructor initializes all fields to the value 0.
DataRequestHeader::DataRequestHeader()
{
    type = (BTPType)0;
    packetTransport = (GNPacketTransport)0;
    trafficClass = (GNTrafficClass)0;
    maxPacketLifetime = 0;

    destinationPort = 0;
    destinationPortInfo = 0;

    destination.latitude = 0;
    destination.longitude = 0;
    destination.distanceA = 0;
    destination.distanceB = 0;
    destination.angle = 0;
    destination.shape = (GNShape)0;

    commsProfile = (GNCommsProfile)0;
    repeatInterval = 0;
    securityProfile = (GNSecurityProfile)0;
    secSSPBitsLength = 0;
    securityITSAID = (GNSecurityITSAID)0;

    for (auto& bits : secSSPBits)
    {
        bits = 0;
    }

    dataLength = 0;
}

DataRequestHeader::~DataRequestHeader()
{
}

const std::vector<uint8_t> DataRequestHeader::serialize() const
{
    std::vector<uint8_t> data;
    data.reserve(headerSize);

    write8BitUInt(data, (uint8_t)type);
    write8BitUInt(data, (uint8_t)packetTransport);
    write8BitUInt(data, (uint8_t)trafficClass);
    write8BitUInt(data, maxPacketLifetime);
    
    write16BitUInt(data, destinationPort);
    write16BitUInt(data, destinationPortInfo);

    write32BitUInt(data, destination.latitude);
    write32BitUInt(data, destination.longitude);
    write16BitUInt(data, destination.distanceA);
    write16BitUInt(data, destination.distanceB);
    write16BitUInt(data, destination.angle);
    write8BitUInt(data, (uint8_t)destination.shape);
    write8BitUInt(data, 0); // Padding / reserve.

    write8BitUInt(data, (uint8_t)commsProfile);
    write8BitUInt(data, repeatInterval);
    write8BitUInt(data, (uint8_t)securityProfile);
    write8BitUInt(data, secSSPBitsLength);
    write32BitUInt(data, (uint32_t)securityITSAID);

    data.insert(data.end(), secSSPBits.begin(), secSSPBits.end());
    write16BitUInt(data, dataLength);

    return std::move(data);
}

bool DataRequestHeader::deserialize(const std::vector<uint8_t>& data)
{
    if (data.size() != headerSize)
    {
        return false;
    }

    auto current = data.begin();
    auto end = data.end();
    uint8_t dummy;

    // Note: If an error is detected, deserialization ends and the current
    // object is possibly left in a half initialized state.

    if (read8BitUInt(current, end, (uint8_t&)type) &&
        read8BitUInt(current, end, (uint8_t&)packetTransport) &&
        read8BitUInt(current, end, (uint8_t&)trafficClass) &&
        read8BitUInt(current, end, maxPacketLifetime) &&
        read16BitUInt(current, end, destinationPort) &&
        read16BitUInt(current, end, destinationPortInfo) &&
        read32BitUInt(current, end, destination.latitude) &&
        read32BitUInt(current, end, destination.longitude) &&
        read16BitUInt(current, end, destination.distanceA) &&
        read16BitUInt(current, end, destination.distanceB) &&
        read16BitUInt(current, end, destination.angle) &&
        read8BitUInt(current, end, (uint8_t&)destination.shape) &&
        read8BitUInt(current, end, dummy) && // Padding / reserve.
        read8BitUInt(current, end, (uint8_t&)commsProfile) &&
        read8BitUInt(current, end, repeatInterval) &&
        read8BitUInt(current, end, (uint8_t&)securityProfile) &&
        read8BitUInt(current, end, secSSPBitsLength) &&
        read32BitUInt(current, end, (uint32_t&)securityITSAID))
    {
        if ((end - current) < secSSPBits.size())
        {
            return false;
        }
        else
        {
            std::copy_n(current, secSSPBits.size(), secSSPBits.begin());
            current += secSSPBits.size();
        }

        return read16BitUInt(current, end, dataLength);
    }

    return false;
}