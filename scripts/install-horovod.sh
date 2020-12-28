
cd horovod
git pull origin master
pip3 uninstall -y horovod
rm -rf build/ dist/
HOROVOD_WITH_PYTORCH=1 HOROVOD_WITHOUT_TENSORFLOW=1  HOROVOD_GPU_OPERATIONS=NCCL python setup.py install