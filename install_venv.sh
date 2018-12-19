#!/usr/bin/env bash

virtualenv -q -p `which python3` PyUBCG
PyUBCG/bin/pip install -r requirements.txt

echo "#!/usr/bin/env bash" > venv.sh
echo "source PyUBCG/bin/activate" >> venv.sh
chmod +x venv.sh
