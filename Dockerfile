FROM ubuntu:latest
WORKDIR /
COPY . /install-runtime/
ENV RUNTIME_DIR=/install-runtime
RUN bash /install-runtime/install_toolchain_prebuilt.sh
ENV PATH "$PATH:/opt/gcc-mipsel-none-elf/bin"
ENV PATH "$PATH:/opt/gcc-mipsel-none-elf/mipsel-none-elf/bin"
RUN pip3 install -r /install-runtime/requirements.txt