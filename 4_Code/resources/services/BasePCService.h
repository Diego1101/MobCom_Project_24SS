/**
 * Base class for all pseudonym change strategies.
 * Each pseudonym change strategy service class should implement
 * `triggerConditionsAreMet` function.
 *
 * @author  Samuel Müller (WS21/22)
 * @author  Martin Dell (WS22/23)
 * @date    24.01.2023
 */

#ifndef MOBCOM_BASEPC_H_
#define MOBCOM_BASEPC_H_

#include "artery/application/CaService.h"

namespace artery
{
    class BasePCService : public CaService
    {
    public:
        void initialize() override;
        void trigger() override;

    protected:
        /**
         * Checks if pseudonym should be changed in this update step.
         *
         * @returns True if pseudonym should be send; otherwise false.
         */
        virtual bool triggerConditionsAreMet() { return false; }

        /**
         * Checks if CAM should be send in this update step.
         *
         * @returns True if CAM should be send; otherwise false.
         */
        virtual bool sendCamConditionsAreMet() { return true; }

        /**
         * Changes the pseudonym of the vehicle.
         */
        virtual void changePseudonym();

        /**
         * Prints the pseudonym change event to console.
         *
         * @param newPseudonym The new pseudonym of the vehicle.
         * @param prevPseudonym The previous pseudonym of the vehicle.
         */
        virtual void logPseudonymChange(uint32_t newPseudonym, uint32_t prevPseudonym) const;
    };
}

#endif
