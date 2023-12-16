
# Update host machine built-ins
apt-get update
apt-get -y upgrade
# install dependencies
apt-get -y install build-essential curl git pkg-config cmake texinfo libmpfr-dev libisl-dev libgmp-dev libmpc-dev libtinyxml2-dev unzip wget
apt-get -y install python3 python3-pip python3-dev libgl1

cd $RUNTIME_DIR
echo $PWD
# Get the latest binary
# TODO: Stop mixing wget and curl
wget $(curl -s https://api.github.com/repos/Lameguy64/PSn00bSDK/releases/latest | grep browser_download_url | cut -d\" -f4 | grep 'linux.zip')

# Extract to the /opt folder
find . -type f -name "gcc-mipsel-none-elf-*.zip" | xargs unzip -d "/opt/gcc-mipsel-none-elf/" -q

# Add binaries to PATH
echo "Prebuilt binaries installed in /opt"