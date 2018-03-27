LTI Learner Profile Dashboard
=============================

Prerequisites
-------------

* SQLite or MySQL
* python-dev
* virtualenv

Setting up the development server
---------------------------------

1. Install python dependencies:

    ```bash
    virtualenv .virtualenv
    . .virtualenv/bin/activate
    pip install -r requirements/base.txt
    ```

1. Create `app/local_settings.py`, and set the sensitive settings:

    ```python
    SECRET_KEY = 'SET ME'
    LTI_CLIENT_KEY = 'SET ME'
    LTI_CLIENT_SECRET = 'SET ME'
    PASSWORD_GENERATOR_NONCE = 'SET ME'

    # Optional - can use default sqlite for dev
    LPD_DB_PASSWORD = 'SET ME'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'lti_lpd',
            'USER': 'lti_lpd',
            'PASSWORD': LPD_DB_PASSWORD,
        }
    }
    ```

    You can use the following script to generate secret keys:

    ```python
    #!/usr/bin/env python
    import string
    from django.utils.crypto import get_random_string
    get_random_string(64, string.hexdigits)
    ```

1. Initialize app: Run migrations and create a superuser.

    ```bash
    ./manage.py migrate
    ./manage.py createsuperuser
    ```

1. Run server:

    ```bash
    # Use port 8080 to avoid conflicting with LMS/CMS ports
    ./manage.py runserver 8080
    ```

1. Run tests, and view coverage report:

    ```bash
    pip install -r requirements/test.txt
    coverage run --source=. manage.py test
    coverage report -m
    ```

Using LPD with Open edX
-----------------------

1. If you haven't already, add `"lti_consumer"` to "Settings" > "Advanced Settings" > "Advanced Module List".

1. Create LTI passport and add it to "Settings" > "Advanced Settings" > "LTI Passports" list:

    ```
    "lti-id:lti-client-key:lti-client-secret"
    ```

    * Replace `lti-id` with a short arbitrary string (must be unique among LTI passports from "LTI Passports" list).
    * Replace `lti-client-key` with `LTI_CLIENT_KEY` from `app/local_settings.py`.
    * Replace `lti-client-secret` with `LTI_CLIENT_SECRET` from `app/local_settings.py`.

    If LPD is the only LTI tool that is available for the current course, the "LTI Passports" list will look like this:

    ```
    [
        "lti-id:lti-client-key:lti-client-secret"
    ]
    ```

1. Add "LTI Consumer" block to unit.

1. Configure block as follows:

    * Display Name: learner-profile-dashboard (or similar)
    * LTI ID: `lti-id` from LTI passport
    * LTI URL: `http://localhost:8080/lti/` (note that you might need to adjust port to match port that you supplied to `runserver` command)

    You can leave remaining settings at their defaults. After saving changes, block will render LPD.
