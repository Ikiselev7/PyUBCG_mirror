#!/usr/bin/env bash

virtualenv -q -p `which python3` pyubcg_venv
pyubcg_venv/bin/pip install -r requirements.txt

echo "#!/usr/bin/env bash" > venv.sh
echo "source pyubcg_venv/bin/activate" >> venv.sh
chmod +x venv.sh
