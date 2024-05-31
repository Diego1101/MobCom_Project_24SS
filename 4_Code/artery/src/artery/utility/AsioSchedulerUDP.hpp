////////////////////////////////////////////////////////////////////////////////
// Header file for the ASIO scheduler (UDP version). This type of scheduler   //
// enables real time synchronization and data exchange with external applica- //
// tions via UDP.                                                             //
//                                                                            //
// THIS FILE IS BASED ON THE ASIO SCHEDULER FILES THAT COME WITH ARTERY.      //
//                                                                            //
// @file    AsioSchedulerUDP.hpp                                              //
// @author  Manuel Haerer                                                     //
// @date    23.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef ARTERY_ASIOSCHEDULERUDP_H_
#define ARTERY_ASIOSCHEDULERUDP_H_

#include <omnetpp/cmodule.h>
#include <omnetpp/cscheduler.h>
#include <boost/asio/ip/udp.hpp>
#include <boost/asio/io_service.hpp>
#include <boost/asio/steady_timer.hpp>
#include <chrono>

namespace artery
{
	class AsioTaskUDP;

	class AsioSchedulerUDP : public omnetpp::cScheduler
	{
		public:
			AsioSchedulerUDP();

			virtual std::string info() const override;

			std::unique_ptr<AsioTaskUDP> createTask(
				omnetpp::cModule&,
				const boost::asio::ip::udp::endpoint* = nullptr);

			void cancelTask(AsioTaskUDP*);
			void processTask(AsioTaskUDP*);

		protected:
			virtual omnetpp::cEvent* guessNextEvent() override;
			virtual omnetpp::cEvent* takeNextEvent() override;
			virtual void putBackEvent(omnetpp::cEvent*) override;

			virtual void startRun() override;
			virtual void endRun() override;
			virtual void executionResumed() override;

		private:
			void handleTask(
				AsioTaskUDP*,
				const boost::system::error_code&,
				std::size_t);
			
			void handleTimer(const boost::system::error_code&);
			void setTimer();

			enum class FluxState
			{
				PAUSED,
				DWADLING,
				SYNC
			} state;

			boost::asio::io_service service;
			boost::asio::io_service::work work;
			boost::asio::steady_timer timer;
			std::chrono::steady_clock::time_point reference;
			std::chrono::steady_clock::time_point runUntil;
	};
}

#endif