#!/usr/bin/env bash
# get working dir
# get token for upload
# save to file
# upload file

xml () {
  # Generate XML Reports of coverage with pytest
  echo "XML Coverage Testing"
  pytest \
    --durations=0 \
    --cov-report xml:cov.xml \
    --cov=strava_map .
}

default() {
    echo "Default Coverage Testing"
    # Default test with results to the terminal.
  pytest \
    --durations=0 \
    --cov-report term-missing \
    --cov=strava_map .
}
if test $# -eq 0
then
  default
  exit 0
fi

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "heeeelp"
      shift
      ;;
    -x|--xml)
      xml
      echo " "
      echo "Created XML report"
      echo " "
      shift
      ;;
    *)
      break
      ;;
  esac
done

# bash <(curl -Ls https://coverage.codacy.com/get.sh)
# python-codacy-coverage -r cov.xml