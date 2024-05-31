////////////////////////////////////////////////////////////////////////////////
// Main file for the ASIO scheduler (UDP version) task class. An object of    //
// this task class enables the interaction between the ASIO scheduler and the //
// corresponding service running inside a vehicle instance.                   //
//                                                                            //
// THIS FILE IS BASED ON THE ASIO SCHEDULER FILES THAT COME WITH ARTERY.      //
//                                                                            //
// @file    AsioTaskUDP.cpp                                                   //
// @author  Manuel Haerer                                                     //
// @date    23.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#include "AsioSchedulerUDP.hpp"
#include "AsioTaskUDP.hpp"

namespace artery
{
	AsioTaskUDP::AsioTaskUDP(
		AsioSchedulerUDP& scheduler,
		boost::asio::ip::udp::socket sSocket,
		boost::asio::ip::udp::socket rSocket,
		omnetpp::cModule& mod) :
		scheduler(scheduler),
		sendSocket(std::move(sSocket)),
		receiveSocket(std::move(rSocket)),
		message(new AsioDataUDP("ASIO data (UDP version)")),
		module(mod)
	{
	}

	AsioTaskUDP::~AsioTaskUDP()
	{
		scheduler.cancelTask(this);
	}

	void AsioTaskUDP::connect(boost::asio::ip::udp::endpoint ep)
	{
		sendSocket.connect(ep);
		scheduler.processTask(this);
	}

	void AsioTaskUDP::write(const std::vector<boost::asio::const_buffer>& buf)
	{
		sendSocket.send(buf);
	}

	void AsioTaskUDP::handleNext()
	{
		scheduler.processTask(this);
	}

	AsioDataUDP* AsioTaskUDP::getDataMessage()
	{
		return message.get();
	}

	const omnetpp::cModule* AsioTaskUDP::getDestinationModule()
	{
		return &module;
	}
}