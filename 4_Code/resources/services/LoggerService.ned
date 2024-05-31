import artery.application.ItsG5Service;

@namespace(mobcom);
simple LoggerService like ItsG5Service
{
    parameters:
        // Name of the log file where to write vehicle data to.
        string logfile = default("vehicles.csv");

    @class(LoggerService);
}
