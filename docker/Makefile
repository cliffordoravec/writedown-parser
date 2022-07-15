BASE_COMMAND=docker run --rm -it -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONUNBUFFERED=1 -e PYTHONPATH=/app/src -e EDITOR=vim -v `pwd`/../:/app -w /app writedown

image:
	docker build -t writedown -f Dockerfile ../

#installer-spec:
#	$(BASE_COMMAND) pyi-makespec -F -n writedown --collect-all writedown src/writedown/cli.py

installer-linux:
	$(BASE_COMMAND) pyinstaller --distpath dist/linux writedown.spec

# TODO: Use GitHub Actions for Windows and MacOS targets?

# Run from a Windows box:
#installer-windows:

# Run from a MacOS box:
#installer-macos:

test-installer-linux:
	$(BASE_COMMAND) dist/linux/writedown

# make run arguments=<arguments>
run:
	$(BASE_COMMAND) python -m writedown.cli $(arguments)

test:
	$(BASE_COMMAND) python -m unittest discover tests --verbose

docs:
	$(BASE_COMMAND) bash -c 'rm -rf ./docs && pdoc writedown -o ./docs'

clean:
	$(BASE_COMMAND) bash -c 'rm -rf ./build ./dist'
