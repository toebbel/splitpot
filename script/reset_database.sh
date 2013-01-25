if [ -f resource/splitpotDB.sqlite ]
then
    rm resource/splitpotDB.sqlite
fi
echo ".read resource/empty_db.dump" | sqlite3 resource/splitpotDB.sqlite
