if [ -f splitpotDB_DEV.sqlite ]
then
    rm splitpotDB_DEV.sqlite
fi
echo ".read sample_db.dump" | sqlite3 splitpotDB_DEV.sqlite
