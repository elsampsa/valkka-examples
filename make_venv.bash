#!/bin/bash
rm -r -f venv
virtualenv --no-site-packages -p python3 venv

# # lets make the dist-packages visible to the virtualenv:
# echo "/usr/lib/python3/dist-packages" > venv/lib/python3.6/site-packages/dist.pth
python3 -c "from distutils import sysconfig; print(sysconfig.get_python_lib())" > venv/lib/python3.6/site-packages/dist.pth 

echo
echo "> Do this"
echo "cd venv"
echo "source bin/activate"
echo "export PYTHONPATH="
echo "> To exit, type"
echo "deactivate"
echo "cd .."
echo
