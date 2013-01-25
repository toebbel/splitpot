if [ -f resource/splitpotDB.sqlite ]
then
    DATE=$(date +"%y-%m-%d-%h-%m-%s")
    BACKUP_FILE="backup/splitpotDB.sqlite.$DATE.backup"
    echo ".dump" | sqlite3 -batch -echo resource/splitpotDB.sqlite > "$BACKUP_FILE"
    echo "writing backup to $BACKUP_FILE"
fi
