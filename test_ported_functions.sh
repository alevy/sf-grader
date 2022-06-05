SNAPFAAS=https://api.github.com/repos/princeton-sns/snapfaas/tarball/faasten
IMAGES=https://api.github.com/repos/princeton-sns/snapfaas-images/tarball/faasten
WD=$(dirname $(realpath $0))
cd $WD

echo '***********************************'
echo '*    building faasten binaries    *'
echo '***********************************'
mkdir -p snapfaas
curl -sL -H "Accept: application/vnd.github.v3+json" $SNAPFAAS --output snapfaas.tgz
tar xzf snapfaas.tgz --strip-components=1 -C snapfaas
cd snapfaas/snapfaas; cargo build --bins; cd $WD
export PATH=snapfaas/target/debug:$PATH
if [ ! command -v sffs 2>/dev/null ] || [ ! command -v singlevm 2>/dev/null ] || [ ! command -v firerunner 2>/dev/null ]; then
    exit 1
fi

echo '************************'
echo '*    getting images    *'
echo '************************'
# download the uncompressed kernel
cp snapfaas/resources/images/vmlinux-4.20.0 . 
# build the python3.ext4
mkdir -p rootfs
curl -sL -H "Accept: application/vnd.github.v3+json" $IMAGES | \
tar xzf - -C rootfs --strip-components=2 --wildcards '*/rootfs/common' '*/rootfs/faasten'
cd rootfs/faasten; ./mk_rtimage.sh python3 ../../python3.ext4; cd $WD 
if [ ! -f python3.ext4 ] || [ ! -f vmlinux-4.20.0 ]; then
    exit 1
fi

echo '*****************'
echo '*    testing    *'
echo '*****************'
make clean
make prepfs
make run/go_grader
make run/grades

echo
echo '**************************************'
echo '*    cating function output files    *'
echo '**************************************'
sffs cat /go_grader/user/submission/test_results.jsonl
sffs cat /grades/user/example/grade.json

#echo '*********************'
#echo '*    cleaning up    *'
#echo '*********************'
#rm -r snapfaas rootfs
#rm vmlinux-4.20.0
#rm python3.ext4
