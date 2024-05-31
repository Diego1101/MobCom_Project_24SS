/**
 * Whisper Pseudonym Change Service
 *
 * @file    WhisperPCService.h
 * @author  Janis Latus
 * @date    27.12.2022
 */

#ifndef __VEINS_WhisperPC_H_
#define __VEINS_WhisperPC_H_

#include "BasePCService.h"



namespace artery
{
    /**
     *  This class implements the whisper pseudonym change strategy
     */
    class WhisperPCService : public BasePCService
    {

    public:
        // Constants for speed classes
        static constexpr int lowSpeed = 18;
        static constexpr int midSpeed = 36;
        static constexpr int highSpeed = 54;

        // Constants for tx range adjustment
        static constexpr int lowSpeedTxRange = 50;
        static constexpr int midSpeedTxRange = 100;
        static constexpr int highSpeedTxRange = 200;
        static constexpr int maxTxRange = 300;

        // Constants for counter decrement
        static constexpr int lowSpeedCtrDec = 5;
        static constexpr int midSpeedCtrDec = 10;
        static constexpr int highSpeedCtrDec = 1;

        /**
         * Initialize the service
         */
        void initialize() override;

        /**
         * Receive CAM from other vehicles.
        */
        void indicate(const vanetza::btp::DataIndication&, std::unique_ptr<vanetza::UpPacket>) override;

        /**
         * Send CAM but only for a specific transmission range.
        */
       void trigger() override;

    protected:
        /*
         * Checks if pseudonym change shall happen or not
         * @Returns true if pseudonym shall be changed; otherwise false.
         */
        bool triggerConditionsAreMet() override;

    private:
        /*
         * Max speed (own speed compared to visitor speed)
         */
        vanetza::units::Velocity _maxSpeed;

        /*
         * Tracks if a visitor is close
         */
        bool _isClose;

        /**
         * Two vehicles are considered as road neighbors
         * if there distance is smaller then _roadNeighborRadius.
         * The vehicles need to drive on the same road aswell.
         */
        double _roadNeighborRadius;

        /**
         * Two vehicles are considered as general neighbors
         * if there distance is smaller then _generalNeighborRadius.
         */
        double _generalNeighborRadius;

        /**
         * Two vehicles are considered as close neighbors
         * if there distance is smaller then _closeNeighborRadius.
         */
        double _closeNeighborRadius;

        /**
         * This counter gets decremented when CAM messages are send.
         * If the value is smaller then a defined threshold,
         * a pseudonym change will be triggered.
         */
        int16_t _counter;

        /**
         * Default value for reinitialization of _counter
         */
        int16_t _counterDefault;
    };
}

#endif
