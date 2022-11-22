##########################################################################################
#   build.sh
##########################################################################################
make clean
python -m venv env
. ./env/bin/activate
pip install --upgrade pip
pip install .
pip install -r test-requirements.txt

make build
make test
make release

GIT_VERSION_NUMBER=$(python setup.py --version)
echo REPO_VERSION=$GIT_VERSION_NUMBER > repo_version.txt
