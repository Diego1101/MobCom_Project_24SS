import artery.application.CaService;

@namespace(artery);
simple BasePCService extends CaService
{
    parameters:
        @signal[PseudonymChanged](type=double);
        @statistic[nPseudonymChanged](source=PseudonymChanged;title="nPseudonyms";record=last);
    
    @class(BasePCService);
}
