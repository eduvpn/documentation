#!/bin/sh

set -e

SPEC_FILE=${1}
NAME=$(basename "${SPEC_FILE}" .spec)
GIT_COMMIT=$(grep -E '%global\s*commit0' "${SPEC_FILE}" | awk '{print $3}')
GIT_SHORTCOMMIT=${GIT_COMMIT:0:7}
GIT_REPO=$(grep -E 'URL:' "${SPEC_FILE}" | awk '{print $2}')
GIT_NAME=$(echo "${GIT_REPO}" | sed  -e 's#.*/##')
TEMP_DIR=$(mktemp --dir)
SPEC_DIR=$(pwd)

cd "${TEMP_DIR}"
(
    echo "Cloning git repo..."
    git clone "${GIT_REPO}"
    (
        cd "${GIT_NAME}"
        git checkout "${GIT_COMMIT}"
        git verify-commit "${GIT_COMMIT}"
    )

    TAR_DIR="${GIT_NAME}-${GIT_COMMIT}"
    mv "${GIT_NAME}" "${TAR_DIR}"
    TAR_FILE="${SPEC_DIR}/${NAME}-${GIT_SHORTCOMMIT}.tar.gz"
    [ -e "${TAR_FILE}" ] && rm -f "${TAR_FILE}"
    tar --exclude-vcs -czf "${TAR_FILE}" "${TAR_DIR}"
    chmod 0644 "${TAR_FILE}"
)
rm -rf "${TEMP_DIR}"
