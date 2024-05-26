ifeq ($(BUILD_ID),561)
LDFLAGS += src/symbol.ld
else
LDFLAGS += src/symbol_jp.ld
endif