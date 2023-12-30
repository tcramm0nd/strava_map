git_root=$(git rev-parse --show-toplevel)
cd "$git_root/strava_map/strava_map_api/migrations"

find ./ -name "*.py" | xargs rm -r
touch __init__.py

cd $git_root

docker volume rm strava_map_postgres_data
docker-compose up -d --build
# docker-compose exec web python strava_map/manage.py makemigrations
# docker-compose exec web python strava_map/manage.py migrate