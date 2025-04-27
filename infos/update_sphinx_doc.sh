source .env
#ls $WD/src/docs/*.rst | grep -v $WD/src/docs/index.rst | xargs rm
sphinx-apidoc -o $WD/src/docs/ $WD/src/ --force --separate --tocfile index
sed -i '' '/:members:/a\
   :special-members: __init__, __next__, __iter__, __call__
' $WD/src/docs/*.rst
cd $WD/src/docs/
make clean
make html
open $WD/src/docs/_build/html/index.html