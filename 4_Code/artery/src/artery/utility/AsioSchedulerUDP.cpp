////////////////////////////////////////////////////////////////////////////////
// Main file for the ASIO scheduler (UDP version). This type of scheduler     //
// enables real time synchronization and data exchange with external          //
// applications via UDP.                                                      //
//                                                                            //
// THIS FILE IS BASED ON THE ASIO SCHEDULER FILES THAT COME WITH ARTERY.      //
//                                                                            //
// @file    AsioSchedulerUDP.cpp                                              //
// @author  Manuel Haerer                                                     //
// @date    23.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#include "AsioSchedulerUDP.hpp"
#include "AsioTaskUDP.hpp"

#include <boost/asio/read.hpp>
#include <omnetpp/simtime.h>
#include <functional>

namespace artery
{
	Register_Class(AsioSchedulerUDP)

	template<typename PERIOD>
	struct ClockResolution
	{
		static const omnetpp::SimTimeUnit unit;
	};

	template<>
	const omnetpp::SimTimeUnit ClockResolution<std::milli>::unit =
		omnetpp::SIMTIME_MS;

	template<>
	const omnetpp::SimTimeUnit ClockResolution<std::micro>::unit =
		omnetpp::SIMTIME_US;
	
	template<>
	const omnetpp::SimTimeUnit ClockResolution<std::nano>::unit =
		omnetpp::SIMTIME_NS;

	constexpr omnetpp::SimTimeUnit steadyClockResolution()
	{
		return ClockResolution<std::chrono::steady_clock::period>::unit;
	}

	std::chrono::steady_clock::duration steadyClockDuration(
		const omnetpp::SimTime t)
	{
		return std::chrono::steady_clock::duration
		{
			t.inUnit(steadyClockResolution())
		};
	}

	AsioSchedulerUDP::AsioSchedulerUDP() :
		work(service),
		timer(service),
		state(FluxState::PAUSED)
	{
	}

	std::string AsioSchedulerUDP::info() const
	{
		return std::string(
			"ASIO scheduler (UDP version; " +
			omnetpp::SimTime(1, steadyClockResolution()).str() +
			" resolution)");
	}

	std::unique_ptr<AsioTaskUDP> AsioSchedulerUDP::createTask(
		omnetpp::cModule& mod,
		const boost::asio::ip::udp::endpoint* lep)
	{
		std::unique_ptr<AsioTaskUDP> result;
		boost::asio::ip::udp::socket sSocket(service);
		boost::asio::ip::udp::socket rSocket(service);
		rSocket.open(boost::asio::ip::udp::v4());

		if (lep)
		{
			rSocket.bind(*lep);
		}

		result.reset(new AsioTaskUDP(
			*this,
			std::move(sSocket),
			std::move(rSocket),
			mod));
		
		return result;
	}

	void AsioSchedulerUDP::cancelTask(AsioTaskUDP* task)
	{
		if (task != nullptr)
		{
			sim->getFES()->remove(task->getDataMessage());
		}
	}

	void AsioSchedulerUDP::processTask(AsioTaskUDP* task)
	{
		auto& buffer = task->message->getBuffer();

		auto handler = std::bind(
			&AsioSchedulerUDP::handleTask,
			this,
			task,
			std::placeholders::_1,
			std::placeholders::_2);
		
		task->receiveSocket.async_receive(
			boost::asio::buffer(buffer.data(), buffer.size()),
			handler);
	}

	omnetpp::cEvent* AsioSchedulerUDP::guessNextEvent()
	{
		return sim->getFES()->peekFirst();
	}

	omnetpp::cEvent* AsioSchedulerUDP::takeNextEvent()
	{
		while (true)
		{
			omnetpp::cEvent* event = sim->getFES()->peekFirst();

			if (event)
			{
				if (event->isStale())
				{
					omnetpp::cEvent* tmp = sim->getFES()->removeFirst();
					ASSERT(tmp == event);
					delete tmp;
				}
				else
				{
					runUntil = reference +
						steadyClockDuration(event->getArrivalTime());
					
					try
					{
						ASSERT(!service.stopped());
						setTimer();

						while (state == FluxState::DWADLING)
						{
							service.run_one();
						}

						timer.cancel();
						service.poll();
					}
					catch (boost::system::system_error& e)
					{
						throw omnetpp::cRuntimeError("ASIO scheduler (UDP "
							"version): Fatal IO error: %s", e.what());
					}

					if (state == FluxState::SYNC)
					{
						return sim->getFES()->removeFirst();
					}
					else
					{
						return nullptr;
					}
				}
			}
			else
			{
				throw omnetpp::cTerminationException(omnetpp::E_ENDEDOK);
			}
		}
	}

	void AsioSchedulerUDP::putBackEvent(omnetpp::cEvent* event)
	{
		sim->getFES()->putBackFirst(event);
	}

	void AsioSchedulerUDP::startRun()
	{
		state = FluxState::SYNC;

		if (service.stopped())
		{
			service.reset();
		}

		reference = std::chrono::steady_clock::now();
	}

	void AsioSchedulerUDP::endRun()
	{
		state = FluxState::PAUSED;
		service.stop();
	}

	void AsioSchedulerUDP::executionResumed()
	{
		state = FluxState::SYNC;

		reference = std::chrono::steady_clock::now();
		reference -= steadyClockDuration(omnetpp::simTime());
	}

	void AsioSchedulerUDP::handleTask(
		AsioTaskUDP* task,
		const boost::system::error_code& ec,
		std::size_t bytes)
	{
		if (!ec)
		{
			if (bytes >= task->message->getBuffer().size())
			{
				EV_WARN << "ASIO scheduler (UDP version): Received UDP packet "
					"may have been truncated; skipping...\n";
			}
			else
			{
				EV_INFO << "ASIO scheduler (UDP version): Received UDP packet; "
					"putting it in the FES...\n";

				const auto arrivalClock =
					std::chrono::steady_clock::now() - reference;
				
				const omnetpp::SimTime arrivalSimtime
				{
					arrivalClock.count(), steadyClockResolution()
				};
				
				ASSERT(omnetpp::simTime() <= arrivalSimtime);

				AsioDataUDP* msg = task->getDataMessage();
				
				msg->setLength(bytes);
				msg->setArrival(
					task->getDestinationModule()->getId(),
					-1,
					arrivalSimtime);
				
				sim->getFES()->insert(msg);
			}
		}
		else if (ec != boost::asio::error::operation_aborted)
		{
			EV_ERROR << "ASIO scheduler (UDP version): Failed reading from "
				"socket: " << ec.message().c_str() << "\n";
		}
	}

	void AsioSchedulerUDP::handleTimer(const boost::system::error_code& ec)
	{
		if (omnetpp::getEnvir()->idle())
		{
			state = FluxState::PAUSED;
		}
		else if (ec)
		{
			state = FluxState::SYNC;
		}
		else
		{
			setTimer();
		}
	}

	void AsioSchedulerUDP::setTimer()
	{
		static const auto maxTimer = std::chrono::milliseconds(100);
		const auto now = std::chrono::steady_clock::now();

		if (runUntil > now)
		{
			state = FluxState::DWADLING;
			timer.expires_at(std::min(runUntil, now + maxTimer));

			timer.async_wait(
				std::bind(
					&AsioSchedulerUDP::handleTimer,
					this,
					std::placeholders::_1));
		}
		else
		{
			state = FluxState::SYNC;
		}
	}
}