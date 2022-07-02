THISDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
TOOLSDIR = $(THISDIR)../tools/

CPPFLAGS += -I$(TOOLSDIR)nugget/common/macros
CPPFLAGS += -I$(TOOLSDIR)nugget/common/crt0
CPPFLAGS += -I$(TOOLSDIR)nugget/common/syscalls

ifeq ($(USE_PSYQ),true)
CPPFLAGS += -I$(TOOLSDIR)gcc-psyq-converted/include
LDFLAGS += -L$(TOOLSDIR)gcc-psyq-converted/lib
LDFLAGS += -Wl,--start-group
LDFLAGS += -lapi
LDFLAGS += -lc
LDFLAGS += -lc2
LDFLAGS += -lcard
LDFLAGS += -lcomb
LDFLAGS += -lds
LDFLAGS += -letc
LDFLAGS += -lgpu
LDFLAGS += -lgs
LDFLAGS += -lgte
LDFLAGS += -lgun
LDFLAGS += -lhmd
LDFLAGS += -lmath
LDFLAGS += -lmcrd
LDFLAGS += -lmcx
LDFLAGS += -lpad
LDFLAGS += -lpress
LDFLAGS += -lsio
LDFLAGS += -lsnd
LDFLAGS += -lspu
LDFLAGS += -ltap
LDFLAGS += -lcd
LDFLAGS += -Wl,--end-group
endif

include $(TOOLSDIR)nugget/common.mk