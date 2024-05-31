/**
 * Cooperative Pseudonym Change Strategy 
 * based on the number of neighbors (CPN)
 *
 * @file    CooperativePCService.h
 * @author  Janis Latus
 * @date    27.12.2022
 */

#include "CooperativePCService.h"
#include "artery/application/CaService.h"
#include "artery/application/VehicleDataProvider.h"
#include "vanetza/facilities/cam_functions.hpp"
#include "artery/application/Asn1PacketVisitor.h"

namespace artery
{
    using namespace omnetpp;
    
    Define_Module(CooperativePCService);

    void CooperativePCService::initialize()
    {
        //Initialize class members
        this->_neighborCount = 0;
        this->_neighborRadius = par("neighborRadius");
        this->_neighborThreshold = par("neighborThreshold");
        this->_readyForPC = false;

#ifdef DEBUG
        std::cout<<"Neighbor Radius:"<<this->_neighborRadius<<std::endl;
        std::cout<<"Neighbor Threshold:"<<this->_neighborThreshold<<std::endl;
#endif

        BasePCService::initialize();
    }

    void CooperativePCService::indicate(const vanetza::btp::DataIndication& ind, std::unique_ptr<vanetza::UpPacket> packet)
    {
        Asn1PacketVisitor<vanetza::asn1::Cam> visitor;
       
        //Get visitor information from CAM
	    const vanetza::asn1::Cam* cam = boost::apply_visitor(visitor, *packet);
        
        //Get visitor position in global coordinates
        const ReferencePosition_t visitorPos = (*cam)->cam.camParameters.basicContainer.referencePosition;

        //Calculate distance between us and visitor
        double distanceToVisitor = vanetza::facilities::distance(visitorPos, mVehicleDataProvider->latitude(),
                                                                 mVehicleDataProvider->longitude()) / boost::units::si::meters;
        
        //If distance is within in the range count it as neighbor
        if (distanceToVisitor <= this->_neighborRadius)
        {
            this->_neighborCount++;

            //Read ready flag
            bool readyFlagVisitor = (*cam)->ncam.readyFlag;
            
            //Visitor requests pseudonym change 
            if (readyFlagVisitor)
            {
                //trigger pseudonym change
                this->_readyForPC = true;   
#ifdef DEBUG               
                std::cout<<"Neighbor Service Id:"<<(*cam)->ncam.serviceId<<std::endl;
                std::cout<<"Neighbor Station Id:"<<(*cam)->header.stationID<<std::endl;
                std::cout<<"Neighbor requests pc change"<<std::endl;
#endif
            }

            //Condition for requesting cooperative pseudonym change
            if (this->_neighborCount >= _neighborThreshold) 
            {
                //Send ready flag with next CAM
                this->mReadyFlag = true;

                //Trigger pseudonym change
                this->_readyForPC = true;
#ifdef DEBUG
                std::cout<<"Own Service Id:"<<this->mId<<std::endl; 
                std::cout<<"Own Station id:"<<this->mVehicleDataProvider->getStationId()<<std::endl;
                std::cout<<"Count of neighbors:"<<std::to_string(this->_neighborCount)<<std::endl;
                std::cout<<"Trigger for requesting pseudonym change met"<<std::endl;
#endif                 
            }
        }      
    }

    bool CooperativePCService::triggerConditionsAreMet()
    {
        //Reset neighbor count for next time slot
        this->_neighborCount = 0;

        if (this->_readyForPC)
        {
            this->_readyForPC = false;
            return true;
        }

        return false;
    }
}