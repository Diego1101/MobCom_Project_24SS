////////////////////////////////////////////////////////////////////////////////
// Header file for the ASIO scheduler (UDP version) task class. An object of  //
// this task class enables the interaction between the ASIO scheduler and the //
// corresponding service running inside a vehicle instance.                   //
//                                                                            //
// THIS FILE IS BASED ON THE ASIO SCHEDULER FILES THAT COME WITH ARTERY.      //
//                                                                            //
// @file    AsioTaskUDP.hpp                                                   //
// @author  Manuel Haerer                                                     //
// @date    23.12.2021                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef ARTERY_ASIOTASKUDP_H_
#define ARTERY_ASIOTASKUDP_H_

#include "artery/utility/AsioDataUDP_m.h"

#include <boost/asio/buffer.hpp>
#include <boost/asio/ip/udp.hpp>
#include <omnetpp/cmodule.h>
#include <vector>

namespace artery
{
	class AsioSchedulerUDP;

	class AsioTaskUDP
	{
		public:
			// As UDP is connectionless, two sockets are required (first socket
			// for sending; second socket for receiving).
			AsioTaskUDP(
				AsioSchedulerUDP&,
				boost::asio::ip::udp::socket,
				boost::asio::ip::udp::socket,
				omnetpp::cModule&);
			
			virtual ~AsioTaskUDP();

			void connect(boost::asio::ip::udp::endpoint);
			void write(const std::vector<boost::asio::const_buffer>&);
			void handleNext();

			AsioDataUDP* getDataMessage();
			const omnetpp::cModule* getDestinationModule();

		private:
			friend class AsioSchedulerUDP;

			AsioSchedulerUDP& scheduler;
			std::unique_ptr<AsioDataUDP> message;
			omnetpp::cModule& module;

			boost::asio::ip::udp::socket sendSocket;
			boost::asio::ip::udp::socket receiveSocket;
	};
}

#endif