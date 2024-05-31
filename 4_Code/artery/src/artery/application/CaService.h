/*
* Artery V2X Simulation Framework
* Copyright 2014-2019 Raphael Riebl et al.
* Licensed under GPLv2, see COPYING file for detailed license and warranty terms.
*/

#ifndef ARTERY_CASERVICE_H_
#define ARTERY_CASERVICE_H_

#include "artery/application/ItsG5BaseService.h"
#include "artery/utility/Channel.h"
#include "artery/utility/Geometry.h"
#include <vanetza/asn1/cam.hpp>
#include <vanetza/btp/data_interface.hpp>
#include <vanetza/units/angle.hpp>
#include <vanetza/units/velocity.hpp>
#include <omnetpp/simtime.h>

/* Headers added by HS Esslingen project WS 2021/2022 by Hauke Groszmuk & Daniela Hörl*/
#include "artery/traci/VehicleController.h"

namespace artery
{

class NetworkInterfaceTable;
class Timer;
class VehicleDataProvider;

class CaService : public ItsG5BaseService
{
	public:
		CaService();
		void initialize() override;
		void indicate(const vanetza::btp::DataIndication&, std::unique_ptr<vanetza::UpPacket>) override;
		void trigger() override;


	protected:
		void checkTriggeringConditions(const omnetpp::SimTime&);
		bool checkHeadingDelta() const;
		bool checkPositionDelta() const;
		bool checkSpeedDelta() const;
		void sendCam(const omnetpp::SimTime&);
		omnetpp::SimTime genCamDcc();
        const VehicleDataProvider* mVehicleDataProvider = nullptr;
		ChannelNumber mPrimaryChannel = channel::CCH;
		const NetworkInterfaceTable* mNetworkInterfaceTable = nullptr;

		const Timer* mTimer = nullptr;
		LocalDynamicMap* mLocalDynamicMap = nullptr;

		omnetpp::SimTime mGenCamMin;
		omnetpp::SimTime mGenCamMax;
		omnetpp::SimTime mGenCam;
		unsigned mGenCamLowDynamicsCounter;
		unsigned mGenCamLowDynamicsLimit;
		Position mLastCamPosition;
		vanetza::units::Velocity mLastCamSpeed;
		vanetza::units::Angle mLastCamHeading;
		omnetpp::SimTime mLastCamTimestamp;
		omnetpp::SimTime mLastLowCamTimestamp;
		vanetza::units::Angle mHeadingDelta;
		vanetza::units::Length mPositionDelta;
		vanetza::units::Velocity mSpeedDelta;
		bool mDccRestriction;
		bool mFixedRate;

		/* Addition from HS Esslingen project WS 2021/2022 by Hauke Groszmuk  & Daniela Hörl */
		int mId;

		const traci::VehicleController* mVehicleController = nullptr;
		int mLength;
		int mWidth;

		/* Addition from HS Esslingen project WS 2022/2023 by Janis Latus */
		bool mReadyFlag = false;

        std::string camLogfile;
        /* End of changes */
};

vanetza::asn1::Cam createCooperativeAwarenessMessage(const VehicleDataProvider&, uint16_t genDeltaTime);
void addLowFrequencyContainer(vanetza::asn1::Cam&, unsigned pathHistoryLength = 0);

} // namespace artery

#endif /* ARTERY_CASERVICE_H_ */
