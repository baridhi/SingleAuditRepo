set -x
set -v
#get current date
TODAY=`date +%Y`

#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_MI.py --year $TODAY
python get_MI.py --year $TODAY

#deactivate virtualenv
deactivate
echo virtualenv deactivated
set +x
set +v