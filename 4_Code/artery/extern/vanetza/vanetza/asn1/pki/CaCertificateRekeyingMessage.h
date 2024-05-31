/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "EtsiTs102941MessagesCa"
 * 	found in "asn1/TS102941v131-MessagesCa.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_CaCertificateRekeyingMessage_H_
#define	_CaCertificateRekeyingMessage_H_


#include "asn_application.h"

/* Including external dependencies */
#include "EtsiTs103097Data-Signed.h"

#ifdef __cplusplus
extern "C" {
#endif

/* CaCertificateRekeyingMessage */
typedef EtsiTs103097Data_Signed_55P1_t	 CaCertificateRekeyingMessage_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_CaCertificateRekeyingMessage;
asn_struct_free_f CaCertificateRekeyingMessage_free;
asn_struct_print_f CaCertificateRekeyingMessage_print;
asn_constr_check_f CaCertificateRekeyingMessage_constraint;
ber_type_decoder_f CaCertificateRekeyingMessage_decode_ber;
der_type_encoder_f CaCertificateRekeyingMessage_encode_der;
xer_type_decoder_f CaCertificateRekeyingMessage_decode_xer;
xer_type_encoder_f CaCertificateRekeyingMessage_encode_xer;
oer_type_decoder_f CaCertificateRekeyingMessage_decode_oer;
oer_type_encoder_f CaCertificateRekeyingMessage_encode_oer;
per_type_decoder_f CaCertificateRekeyingMessage_decode_uper;
per_type_encoder_f CaCertificateRekeyingMessage_encode_uper;

#ifdef __cplusplus
}
#endif

#endif	/* _CaCertificateRekeyingMessage_H_ */
#include "asn_internal.h"