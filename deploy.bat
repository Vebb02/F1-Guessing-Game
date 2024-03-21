python ./src/Main.py
pushd .
cd pages
git add .
git commit -m "Deployment"
git push
popd
pause
