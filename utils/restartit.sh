git_root=$(git rev-parse --show-toplevel)
cd "$git_root/chores/migrations"

find ./ -name "*.py" | xargs rm -r
touch __init__.py

cd $git_root

docker volume rm chores_postgres_data
docker-compose up -d --build
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate