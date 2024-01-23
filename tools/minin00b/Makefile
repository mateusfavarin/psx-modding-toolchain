PREFIX ?= mipsel-none-elf
FORMAT ?= elf32-littlemips

CC  = $(PREFIX)-gcc
CXX = $(PREFIX)-g++
AR  = $(PREFIX)-ar

ARCHFLAGS = -march=mips1 -mabi=32 -EL -fno-pic -mno-shared -mno-abicalls -mfp32
ARCHFLAGS += -fno-stack-protector -nostdlib -ffreestanding

CPPFLAGS += -O2 -Iinclude/
CPPFLAGS += -mno-gpopt -fomit-frame-pointer -ffunction-sections -fdata-sections
CPPFLAGS += -fno-builtin -fno-strict-aliasing -Wno-attributes -Wextra
CPPFLAGS += $(ARCHFLAGS)
CXXFLAGS += -fno-exceptions -fno-rtti

all: libc.a psxcd.a psxetc.a psxgpu.a psxgte.a psxpress.a psxsio.a psxspu.a psxapi.a

libc.a: libc_misc.o libc_scanf.o libc_string.o libc_vsprintf.o libc_clz.o libc_memset.o libc_setjmp.o
	$(AR) rcs lib/$@ $^

psxcd.a: psxcd_cdread.o psxcd_common.o psxcd_isofs.o psxcd_misc.o
	$(AR) rcs lib/$@ $^

psxetc.a: psxetc_interrupts.o
	$(AR) rcs lib/$@ $^

psxgpu.a: psxgpu_common.o psxgpu_drawing.o psxgpu_env.o psxgpu_font.o psxgpu_image.o
	$(AR) rcs lib/$@ $^

psxgte.a: psxgte_isin.o psxgte_matrixc.o psxgte_initgeom.o psxgte_matrixs.o psxgte_squareroot.o psxgte_vector.o
	$(AR) rcs lib/$@ $^

psxpress.a: psxpress_mdec.o psxpress_vlcc.o psxpress_vlc2.o psxpress_vlcs.o
	$(AR) rcs lib/$@ $^

psxsio.a: psxsio_sio.o psxsio_tty.o
	$(AR) rcs lib/$@ $^

psxspu.a: psxspu_common.o
	$(AR) rcs lib/$@ $^

psxapi.a: psxapi_drivers.o psxapi_fs.o psxapi_stdio.o psxapi_sys.o psxapi__syscalls.o
	$(AR) rcs lib/$@ $^

libc_misc.o: libc/misc.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

libc_scanf.o: libc/scanf.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

libc_string.o: libc/string.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

libc_vsprintf.o: libc/vsprintf.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxcd_cdread.o: psxcd/cdread.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxcd_common.o: psxcd/common.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxcd_isofs.o: psxcd/isofs.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxcd_misc.o: psxcd/misc.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxetc_interrupts.o: psxetc/interrupts.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgpu_common.o: psxgpu/common.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgpu_drawing.o: psxgpu/drawing.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgpu_env.o: psxgpu/env.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgpu_font.o: psxgpu/font.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgpu_image.o: psxgpu/image.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgte_isin.o: psxgte/isin.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgte_matrixc.o: psxgte/matrix.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxpress_mdec.o: psxpress/mdec.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxpress_vlcc.o: psxpress/vlc.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxpress_vlc2.o: psxpress/vlc2.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxsio_sio.o: psxsio/sio.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxsio_tty.o: psxsio/tty.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxspu_common.o: psxspu/common.c
	$(CC) $(CPPFLAGS) -c -o $@ $^

libc_clz.o: libc/clz.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

libc_memset.o: libc/memset.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

libc_setjmp.o: libc/setjmp.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxapi_drivers.o: psxapi/drivers.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxapi_fs.o: psxapi/fs.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxapi_stdio.o: psxapi/stdio.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxapi_sys.o: psxapi/sys.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxapi__syscalls.o: psxapi/_syscalls.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgte_initgeom.o: psxgte/initgeom.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgte_matrixs.o: psxgte/matrix.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgte_squareroot.o: psxgte/squareroot.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxgte_vector.o: psxgte/vector.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

psxpress_vlcs.o: psxpress/vlc.s
	$(CC) $(CPPFLAGS) -c -o $@ $^

objclean:
	rm *.o

clean:
	rm *.o lib/*.a