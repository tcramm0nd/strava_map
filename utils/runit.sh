git_root=$(git rev-parse --show-toplevel)
cd "$git_root"

docker-compose up -d --build