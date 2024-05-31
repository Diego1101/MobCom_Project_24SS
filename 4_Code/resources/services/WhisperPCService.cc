/**
 * Whisper Pseudonym Change Service 
 *
 * @file    WhisperPCService.cc
 * @author  Janis Latus, Noah Köhler
 * @date    27.12.2022
 */

#include "WhisperPCService.h"
#include "artery/application/CaService.h"
#include "artery/application/VehicleDataProvider.h"
#include "vanetza/facilities/cam_functions.hpp"
#include "artery/application/Asn1PacketVisitor.h"
#include <algorithm>

namespace artery
{
    using namespace omnetpp;
    
    Define_Module(WhisperPCService);

    void WhisperPCService::initialize()
    {
        //Get init values
        this->_roadNeighborRadius = par("roadNeighborRadius");
        this->_generalNeighborRadius = par("generalNeighborRadius");
        this->_closeNeighborRadius = par("closeNeighborRadius");
        this->_counter = par("counter");
        this->_counterDefault = par("counter");
        this->_maxSpeed = 0;

        BasePCService::initialize();
    }

    void WhisperPCService::indicate(const vanetza::btp::DataIndication& ind, std::unique_ptr<vanetza::UpPacket> packet)
    {
        Asn1PacketVisitor<vanetza::asn1::Cam> visitor;
        auto traci = mVehicleController->getTraCI();

        //Get visitor information from CAM
	    const vanetza::asn1::Cam* cam = boost::apply_visitor(visitor, *packet);
        
        //Get visitor position in global coordinates
        const ReferencePosition_t visitorPos = (*cam)->cam.camParameters.basicContainer.referencePosition;

        //Calculate distance between us and visitor
        double distanceToVisitor = vanetza::facilities::distance(visitorPos, mVehicleDataProvider->latitude(),
                                                                 mVehicleDataProvider->longitude()) / boost::units::si::meters;

        //If the distance to the CAM Source is greater then the TxRange of the CAM, drop it
        if ((*cam)->ncam.txRange < distanceToVisitor)
        {
#ifdef DEBUG
            std::cout << "CAM got thrown away" << std::endl;
#endif
            return;
        }
        
        //Access to high frequency container
        BasicVehicleContainerHighFrequency_t basicVehicleContainer = (*cam)->cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency;

        //Get visitor speed in m/s
        vanetza::units::Velocity visitorSpeed = basicVehicleContainer.speed.speedValue / 100 * boost::units::si::meter_per_second;
        
        //Get visitor vehicle ID
        char visitorIdBuffer[(*cam)->ncam.vehicleId.size + 1] = { 0 };
        
        //Translate CAM octet_string to std::string
        vanetza::facilities::print_octet_string((*cam)->ncam.vehicleId, visitorIdBuffer, sizeof(visitorIdBuffer));
        std::string visitorId = std::string(visitorIdBuffer);

        //Get visitor RoadID
        std::string visitorRoad = traci->vehicle.getRoadID(visitorId);

        //Get own speed in m/s
        vanetza::units::Velocity ownSpeed = mVehicleDataProvider->speed();

        //Get own RoadID
        std::string ownRoad = traci->vehicle.getRoadID(mVehicleController->getVehicleId());
        
        //Are we and visitor on the same road 
        bool onSameRoad = (ownRoad == visitorRoad);
        
        // Check if visitor is a neighbour
        if((distanceToVisitor <= this->_generalNeighborRadius) ||
           ((distanceToVisitor <= this->_roadNeighborRadius) && onSameRoad))
        {
    
            // Check if visitor or we are faster and update _maxSpeed
            this->_maxSpeed = std::max(visitorSpeed, ownSpeed);
#ifdef DEBUG
            std::cout<<"###Detected neighbour##################"<<std::endl;
            std::cout<<"Distance to vehicle: "<<distanceToVisitor<<std::endl;
            std::cout<<"Own stationid: "<<mId<<std::endl;
            std::cout<<"Visitor stationid: "<<(*cam)->ncam.serviceId<<std::endl;
            std::cout<<"Own RoadId: "<<ownRoad<<std::endl;
            std::cout<<"Visitor RoadId: "<<visitorRoad<<std::endl;
            std::cout<<"RoadId is equal: "<<onSameRoad<<std::endl;
            std::cout<<"Own speed in m/s: "<<ownSpeed.value()<<std::endl;
            std::cout<<"Visitor speed in m/s: "<<visitorSpeed.value()<<std::endl;
#endif     
            //Check if visitor is close      
            if(distanceToVisitor <= this->_closeNeighborRadius)
            {
                this->_isClose = true;
            }
        }

        CaService::indicate(ind, std::move(packet));
    }

    bool WhisperPCService::triggerConditionsAreMet()
    {
       //Check if Messages were sent in a small range for a while, if so change pseoudnym and reset
        if (this->_counter <= (this->_counterDefault / 2) && this->_isClose)   
        {
            this->_counter = this->_counterDefault;
            this->_isClose = false;
            return true;
        }
        else if (this->_counter <= 0)
        {
            this->_counter = this->_counterDefault;
            return true;
        }
        return false;
    }

    void WhisperPCService::trigger()
    {
        //Update max speed
        this->_maxSpeed = std::max(this->_maxSpeed, mVehicleDataProvider->speed());

        //Change unit to km/h
        double maxSpeedKmh = this->_maxSpeed.value() * 3.6;

        if (maxSpeedKmh < lowSpeed)
        {
            const_cast<VehicleDataProvider *>(mVehicleDataProvider)->setTxRange(lowSpeedTxRange);
            this->_counter -= lowSpeedCtrDec;
        }
        else if (maxSpeedKmh < midSpeed)
        {
            const_cast<VehicleDataProvider *>(mVehicleDataProvider)->setTxRange(midSpeedTxRange);
            this->_counter -= midSpeedCtrDec;
        }
        else if (maxSpeedKmh < highSpeed)
        {
            const_cast<VehicleDataProvider *>(mVehicleDataProvider)->setTxRange(highSpeedTxRange);
            this->_counter -= highSpeedCtrDec;
            /**
             * In the Model the counter isn't decreased when the car gets faster then 36 km/h
             * But it makes sense to still decrease the counter, because otherwise there won't be a PC at all after the car is too fast
             * To counter this problem we can decrease the counter, but just a little and we can set the default value of the counter higher
             * 
             * uncomment this:
             * this->_counter -= highSpeedCtrDec;
             * 
            */
        }
        else
        {
            this->_counter -= highSpeedCtrDec;
            const_cast<VehicleDataProvider *>(mVehicleDataProvider)->setTxRange(maxTxRange);
            this->_counter = this->_counterDefault;
        }
#ifdef DEBUG
        std::cout << "Speed in km/h: " << maxSpeedKmh << std::endl;
        std::cout << "TxRange in m: " << mVehicleDataProvider->getTxRange() << std::endl;
#endif 

        this->_maxSpeed = 0;

        if (triggerConditionsAreMet())
        {
            changePseudonym();
        }
        
        CaService::trigger();
    }

}