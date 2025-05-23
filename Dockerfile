FROM python:3.10-slim

LABEL maintainer="Ladybug Tools" email="info@ladybug.tools"

ARG OPENSTUDIO_VERSION
ARG OPENSTUDIO_FILENAME
ARG LBT_MEASURES_FILENAME
ARG IRONBUG_FILENAME

ENV HOME_PATH='/home/ladybugbot'
ENV LBT_PATH="${HOME_PATH}/ladybug_tools"
ENV LIBRARY_PATH="${HOME_PATH}/lib"
ENV LOCAL_OPENSTUDIO_PATH="${LBT_PATH}/openstudio"
ENV RUN_PATH="${HOME_PATH}/run"
ENV SIM_PATH="${RUN_PATH}/simulation"
ENV PATH="${HOME_PATH}/.local/bin:${PATH}"

# Create non-root user
RUN adduser ladybugbot --uid 1000 --disabled-password --gecos ""
USER ladybugbot
WORKDIR ${HOME_PATH}
RUN mkdir -p ${LOCAL_OPENSTUDIO_PATH} \
    && touch ${LBT_PATH}/config.json \
    && mkdir -p ${SIM_PATH}

# Expects an untarred OpenStudio download in the build context
COPY ${OPENSTUDIO_FILENAME}/usr/local/openstudio-${OPENSTUDIO_VERSION}/EnergyPlus \
    ${LOCAL_OPENSTUDIO_PATH}/EnergyPlus

COPY ${OPENSTUDIO_FILENAME}/usr/local/openstudio-${OPENSTUDIO_VERSION}/bin \
    ${LOCAL_OPENSTUDIO_PATH}/bin

COPY ${OPENSTUDIO_FILENAME}/usr/local/openstudio-${OPENSTUDIO_VERSION}/lib \
    ${LOCAL_OPENSTUDIO_PATH}/lib

# Add lbt-measures to the ladybug_tools folder
# https://github.com/ladybug-tools/lbt-measures
COPY ${LBT_MEASURES_FILENAME}/lib \
    ${LBT_PATH}/resources/measures

# Add ironbug to the ladybug_tools folder
# https://github.com/MingboPeng/Ironbug
COPY ${IRONBUG_FILENAME} \
    ${LBT_PATH}/grasshopper/ironbug

# Install honeybee-energy
COPY honeybee_energy ${LIBRARY_PATH}/honeybee_energy
COPY .git ${LIBRARY_PATH}/.git
COPY setup.py ${LIBRARY_PATH}
COPY setup.cfg ${LIBRARY_PATH}
COPY requirements.txt ${LIBRARY_PATH}
COPY standards-requirements.txt ${LIBRARY_PATH}
COPY openstudio-requirements.txt ${LIBRARY_PATH}
COPY README.md ${LIBRARY_PATH}
COPY LICENSE ${LIBRARY_PATH}

USER root

# install dotnet package
RUN apt-get update \
    && apt-get -y install --no-install-recommends wget\
    && wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb

RUN apt-get update \
    && apt-get -y install --no-install-recommends git \
    # EnergyPlus dynamically links to libx11
    && apt-get -y install libx11-6 libgomp1 aspnetcore-runtime-7.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir setuptools wheel \
    && pip3 install --no-cache-dir ${LIBRARY_PATH}[standards,openstudio] \
    && apt-get -y --purge remove git \
    && apt-get -y clean \
    && apt-get -y autoremove \
    && rm -rf ${LIBRARY_PATH}/.git \
    && chown -R ladybugbot ${HOME_PATH}

USER ladybugbot
# Set working directory
WORKDIR ${RUN_PATH}
