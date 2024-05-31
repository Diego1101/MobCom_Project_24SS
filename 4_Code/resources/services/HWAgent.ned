////////////////////////////////////////////////////////////////////////////////
// Parameter specification for the "HWAgent" service.                         //
//                                                                            //
// @file    HWAgent.ned                                                       //
// @author  Manuel Haerer                                                     //
// @date    27.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

simple HWAgent
{
    parameters:
        // Flag for the call "moveToXY" (SUMO API); see SUMO documentation.
        int keepRouteFlag = default(6);

        // If true, the ITS-AID will get set from the destination port (assuming
        // the usage of well-known service ports) if the ITS-AID is not
        // available from the data indication; used for Cohda data requests.
        bool useCohdaPortClassification = default(true);

        // IP address of the host which will receive Cohda data requests.
        string remoteIP = default("127.0.0.1");

        // Port of the UDP service which will receive Cohda data requests.
        int remotePort = default(4401);
        
        // Local IP address which will receive Cohda data indications.
        string localIP = default("127.0.0.1");

        // Local port which will receive Cohda data indications.
        int localPort = default(4400);
}