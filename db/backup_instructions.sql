# Logical backup of just this database
pg_dump -U youruser -d online_store_db > online_store_backup.sql

# Or with custom (compressed) format:
pg_dump -U youruser -F c -d online_store_db -f online_store_backup.dump
# Create empty DB first
createdb -U youruser online_store_db_restored

# Restore from plain SQL
psql -U youruser -d online_store_db_restored -f online_store_backup.sql

# Restore from custom dump
pg_restore -U youruser -d online_store_db_restored online_store_backup.dump