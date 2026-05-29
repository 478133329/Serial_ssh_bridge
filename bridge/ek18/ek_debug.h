#ifndef __DEBUG_H__
#define __DEBUG_H__

#define EK_DEBUG

/* ek_dodebug() function codes... */
#define DB_OPN 1			/* Open log */
#define DB_LOG 2			/* Write label+string or int to log */
#define DB_MSG 3			/* Write message to log */
#define DB_CHR 4			/* Write label + char to log */
#define DB_PKT 5			/* Record a Kermit packet in log */
#define DB_CLS 6			/* Close log */

#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

#ifdef EK_DEBUG				/* Debugging included... */

#define ek_trace(fmt, ...) fprintf(debug_log, "[ek_trace] " fmt, ##__VA_ARGS__)

/*
  ek_dodebug() is accessed throug a macro that:
   . Coerces its args to the required types.
   . Accesses ek_dodebug() directly or thru a pointer according to context.
   . Makes it disappear entirely if EK_DEBUG not defined.
*/
#ifdef KERMIT_C
/* In kermit.c we debug only through a function pointer */
#define ek_debug(a,b,c,d) \
if(*(k->dbf))(*(k->dbf))(a,(UCHAR *)b,(UCHAR *)c,(long)(d))

#else  /* KERMIT_C */
/* Elsewhere we can call the debug function directly */
#define ek_debug(a,b,c,d) ek_dodebug(a, b, c, (long)(d))
#endif /* KERMIT_C */

#else  /* Debugging not included... */

#define ek_debug(a,b,c,d)

#endif /* EK_DEBUG */


#endif /* __DEBUG_H__ */
