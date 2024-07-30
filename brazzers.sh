export CURRENT_DIR=`dirname $(readlink -f $0)`
export PRJ_DIR=`dirname $CURRENT_DIR`
cd $PRJ_DIR

killall -9 python qemu-system-x86_64
. env/bin/activate


python manage.py delete
python manage.py update_conf