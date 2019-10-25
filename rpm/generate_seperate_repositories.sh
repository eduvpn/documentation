#!/bin/sh

REPO_DIR=${HOME}/repo-SPEC
rm -rf ${REPO_DIR}

for SPEC in $(ls *.spec)
do
	REPO_NAME=$(basename ${SPEC} .spec)
	echo ${REPO_NAME}
 	mkdir -p ${REPO_DIR}/${REPO_NAME}/SPECS
	mkdir -p ${REPO_DIR}/${REPO_NAME}/SOURCES
	cp ${REPO_NAME}.spec ${REPO_DIR}/${REPO_NAME}/SPECS
	cp ${REPO_NAME}* ${REPO_DIR}/${REPO_NAME}/SOURCES
	cp minisign-8466FFE127BCDC82.pub ${REPO_DIR}/${REPO_NAME}/SOURCES 
	rm ${REPO_DIR}/${REPO_NAME}/SOURCES/*.spec
	(
		cd ${REPO_DIR}/${REPO_NAME}
		git init
		git add .
		git commit -a -m 'initial commit'
		git remote add origin git@git.tuxed.net:rpm/${REPO_NAME}
		git push origin master
		git branch v2
		git push origin v2
	)
done
