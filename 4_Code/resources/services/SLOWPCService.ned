import BasePCService;

@namespace(artery);
simple SLOWPCService extends BasePCService
{
    parameters:
        // The time in seconds after which the pseudonym is changed.
        double pseudonymLifetime = default(0.5);

        // The max speed in km/h where a vehicle is considered slow.
        // Slow vehicles do not send CAMs.
        double slowThreshold = default(30);

    @class(SLOWPCService);
}
