# Commands ####################################################################

clean:
	find . -name '*.pyc' -delete
	find . -name '*~' -delete
	find . -name '__pycache__' -type d -delete
	rm -rf .coverage build

# Tests #######################################################################

test_prospector: clean
	prospector --profile lpd --uses django

test: test_prospector
	python manage.py test
