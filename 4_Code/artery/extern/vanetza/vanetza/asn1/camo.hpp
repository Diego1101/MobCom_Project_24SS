////////////////////////////////////////////////////////////////////////////////
// Wrapper class for the original CAM structure (conforming to the standard). //
//                                                                            //
// @file    camo.hpp                                                          //
// @author  Manuel Haerer                                                     //
// @date    04.01.2022                                                        //
////////////////////////////////////////////////////////////////////////////////

#ifndef CAMO_HPP_WXYNEKFN
#define CAMO_HPP_WXYNEKFN

#include <vanetza/asn1/asn1c_conversion.hpp>
#include <vanetza/asn1/asn1c_wrapper.hpp>
#include <vanetza/asn1/its/CAMO.h>

namespace vanetza
{
    namespace asn1
    {
        class Camo : public asn1c_per_wrapper<CAMO_t>
        {
        public:
            using wrapper = asn1c_per_wrapper<CAMO_t>;
            Camo() : wrapper(asn_DEF_CAMO) {}
        };
    }
}

#endif