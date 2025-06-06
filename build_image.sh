#! /usr/bin/env sh
set -e

error_help="Usage: $0 CONTAINER_NAME TAG [REMOVE_DOWNLOADS=false|true]"

export CONTAINER_NAME="${1:?$error_help}"
export TAG="${2:?$error_help}"

# Get OpenStudio
export OPENSTUDIO_VERSION='3.9.0'
export OPENSTUDIO_DOWNLOAD_URL='https://github.com/NREL/OpenStudio/releases/download/v3.9.0/OpenStudio-3.9.0+c77fbb9569-Ubuntu-22.04-x86_64.tar.gz'
export OPENSTUDIO_TAR_FILENAME='openstudio.tar.gz'
export OPENSTUDIO_FILENAME='openstudio'

curl -SL -o ${OPENSTUDIO_TAR_FILENAME} ${OPENSTUDIO_DOWNLOAD_URL}
tar zxvf ${OPENSTUDIO_TAR_FILENAME}
mv OpenStudio-*-Ubuntu-*/ ${OPENSTUDIO_FILENAME}

# Get lbt-measures
export LBT_MEASURES_VERSION="0.3.1"
export LBT_MEASURES_URL="https://github.com/ladybug-tools/lbt-measures/archive/v${LBT_MEASURES_VERSION}.tar.gz"
export LBT_MEASURES_TAR='lbt-measures.tar.gz'
export LBT_MEASURES_FILENAME='measures-gem'

curl -SL -o ${LBT_MEASURES_TAR} ${LBT_MEASURES_URL}
tar zxvf ${LBT_MEASURES_TAR}
mv lbt-measures-*/ ${LBT_MEASURES_FILENAME}

# Get ironbug
export IRONBUG_VERSION="1.19.1"
export IRONBUG_URL="https://github.com/MingboPeng/Ironbug/releases/download/v${IRONBUG_VERSION}/ironbug.console.linux-${IRONBUG_VERSION}.zip"
export IRONBUG_ZIP='ironbug.console.linux.zip'
export IRONBUG_FILENAME='ironbug'

curl -SL -o ${IRONBUG_ZIP} ${IRONBUG_URL}
unzip ${IRONBUG_ZIP} -d ironbug_unzip
mv ironbug_unzip/src/Ironbug.Console/bin/Release/linux-x64 ironbug_unzip/src/Ironbug.Console/bin/Release/ironbug
mv ironbug_unzip/src/Ironbug.Console/bin/Release/ironbug ${IRONBUG_FILENAME}

# build the docker image
docker build . \
  -t $CONTAINER_NAME:$TAG \
  --build-arg OPENSTUDIO_VERSION=${OPENSTUDIO_VERSION} \
  --build-arg OPENSTUDIO_FILENAME=${OPENSTUDIO_FILENAME} \
  --build-arg LBT_MEASURES_FILENAME=${LBT_MEASURES_FILENAME} \
  --build-arg IRONBUG_FILENAME=${IRONBUG_FILENAME}

if [[ "${3}" == 'true' ]]; then
    rm -rf openstudio* honeybee-*
fi
