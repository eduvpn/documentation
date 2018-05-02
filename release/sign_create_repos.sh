#!/bin/sh

(
    # Sign RPMs
    rpm --addsign ${RPM_DIR}/unsigned/* ${SRPM_DIR}/unsigned/*
    cp ${RPM_DIR}/unsigned/* "${RPM_DIR}/"
    cp ${SRPM_DIR}/unsigned/* "${SRPM_DIR}/"
    rm -rf "${RPM_DIR}/unsigned" "${SRPM_DIR}/unsigned"

    # Create Repositories
    cd "${RPM_DIR}" || exit
    createrepo_c .
    cd "${SRPM_DIR}" || exit
    createrepo_c .
)
