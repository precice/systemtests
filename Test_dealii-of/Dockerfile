# System testing preCICE with openfoam-adapter

# Using latest preCICE from dockerhub.com
ARG from=precice/precice:latest
FROM $from

USER root
ENV USER=root

# Install dependecies
RUN apt-get -qq update && apt-get -qq install \
    software-properties-common \
    wget apt-transport-https \
    libyaml-cpp-dev && \
    rm -rf /var/lib/apt/lists/*

RUN add-apt-repository "http://dl.openfoam.org/ubuntu dev"
RUN sh -c "wget -O - http://dl.openfoam.org/gpg.key | apt-key add -"
RUN add-apt-repository http://dl.openfoam.org/ubuntu && apt update
RUN apt-get -y install openfoam4 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building openfoam-adapter
WORKDIR /
RUN git clone https://github.com/precice/openfoam-adapter.git
WORKDIR /openfoam-adapter
RUN . /opt/openfoam4/etc/bashrc && ./Allwmake

COPY --from=precice/deal.ii  /root/dealii/ /root/dealii/

WORKDIR /
RUN git clone https://github.com/precice/dealii-adapter.git
RUN cd dealii-adapter && \
    cmake -DDEAL_II_DIR=$HOME/dealii -DCMAKE_BUILD_TYPE=Release . && \
    make -j $(nproc)
# Simulating

# Downloading tutorials, switch and copy parameters 
WORKDIR /
RUN git clone https://github.com/precice/tutorials.git && \
    cd tutorials &&  \
    cp /dealii-adapter/coupled_elasto_dynamics /tutorials/FSI/flap_perp/OpenFOAM-deal.II/Solid && \
    # adjust controldict, since we are runnning on older solver 
    sed -i '/application     pimpleFoam/d; s/\/\/ application     pimpleDyMFoam/application    pimpleDyMFoam/g' \
    /tutorials/FSI/flap_perp/OpenFOAM-deal.II/Fluid/system/controlDict


WORKDIR  /tutorials/FSI/flap_perp/OpenFOAM-deal.II/
RUN . /opt/openfoam4/etc/bashrc; ./Allrun

# Copy only fluid output since solid is too large
WORKDIR /
RUN mkdir Output && \
     cp -r /tutorials/FSI/flap_perp/OpenFOAM-deal.II/Fluid /Output/
