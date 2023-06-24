git_root=$(git rev-parse --show-toplevel)
cd "$git_root"

docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# docker-compose exec web python manage.py createsuperuser