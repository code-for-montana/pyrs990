#!/bin/sh

echo "testing version agreement"
claimed=$(poetry run python -m pyrs990 --version)
actual=$(poetry version | cut -d ' ' -f 2)
if [ "$claimed" !=  "$actual" ]; then
  echo "$claimed (claimed version) and $actual (actual version) do not match"
  exit 1
else
  echo "version verified"
fi
