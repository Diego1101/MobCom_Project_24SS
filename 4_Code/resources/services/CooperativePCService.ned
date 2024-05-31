@namespace(artery);
simple CooperativePCService extends BasePCService
{
    parameters:
        // This number of neighbors is required 
        // to trigger a cooperative pseudonym change 
        int neighborThreshold = default(3);

        // When the distance of two vehicles is smaller
        // they are considered as neighbors
        double neighborRadius = default(30);
        
    @class(CooperativePCService);
}