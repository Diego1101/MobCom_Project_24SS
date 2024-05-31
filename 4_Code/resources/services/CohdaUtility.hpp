////////////////////////////////////////////////////////////////////////////////
// This file contains basic data types and data structures for proprietary    //
// Cohda headers. Additionally, some utility functions for serialization and  //
// deserialization are provided.                                              //
//                                                                            //
// @file    CohdaUtility.hpp                                                  //
// @author  Manuel Haerer                                                     //
// @date    27.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef COHDA_UTILITY_H_
#define COHDA_UTILITY_H_

#include <vector>
#include <cstdint>

namespace Cohda
{
    // Types and structures according to the Cohda document "ETSI: Sending /
    // receiving BTP packets through UDP"; see Cohda support.

    enum BTPType : uint8_t
    {
        TP_B = 2
    };

    enum GNPacketTransport : uint8_t
    {
        PT_GeoUniCast = 2,
        PT_GeoBroadCast = 4,
        PT_SingleHopBroadcast = 7
    };

    enum GNTrafficClass : uint8_t
    {
        TC_CAM = 0x02,
        TC_DENM = 0x01,
        TC_MAP_SPAT_IVIM_SAEM = 0x03,
        TC_SCH = 0x09
    };

    enum GNShape : uint8_t
    {
        SH_Circle = 0,
        SH_Rectangle = 1,
        SH_Ellipse = 2
    };

    struct GNDestination
    {
        uint32_t latitude;
        uint32_t longitude;
        uint16_t distanceA;
        uint16_t distanceB;
        uint16_t angle;
        GNShape shape;
    };

    enum GNCommsProfile : uint8_t
    {
        CP_G5 = 0
    };

    enum GNSecurityProfile : uint8_t
    {
        SP_Disabled = 0,
        SP_Enabled = 1
    };

    enum GNSecurityITSAID : uint32_t
    {
        AID_CAM = 0x24,
        AID_DENM = 0x25,
        AID_MAP = 0x8A,
        AID_SPAT = 0x89,
        AID_IVI = 0x8B,
        AID_SAEM = 0x84081,
        AID_CPM = 0x27F
    };

    // Utility functions for serialization.

    inline void write8BitUInt(std::vector<uint8_t>& data, uint8_t uin)
    {
        data.push_back(uin);
    }

    inline void write16BitUInt(std::vector<uint8_t>& data, uint16_t uin)
    {
        for (auto i = 1; i >= 0; i--)
        {
            data.push_back((uint8_t)(uin >> (i * 8)));
        }
    }

    inline void write32BitUInt(std::vector<uint8_t>& data , uint32_t uin)
    {
        for (auto i = 3; i >= 0; i--)
        {
            data.push_back((uint8_t)(uin >> (i * 8)));
        }
    }

    // Utility functions for deserialization.

    inline bool read8BitUInt(
        std::vector<uint8_t>::const_iterator& current,
        const std::vector<uint8_t>::const_iterator& end, 
        uint8_t& uin)
    {
        if ((end - current) < 1)
        {
            return false;
        }

        uin = *current;
        current++;

        return true;
    }

    inline bool read16BitUInt(
        std::vector<uint8_t>::const_iterator& current,
        const std::vector<uint8_t>::const_iterator& end, 
        uint16_t& uin)
    {
        if ((end - current) < 2)
        {
            return false;
        }

        uin = 0;

        for (auto i = 1; i >= 0; i--)
        {
            uin |= ((uint16_t)*current) << (i * 8);
            current++;
        }

        return true;
    }

    inline bool read32BitUInt(
        std::vector<uint8_t>::const_iterator& current,
        const std::vector<uint8_t>::const_iterator& end, 
        uint32_t& uin)
    {
        if ((end - current) < 4)
        {
            return false;
        }

        uin = 0;

        for (auto i = 3; i >= 0; i--)
        {
            uin |= ((uint32_t)*current) << (i * 8);
            current++;
        }

        return true;
    }
}

#endif