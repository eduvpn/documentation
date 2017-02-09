# Introduction

This is an initial attempt at creating a Docker package builder. Currently we 
depend on COPR for creating the RPM packages used to install eduVPN on various
servers. 

This instead depends on the (official) Docker image of CentOS to build the 
packages, including their dependencies, if needed.

# Creating Container Image

    sudo docker build -t fkooman/eduvpn .

# Builder

Place the SRPM file you want to build in `build/in`.

     sudo docker run --rm -v $PWD/build/in:/in:Z -v $PWD/build/out:/out:Z -i -t fkooman/eduvpn /build.sh file.src.rpm

The built package(s) can be found in `build/out/RPMS/noarch`.

# TODO 

* We are currently building as _root_, that is not good;
* Sign packages;
* Do not depend on Docker registry version of CentOS, or make sure that it is 
  properly signed and vetted;
* Do not require an SRPM, but built directly from source (tar) or commit. 
