# run at the git repo root in the devstack VM

rsync -avz --delete --progress --exclude '.stestr' --exclude '.tox' --exclude '*.pyc' --exclude '.testrepository' ebalgib@100.109.0.1:/home/ebalgib/upstream/git/osc-placement-tree ../

sudo pip install . --upgrade --no-deps
