FROM centos:latest

RUN yum -y update
RUN yum -y install epel-release
RUN yum -y install fedora-packager
RUN yum clean all

COPY build.sh /build.sh
