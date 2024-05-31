/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "ITS-Container"
 * 	found in "asn1/TS102894-2v131-CDD.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_PtActivationType_H_
#define	_PtActivationType_H_


#include "asn_application.h"

/* Including external dependencies */
#include "NativeInteger.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum PtActivationType {
	PtActivationType_undefinedCodingType	= 0,
	PtActivationType_r09_16CodingType	= 1,
	PtActivationType_vdv_50149CodingType	= 2
} e_PtActivationType;

/* PtActivationType */
typedef long	 PtActivationType_t;

/* Implementation */
extern asn_per_constraints_t asn_PER_type_PtActivationType_constr_1;
extern asn_TYPE_descriptor_t asn_DEF_PtActivationType;
asn_struct_free_f PtActivationType_free;
asn_struct_print_f PtActivationType_print;
asn_constr_check_f PtActivationType_constraint;
ber_type_decoder_f PtActivationType_decode_ber;
der_type_encoder_f PtActivationType_encode_der;
xer_type_decoder_f PtActivationType_decode_xer;
xer_type_encoder_f PtActivationType_encode_xer;
oer_type_decoder_f PtActivationType_decode_oer;
oer_type_encoder_f PtActivationType_encode_oer;
per_type_decoder_f PtActivationType_decode_uper;
per_type_encoder_f PtActivationType_encode_uper;

#ifdef __cplusplus
}
#endif

#endif	/* _PtActivationType_H_ */
#include "asn_internal.h"
