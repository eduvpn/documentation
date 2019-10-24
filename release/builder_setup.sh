#!/bin/sh
KEY_IDENTITY=release@example.org
REPO_ROOT=${HOME}/repo-v2

# generate a PGP key
gpg2 --batch --quick-generate-key --passphrase '' ${KEY_IDENTITY}

mkdir -p ${HOME}/.config
cat << 'EOF' > ${HOME}/.config/mock.cfg
config_opts['nosync'] = True
# config_opts['plugin_conf']['tmpfs_enable'] = True
# config_opts['plugin_conf']['tmpfs_opts'] = {}
# config_opts['plugin_conf']['tmpfs_opts']['required_ram_mb'] = 4096
# config_opts['plugin_conf']['tmpfs_opts']['max_fs_size'] = '3072m'
# config_opts['plugin_conf']['tmpfs_opts']['mode'] = '0755'
# config_opts['plugin_conf']['tmpfs_opts']['keep_mounted'] = False
config_opts['plugin_conf']['sign_enable'] = True
config_opts['plugin_conf']['sign_opts'] = {}
config_opts['plugin_conf']['sign_opts']['cmd'] = 'rpmsign'
config_opts['plugin_conf']['sign_opts']['opts'] = '--addsign %(rpms)s'
EOF

cat << EOF > ${HOME}/.rpmmacros
%_signature gpg
%_gpg_name ${KEY_IDENTITY}
%_gpg_digest_algo sha256
EOF

gpg2 --export -a ${KEY_IDENTITY} > ${HOME}/RPM-GPG-KEY-LC

# setup the ${HOME}/rpmbuild structure (if not yet there)
rpmdev-setuptree
# clean it up if it already existed...
rpmdev-wipetree
