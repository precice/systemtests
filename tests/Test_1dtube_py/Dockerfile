ARG from=precice/precice-ubuntu1604.home-develop
FROM $from
USER root

RUN apt-get -qq update && apt-get -qq install \
    python3 python3-dev \
    libsm6 libgl1 && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    python3 get-pip.py && \
    pip install Cython mpi4py numpy enum34 matplotlib vtk

ARG CACHEBUST

RUN mkdir /Output

WORKDIR $PRECICE_ROOT/src/precice/bindings/python_future
RUN pip3 install --user .

WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN pip3 install --user .

WORKDIR /home/precice/
RUN git clone https://github.com/Eder-K/elastictube1d.git

WORKDIR /home/precice/elastictube1d


RUN ./Allrun

# transfer only VTK results
RUN cp -r VTK /Output/
