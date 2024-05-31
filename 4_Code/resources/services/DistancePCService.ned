import BasePCService;

@namespace(artery);
simple DistancePCService extends BasePCService
{
    parameters:
        double pseudonymChangeDistance = default(500);
        
    @class(DistancePCService);
}
