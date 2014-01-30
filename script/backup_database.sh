if [ -f resource/splitpotDB.sqlite ]
then
    DATE=$(date +"%Y-%m-%d_%H-%M-%S")
    BACKUP_FILE="backup/splitpotDB.sqlite.$DATE.backup"
    echo ".dump" | sqlite3 -batch -echo resource/splitpotDB.sqlite > $BACKUP_FILE
    tar -cpzf $BACKUP_FILE.tar.gz $BACKUP_FILE
    rm $BACKUP_FILE
    echo "writing backup to $BACKUP_FILE"
fi
