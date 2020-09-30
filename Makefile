.PHONY: publish pytest clean lint xmllint xml_validate clear-objects build test xml

build:
	./setup.py sdist && ./setup.py bdist_wheel

test: pytest lint xmllint xml_validate

xml: xmllint xml_validate

publish:
	twine upload dist/* && git push && git push --tags

clean:
	rm -rf dist/

pytest:
	pytest -xvv

lint:
	flake8 --exclude=.env,.tox,dist,docs,build,*.egg,.venv --max-line-length 99 .

xmllint:
	xmllint --noout --relaxng cacahuate/xml/process-spec.rng xml/*.xml

xml_validate:
	xml_validate xml/*.xml

clear-objects:
	python -c "from coralillo import Engine; eng=Engine(); eng.lua.drop(args=['*'])"
	mongo cacahuate --eval "db.pointer.drop()"
	mongo cacahuate --eval "db.execution.drop()"
	sudo rabbitmqctl purge_queue cacahuate_process
