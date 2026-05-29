#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

#include <ctype.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#include "ek_debug.h" /* Debugging */
#include "kermit.h" /* Kermit symbols and data structures */

#define IBUFLEN 1024 /* File input buffer size */
#define OBUFLEN 1024 /* File output buffer size */

static UCHAR o_buf[OBUFLEN + 8]; /* File output buffer */
static UCHAR i_buf[IBUFLEN + 8]; /* File output buffer */

static struct k_data k; /* Kermit data structure */
static struct k_response r; /* Kermit response structure */

static const int ftype = 1; /* Global file type 0=text 1=binary*/
static const int parity = P_PARITY; /* Parity */
static const int check = 1;

int kermit_send(char **filelist)
{
	int status = KX_OK;

	UCHAR *inbuf;
	short r_slot;
	int rx_len;

	ek_debug(DB_OPN, "debug.log", 0, 0);
	ek_debug(DB_MSG, "Initializing...", 0, 0);

	/*  Fill in parameters for this run */

	k.xfermode = 0; /* Text/binary automatic/manual  */
	k.binary = ftype; /* 0 = text, 1 = binary */
	k.parity = parity; /* Communications parity */
	k.ikeep = 0; /* Keep incompletely received files */
	k.filelist = filelist; /* List of files to send (if any) */
	k.cancel = 0; /* Not canceled yet */

	k.bct = check; /* Block check type */
	/* Force Type 3 Block Check (16-bit CRC) on all packets, or not */
	k.bctf = (check == 5) ? 1 : 0;

	/*  Fill in the i/o pointers  */

	k.zinbuf = i_buf; /* File input buffer */
	k.zinlen = IBUFLEN; /* File input buffer length */
	k.zincnt = 0; /* File input buffer position */
	k.obuf = o_buf; /* File output buffer */
	k.obuflen = OBUFLEN; /* File output buffer length */
	k.obufpos = 0; /* File output buffer position */

	/* Fill in function pointers */
	k.rxd = readpkt; /* for reading packets */
	k.txd = tx_data; /* for sending packets */
	k.openf = openfile; /* for opening files */
	k.finfo = fileinfo; /* for getting file info */
	k.readf = readfile; /* for reading files */
	k.writef = writefile; /* for writing to output file */
	k.closef = closefile; /* for closing files */

	k.dbf = ek_dodebug; /* for debugging */

	status = KX_OK; /* Initial kermit status */

	/* Initialize Kermit protocol */
	status = kermit(K_INIT, &k, 0, 0, "", &r);

	if (status == KX_ERROR)
		return status;

	// fprintf(stderr, "[kermit_send] init: status=%d version=%s\n", status, k.version);

	/* Send files */
	status = kermit(K_SEND, &k, 0, 0, "", &r);

	while (status != X_DONE) {
		inbuf = getrslot(&k, &r_slot); /* Allocate a window slot */
		rx_len = k.rxd(&k, inbuf, P_PKTLEN); /* Try to read a packet */
		// ek_debug(DB_PKT, "main packet", &(k.ipktbuf[0][r_slot]), rx_len);

		if (rx_len < 1) { /* No data was read */
			freerslot(&k, r_slot); /* So free the window slot */
			if (rx_len < 0) /* If there was a fatal error */
				return EK_FAILURE; /* give up */

			/* This would be another place to dispatch to another task */
			/* while waiting for a Kermit packet to show up. */
		}
		/* Handle the input */

		switch (status = kermit(K_RUN, &k, r_slot, rx_len, "", &r)) {
		case KX_OK:
			// fprintf(stderr, "[kermit_send] KX_OK\n");
			// ek_debug(DB_LOG, "NAME", r.filename ? r.filename : (UCHAR *)"(NULL)", 0);
			// ek_debug(DB_LOG, "DATE", r.filedate ? r.filedate : (UCHAR *)"(NULL)", 0);
			// ek_debug(DB_LOG, "SIZE", 0, r.filesize);
			// ek_debug(DB_LOG, "STATE", 0, r.status);
			// ek_debug(DB_LOG, "SOFAR", 0, r.sofar);
			/* Maybe do other brief tasks here... */
			continue; /* Keep looping */
		case X_DONE:
			// fprintf(stderr, "[kermit_send] X_DONE\n");
			break; /* Finished */
		case KX_ERROR:
			fprintf(stderr, "[kermit_send] KX_ERROR status=%d\n", status);
			return -1;
		}
	}
	return 0;
}
