.PHONY:
	local

ACCESS_KEY=`cat blobstorage_access_key.txt`

help:
	cat Makefile

createwebjob:
	rm cleanup_webjob.zip; zip -r cleanup_webjob.zip cleanup_blobstorage.py azure 

cleanup:
	export APPSETTING_storage_access_key=$(ACCESS_KEY); python cleanup_blobstorage.py

local:
	export APPSETTING_storage_access_key=$(ACCESS_KEY); export PYTHONPATH=env/Scripts/; python myapp.py

deploy:
	git push azure master

make restart:
	azure site restart send2geoadmin

