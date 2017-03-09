FROM centos:latest

RUN yum -y update
RUN yum -y install epel-release
RUN yum -y install fedora-packager
RUN yum clean all

RUN mkdir /rpm
COPY dkr/.rpmmacros /root/.rpmmacros
COPY dkr/eduVPN.repo /etc/yum.repos.d/eduVPN.repo
COPY dkr/build.sh /build.sh
