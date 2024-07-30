export CURRENT_DIR=`dirname $(readlink -f $0)`
export PRJ_DIR=`dirname $CURRENT_DIR`
cd $PRJ_DIR

killall -9 python qemu-system-x86_64
. env/bin/activate


python manage.py delete

python manage.py braz
python manage.py hand
python manage.py prime
python manage.py fivek
python manage.py rev
python manage.py sexmax
python manage.py vip
python manage.py whorny
python manage.py update_conf