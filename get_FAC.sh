#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_FAC_SA.py
python get_FAC_SA.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated