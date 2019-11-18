#!/usr/bin/env bash
set -ex

# check that both Git URLs are defined
if [ ! -n "${GIT_TEMPLATE}" ]; then
  echo Error: Environment variable GIT_TEMPLATE is not defined;
  exit 1;
fi

# set up the template repo
TEMPLATE_TMP_DIR=template.tmp
rm -rf ${TEMPLATE_TMP_DIR}

git clone ${GIT_TEMPLATE} ${TEMPLATE_TMP_DIR}

### clear existing files
pushd ${TEMPLATE_TMP_DIR}
git rm -r *
popd

### create the pipeline and requirements.txt file
cp template.gitlab-ci.yml "${TEMPLATE_TMP_DIR}"/.gitlab-ci.yml
cp template.requirements.txt "${TEMPLATE_TMP_DIR}"/requirements.txt

### copy other files that should be in the template repo
cp -r policies "${TEMPLATE_TMP_DIR}"/policies
cp -r ansible-policies "${TEMPLATE_TMP_DIR}"/ansible-policies
cp -r code "${TEMPLATE_TMP_DIR}"/code
cp -r playbooks "${TEMPLATE_TMP_DIR}"/playbooks
cp -r inputs "${TEMPLATE_TMP_DIR}"/inputs
cp -r templates "${TEMPLATE_TMP_DIR}"/templates
cp -r batfish "${TEMPLATE_TMP_DIR}"/batfish


### add files to git
pushd ${TEMPLATE_TMP_DIR}
git add .gitlab-ci.yml *
git commit --allow-empty -am "baseline commit"
git push --force
popd

