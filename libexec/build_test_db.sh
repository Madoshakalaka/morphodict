# should be called from pipfile

# -i makes it interactive, ask user to comfirm before he deletes the database
# "$@" passes extra arguments to subcommand build-test-db

DB_FILE=CreeDictionary/test_db.sqlite3
if [ -f "$DB_FILE" ]; then
  rm -i $DB_FILE
fi

set -e

echo "Creating test_db.sqlite3 from scratch..."

pipenv run python CreeDictionary/manage.py migrate API 0001

manage-db build-test-db "$@"

pipenv run python CreeDictionary/manage.py migrate
