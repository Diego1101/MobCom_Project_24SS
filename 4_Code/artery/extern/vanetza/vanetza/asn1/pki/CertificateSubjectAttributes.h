/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "EtsiTs102941BaseTypes"
 * 	found in "asn1/TS102941v131-BaseTypes.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_CertificateSubjectAttributes_H_
#define	_CertificateSubjectAttributes_H_


#include "asn_application.h"

/* Including external dependencies */
#include "SubjectAssurance.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Forward declarations */
struct CertificateId;
struct ValidityPeriod;
struct GeographicRegion;
struct SequenceOfPsidSsp;
struct SequenceOfPsidGroupPermissions;

/* CertificateSubjectAttributes */
typedef struct CertificateSubjectAttributes {
	struct CertificateId	*id	/* OPTIONAL */;
	struct ValidityPeriod	*validityPeriod	/* OPTIONAL */;
	struct GeographicRegion	*region	/* OPTIONAL */;
	SubjectAssurance_t	*assuranceLevel	/* OPTIONAL */;
	struct SequenceOfPsidSsp	*appPermissions	/* OPTIONAL */;
	struct SequenceOfPsidGroupPermissions	*certIssuePermissions	/* OPTIONAL */;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} CertificateSubjectAttributes_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_CertificateSubjectAttributes;
extern asn_SEQUENCE_specifics_t asn_SPC_CertificateSubjectAttributes_specs_1;
extern asn_TYPE_member_t asn_MBR_CertificateSubjectAttributes_1[6];
extern asn_per_constraints_t asn_PER_type_CertificateSubjectAttributes_constr_1;

#ifdef __cplusplus
}
#endif

/* Referred external types */
#include "CertificateId.h"
#include "ValidityPeriod.h"
#include "GeographicRegion.h"
#include "SequenceOfPsidSsp.h"
#include "SequenceOfPsidGroupPermissions.h"

#endif	/* _CertificateSubjectAttributes_H_ */
#include "asn_internal.h"