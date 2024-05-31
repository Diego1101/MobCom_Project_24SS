/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "EtsiTs102941TrustLists"
 * 	found in "asn1/TS102941v131-TrustLists.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_RootCaEntry_H_
#define	_RootCaEntry_H_


#include "asn_application.h"

/* Including external dependencies */
#include "EtsiTs103097Certificate.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Forward declarations */
struct EtsiTs103097Certificate;

/* RootCaEntry */
typedef struct RootCaEntry {
	EtsiTs103097Certificate_t	 selfsignedRootCa;
	struct EtsiTs103097Certificate	*linkRootCaCertificate	/* OPTIONAL */;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} RootCaEntry_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_RootCaEntry;
extern asn_SEQUENCE_specifics_t asn_SPC_RootCaEntry_specs_1;
extern asn_TYPE_member_t asn_MBR_RootCaEntry_1[2];

#ifdef __cplusplus
}
#endif

/* Referred external types */
#include "EtsiTs103097Certificate.h"

#endif	/* _RootCaEntry_H_ */
#include "asn_internal.h"
