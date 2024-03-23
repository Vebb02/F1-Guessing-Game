git pull
pushd .
cd pages
git pull
cd ..
popd
python ./src/Main.py
pushd .
cd pages
git add .
git commit -m "Deployment"
git push
popd
pause
