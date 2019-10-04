ARG from=precice/precice-ubuntu1604.home-develop
FROM $from
USER root

RUN apt-get -qq update && apt-get -qq install \
    liblapack-dev && \
    rm -rf /var/lib/apt/lists/*


ARG CACHEBUST

RUN mkdir -p /Output/Postproc

USER precice

WORKDIR /home/precice/
RUN git clone https://github.com/Eder-K/elastictube1d.git

WORKDIR /home/precice/elastictube1d/elastictube1d-cxx
RUN cmake . && make all && ./Allrun-cxx

# transfer results
USER root
RUN cp *.json *.log /Output/ && \
    cp Postproc/*.vtk /Output/Postproc/
