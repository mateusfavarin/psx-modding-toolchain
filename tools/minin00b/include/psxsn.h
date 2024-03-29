/*
 * PSn00bSDK kernel API library (host file access)
 * (C) 2023 spicyjpeg - MPL licensed
 */

/**
 * @file psxsn.h
 * @brief Host file access API header
 *
 * @details This header provides stubs for the PCDRV API, which grants read and
 * write access to a directory on the host's filesystem when the executable is
 * running on an emulator or through a debugger that supports the PCDRV
 * protocol, such as Unirom or pcsx-redux. These functions are completely
 * separate and independent from the file APIs provided by the BIOS and do not
 * register any device drivers.
 *
 * Note that in the official SDK these functions are provided by libsn, while
 * in PSn00bSDK they are part of libpsxapi.
 *
 * IMPORTANT: as these function rely on break instructions internally, calling
 * them on real hardware without a PCDRV handler installed or on an emulator
 * that does not support the API will result in an uncaught break exception,
 * which will cause the BIOS to get stuck in an infinite loop.
 */

#pragma once

#include <stddef.h>

typedef enum {
	PCDRV_MODE_READ       = 0,
	PCDRV_MODE_WRITE      = 1,
	PCDRV_MODE_READ_WRITE = 2
} PCDRV_OpenMode;

typedef enum {
	PCDRV_SEEK_SET = 0,
	PCDRV_SEEK_CUR = 1,
	PCDRV_SEEK_END = 2
} PCDRV_SeekMode;

#ifdef __cplusplus
extern "C" {
#endif

int PCinit(void);
int PCcreat(const char *path);
int PCopen(const char *path, PCDRV_OpenMode mode);
int PCclose(int fd);
int PCread(int fd, void *data, size_t length);
int PCwrite(int fd, const void *data, size_t length);
int PClseek(int fd, int offset, PCDRV_SeekMode mode);

#ifdef __cplusplus
}
#endif
