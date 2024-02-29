ifeq ($(OS),Windows_NT)
  PYTHON = python
else ifeq ($(shell which python3),)
  PYTHON = python
else
  PYTHON = python3
endif

THISDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
TOOLSDIR = $(THISDIR)../tools/

CPPFLAGS += -I$(TOOLSDIR)nugget/common/macros/
CPPFLAGS += -I$(GAMEINCLUDEDIR)
CPPFLAGS += -I$(MODDIR)

ifeq ($(USE_MININOOB),true)
  CPPFLAGS += -I$(TOOLSDIR)minin00b/include/
  LDFLAGS += -L$(TOOLSDIR)minin00b/lib/
  LDFLAGS += -Wl,--start-group
  LDFLAGS += -l:libc.a
  LDFLAGS += -l:psxcd.a
  LDFLAGS += -l:psxetc.a
  LDFLAGS += -l:psxgpu.a
  LDFLAGS += -l:psxgte.a
  LDFLAGS += -l:psxpress.a
  LDFLAGS += -l:psxsio.a
  LDFLAGS += -l:psxspu.a
  LDFLAGS += -l:psxapi.a
  LDFLAGS += -Wl,--end-group
endif

ifeq ($(USE_PSYQ),true)
  CPPFLAGS += -I$(TOOLSDIR)gcc-psyq-converted/include/
  LDFLAGS += -L$(TOOLSDIR)gcc-psyq-converted/lib/
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