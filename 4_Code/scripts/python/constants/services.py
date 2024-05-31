# Pseudonym change strategies service class mappings

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Janis Latus (WS22/23)
# @date    27.12.2022

from enums.PseudoChangeType import PseudoChangeType


service_classes = {
    PseudoChangeType.NONE: 'artery.application.CaService',
    PseudoChangeType.PERIODICAL: 'PeriodicalPCService',
    PseudoChangeType.DISTANCE: 'DistancePCService',
    PseudoChangeType.SLOW: 'SLOWPCService',
    PseudoChangeType.WHISPER: 'WhisperPCService',
    PseudoChangeType.CPN: 'CooperativePCService'
}
