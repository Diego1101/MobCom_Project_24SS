import artery.application.ItsG5Service;
import artery.application;
import artery.application.CaService;

simple CaAttackerService like ItsG5Service
{
    parameters:
        @signal[CamReceived](type=artery::CaObject);

        @statistic[reception](source=CamReceived;record=vector(camStationId)?,vector(camGenerationDeltaTime)?);
        @class(CaAttackerService);

        string targetId;
        string logfile = default("dynamic_attacker.csv");
}
