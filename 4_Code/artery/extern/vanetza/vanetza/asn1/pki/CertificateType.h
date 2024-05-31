/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "IEEE1609dot2"
 * 	found in "asn1/IEEE1609dot2.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_CertificateType_H_
#define	_CertificateType_H_


#include "asn_application.h"

/* Including external dependencies */
#include "NativeEnumerated.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum CertificateType {
	CertificateType_explicit	= 0,
	CertificateType_implicit	= 1
	/*
	 * Enumeration is extensible
	 */
} e_CertificateType;

/* CertificateType */
typedef long	 CertificateType_t;

/* Implementation */
extern asn_per_constraints_t asn_PER_type_CertificateType_constr_1;
extern asn_TYPE_descriptor_t asn_DEF_CertificateType;
extern const asn_INTEGER_specifics_t asn_SPC_CertificateType_specs_1;
asn_struct_free_f CertificateType_free;
asn_struct_print_f CertificateType_print;
asn_constr_check_f CertificateType_constraint;
ber_type_decoder_f CertificateType_decode_ber;
der_type_encoder_f CertificateType_encode_der;
xer_type_decoder_f CertificateType_decode_xer;
xer_type_encoder_f CertificateType_encode_xer;
oer_type_decoder_f CertificateType_decode_oer;
oer_type_encoder_f CertificateType_encode_oer;
per_type_decoder_f CertificateType_decode_uper;
per_type_encoder_f CertificateType_encode_uper;

#ifdef __cplusplus
}
#endif

#endif	/* _CertificateType_H_ */
#include "asn_internal.h"
