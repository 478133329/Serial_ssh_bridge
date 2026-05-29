# cython: language_level=3

from libc.stdlib cimport malloc, free
from libc.string cimport memset
from libc.stdint cimport uintptr_t
import logging
import random
import sys
from cpython.exc cimport PyErr_Occurred


__version__ = "v0.0.1"


cdef extern from "kermit.h":
    const char __func__[]

    int KX_ERROR = -1
    int KX_OK = 0

    int X_DONE = 3

    struct k_data:
        short parity
        short r_soh
        short r_eom
        int r_maxlen
        short s_first
        int zincnt
        unsigned char *zinbuf
        unsigned char *zinptr

    struct k_response:
        pass

    int kermit_send(char **filelist)


class S:
    uart_dl = None
    ek_flist = None


def to_bytes(v):
    if type(v) == str:
        v = v.encode("ascii")
    return v


cdef class EkFileList:
    cdef object files
    cdef char **c_filelist
    cdef size_t c_filelist_size

    def __cinit__(self, files):
        self.c_filelist = NULL
        self.c_filelist_size = 0

        self.files = [to_bytes(i) for i in files]

        self.c_filelist_size = (len(files) + 1) * sizeof(char *)
        logging.debug('[EKF] size=%d', self.c_filelist_size)
        self.c_filelist = <char **>malloc(self.c_filelist_size)
        memset(self.c_filelist, 0, self.c_filelist_size)

        for n, v in enumerate(self.files):
            logging.debug('[EKF] %r=%r', n, v)
            self.c_filelist[n] = v

    def __dealloc__(self):
        if self.c_filelist:
            logging.debug('[EKF] free')
            free(self.c_filelist)

    cdef char **get_list(self):
        return self.c_filelist


def start(uart_dl, filename):
    cdef char **c_filelist
    cdef void* pending

    logging.info("start: filename=%r", filename)

    S.uart_dl = uart_dl

    ek_flist = EkFileList([filename])
    S.ek_flist = ek_flist

    c_filelist = ek_flist.get_list()

    logging.info("kermit sending start")
    r = -1
    try:
        r = kermit_send(c_filelist)
    except Exception:
        logging.exception("kermit_send failed for %r", filename)
        raise
    # If a Python exception was raised inside a callback (readpkt/tx_data/etc.),
    # the C kermit core may return normally while leaving the exception set.
    # Avoid calling into Python (e.g. logging) while an exception is pending,
    # otherwise we can crash with SystemError: LogRecord ... exception set.
    pending = <void*>PyErr_Occurred()
    if pending != NULL:
        raise RuntimeError("kermit_send returned with pending Python exception")

    logging.info("kermit sending finished, r=%r", r)
    if r < 0:
        raise ValueError("kermit_send failed, return %r" % r)


cdef public int readpkt(k_data *k, unsigned char *buf, int buf_len) except -1:
    cdef int x = 0
    cdef int n = 0
    cdef short flag = 0
    cdef unsigned char c
    cdef unsigned char *p2 = buf
    cdef bytes py_buf

    if not buf:
        logging.error("readpkt: buf is NULL")
        return -1

    flag = n = 0 # Init local variables
    p2 = buf
    logging.debug("buf_len=%d k->r_soh=%d k->r_maxlen=%d", buf_len, k.r_soh, k.r_maxlen)

    while True:
        x = S.uart_dl.getc()

        c = <unsigned char>(x & 0x7f if k.parity else x & 0xff) # Strip parity
        if not flag and c != k.r_soh: # No start of packet yet
            continue # so discard these bytes.

        if c == k.r_soh: # Start of packet
            flag = 1 # Remember
            continue # But discard.
        elif c == k.r_eom: # Packet terminator
            buf[0] = 0 # Terminate for printing
            py_buf = p2[:n]
            logging.debug("readpkt: p2=%r", py_buf.hex())
            return n
        else: # Contents of packet
            n += 1
            if n > k.r_maxlen: # Check length
                return 0
            else:
                buf[0] = x & 0xff
                buf += 1

    logging.error("readpkt: failed")
    return -1


cdef public int tx_data(k_data *k, unsigned char *buf, int buf_len) except -1:
    cdef bytes py_buf = buf[:buf_len]
    return S.uart_dl.write(py_buf)


cdef public int openfile(k_data *k, unsigned char *path, int mode) except -1:
    logging.debug("openfile: path=%r", path)

    k.s_first = 1 # Set up for getkpt
    k.zinbuf[0] = 0 # Initialize buffer
    k.zinptr = k.zinbuf # Set up buffer pointer
    k.zincnt = 0 # and count

    return S.uart_dl.openfile(path, mode)


cdef public unsigned long fileinfo(k_data *k, unsigned char *filename,
        unsigned char *buf, int buflen, short *type, short mode) except 0:
    logging.debug("fileinfo: filename=%r", filename)

    return S.uart_dl.fileinfo(filename)


cdef public int readfile(k_data *k) except -1:
    return S.uart_dl.readfile()


cdef public int writefile(k_data *k, unsigned char *s, int n) except -1:
    logging.debug("writefile: n=%d", n)
    return KX_OK


cdef public int closefile(k_data *k, unsigned char c, int mode) except -1:
    logging.debug("closefile: c=%r mode=%r", c, mode)
    if mode in [1, 2, 3]:
        return KX_OK

    return KX_ERROR


cdef public int xerror():
    cdef int x = 0
    cdef int errorrate = 0

    if not errorrate:
        return 0

    x = random.ranint(0, 99)
    logging.debug("xerror: x=%r errorrate=%r", x, errorrate)

    return x < errorrate


cdef public int ek_dodebug(int fc, void *_label, void *_sval, long nval) except -1:
    cdef bytes label = b"..."
    cdef bytes sval = b"..."

    try:
        if _label != NULL:
            label = <char *>_label

        if _sval != NULL:
            sval = <char *>_sval

        logging.debug("[ek_dodebug] %r %r %r %r" % (fc, label, sval, nval))
        return 0
    except Exception:
        # Never allow debug callback to leave a pending exception (it can crash kermit_send).
        try:
            logging.exception("[ek_dodebug] exception fc=%r nval=%r", fc, nval)
        except Exception:
            pass
        return 0
