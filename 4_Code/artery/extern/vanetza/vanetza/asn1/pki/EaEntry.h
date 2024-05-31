/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "EtsiTs102941TrustLists"
 * 	found in "asn1/TS102941v131-TrustLists.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_EaEntry_H_
#define	_EaEntry_H_


#include "asn_application.h"

/* Including external dependencies */
#include "EtsiTs103097Certificate.h"
#include "Url.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* EaEntry */
typedef struct EaEntry {
	EtsiTs103097Certificate_t	 eaCertificate;
	Url_t	 aaAccessPoint;
	Url_t	*itsAccessPoint	/* OPTIONAL */;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} EaEntry_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_EaEntry;
extern asn_SEQUENCE_specifics_t asn_SPC_EaEntry_specs_1;
extern asn_TYPE_member_t asn_MBR_EaEntry_1[3];

#ifdef __cplusplus
}
#endif

#endif	/* _EaEntry_H_ */
#include "asn_internal.h"
