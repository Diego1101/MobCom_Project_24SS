////////////////////////////////////////////////////////////////////////////////
// OMNeT++ data message which gets sent from the ASIO scheduler (UDP version) //
// to the target module. The target module can receive this message via       //
// overloading the method "handleMessage".                                    //
//                                                                            //
// THIS FILE IS BASED ON THE ASIO SCHEDULER FILES THAT COME WITH ARTERY.      //
//                                                                            //
// @file    AsioDataUDP.msg                                                   //
// @author  Manuel Haerer                                                     //
// @date    23.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

cplusplus
{{
    #include <array>
    #include <cstdint>

    typedef std::array<uint8_t, 2048> AsioBufferUDP;
    typedef std::size_t AsioLengthUDP;
}}

class noncobject AsioBufferUDP;
class noncobject AsioLengthUDP;

message AsioDataUDP
{
    AsioBufferUDP Buffer;
    AsioLengthUDP Length;
}