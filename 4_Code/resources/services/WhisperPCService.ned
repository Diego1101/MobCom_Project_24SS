import BasePCService;

@namespace(artery);
simple WhisperPCService extends BasePCService
{
    parameters:
        // Two vehicles are considered as road neighbors
        // if there distance is smaller then roadNeighborRadius 
        // & if they are on the same road
        double roadNeighborRadius = default(100);

        // Two vehicles are considered as general neighbors
        // if there distance is smaller then generalNeighborRadius
        double generalNeighborRadius = default(30);

        // Two vehicles are considered as close neighbors
        // if there distance is smaller then closeNeighborRadius
        double closeNeighborRadius = default(30);

        // This counter gets decremented when CAM messages
        // are send. When it crosses a defined threshold a 
        // pseudonym change is triggered.
        int counter = default(50);
    @class(WhisperPCService);
}