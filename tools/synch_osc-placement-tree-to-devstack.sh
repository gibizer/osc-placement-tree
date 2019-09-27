# run at the git repo root in the devstack VM

rsync -avz --delete --progress --exclude '.stestr' --exclude '.tox' --exclude '*.pyc' --exclude '.testrepository' gibizer@192.168.142.1:/home/gibizer/upstream/git/osc-placement-tree ../

sudo pip install . --upgrade --no-deps
