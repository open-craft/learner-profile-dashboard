LTI Learner Profile Dashboard
=============================

# Overview

Learner Profile Dashboard (LPD) is an LTI application that allows course authors to collect information about the
background and interests of learners that are enrolled in a course, and to (optionally) use that information to drive
course content selection for individual learners. (Technically, LPD can be used to collect *any* kind of information
from learners but it was developed for the use case mentioned here, i.e., asking learners about their background and
interests.) It integrates with Harvard VPAL's Adaptive Engine (https://github.com/harvard-vpal/adaptive-engine) which

> powers the recommendation of learning resources to learners based on real-time activity.

The following sections describe the basic structure of the LPD as well as available questions types and associated
configuration options, and mention options for authoring content for the LPD.

## Basic Structure of the LPD

The LPD consists of a set of sections and associated questions. Aside from a set of questions, each section has a title
and some introducture text (which is optional). Learners submit answers to questions at section-level: Each section
includes a "Submit your answers" button at the bottom that learners can click to save their answers to questions
belonging to the section. Learners can click the title of a section to expand/collapse its content as needed.
Irrespective of its type (cf. below), each question consists of a number (relative to the parent section), text that
represents the question, and some framing text (which is optional). It is also possible to store author notes for a
given question; the LPD will not show these notes to the learner.

## Question Types

The LPD currently supports the following question types:

### Qualitative Questions

*Qualitative questions* are questions that require learners to provide free-text answers.

#### Short Answers

*Short Answer* questions prompt learners for short free-text answers that consist of a few words, or maybe one full
sentence. The LPD displays a small text field for learners to enter their answers to these types of questions.

#### Essays

*Essay* questions prompt learners for longer answers that consist of multiple sentences or paragraphs. The LPD displays
a large text area for learners to enter their answers to these types of questions.

#### Configuration Options

- `question_type`:
    - No default
    - Set to `'short-answer'` or `'essay'`.
- `influences_group_membership`:
    - Default: `False`
    - When set to `True`, LPD will take this question into account when analyzing learners' answers to qualitative
      questions (for the purpose of driving content selection).
- `split_answer`:
    - Default: `False`
    - Whether answers to this question consist of a comma-separated list of values
      that should be stored as separate answers to facilitate certain post-processing steps after export.
    - When set to `True`, LPD will split answers to this question at commas
      and store reach resulting answer component as a separate answer.

### Quantitative Questions

*Quantitative questions* are questions that require learners to choose from a pre-defined set of *answer options* (cf. below).

#### Configuration options

- `randomize_options`:
    - Default: `False` (results in alphabetical ordering of answer options)
    - When set to `True`, LPD will display answer options in random order.

#### Multiple Choice Questions

*Multiple choice* questions prompt learners to select one or more answer options. For questions that prompt learners to
select a single answer option the LPD displays the set of answer options using radio buttons. For questions that prompt
learners to select two or more answer options, the LPD displays the set of answer options using check boxes.

##### Configuration options

- `max_options_to_select`:
    - Default: `1`
    - Maximum number of answer options that learner is allowed to select for this question.

#### Ranking Questions

*Ranking* questions prompt learners to rank (a subset of) their answer options, on a scale of `1` to the maximum number
of options to rank (cf. below). For example, if a ranking question is configured to allow learners to rank three
options, learners can assign ranks `1`, `2`, and `3` to exactly one answer option each. The maximum number of options to
rank does not place any restrictions on the number of answer options that can be associated with a ranking question. In
other words, the number of answer options defined for a ranking question can be less than, equal to, or greather than
the maximum number of options to rank. For each answer option that belongs to a ranking question, the LPD displays a
radio button for each rank that a learner may choose for the answer option. For example, if a ranking question is
configured to allow learners to rank three options, the LPD will display three radio buttons (labeled "1", "2", and "3")
next to each answer option.

##### Configuration options

- `number_of_options_to_rank`:
    - Default: `3`
    - Number of answer options belonging to this question that learners are allowed to rank.

#### Likert Scale Questions

*Likert Scale* questions prompt learners to choose from a predefined range of values for each answer option. There are
currently two ranges of values to choose from (cf. below). For example, when choosing the `'agreement'` range, the LPD
will display a set of radio buttons with the following values next to each answer option:

- Strongly Disagree (raw value: `1`)
- Disagree (raw value: `2`)
- Undecided (raw value: `3`)
- Agree (raw value: `4`)
- Strongly Agree (raw value: `5`)

##### Configuration options

- `answer_option_range`:
    - Default: `'agreement'`
    - Set to `'agreement'` or `'value'`.
    - Range of values to display for answer options belonging to this question.

## Answer Options

As mentioned above, each *answer option* is associated with a specific quantitative question. How it will be displayed
depends on the type of quantitative question that it is associated with.

### Configuration options

- `option_text`:
    - No default
    - Text to display for this answer option.
- `allows_custom_input`:
    - Default: `False`
    - Whether this answer option allows learners to specify custom input.
- `influences_recommendations`:
    - Default: `False`
    - When set to `True`, LPD will send answers to this answer option to the Adaptive Engine (for the purpose of driving
      content selection). Note that the answer option also needs to be associated with a *knowledge component* for this to work.
- `fallback_option`:
    - Default: `False`
    - Whether this is a catch-all option (such as "Don't know", or "Other:") that learners would choose
      if none of the other options apply to them.
    - When set to `True`, LPD will display this option below regular options
      (i.e., options that have `fallback_option` set to `False`), in reverse alphabetical order.
      Note that the LPD's behavior regarding fallback options is the same
      regardless of whether a quantitative question has been configured
      to display answer options in random order or not.

## Knowledge Components

*Knowledge components* represent groups that a learner might belong to (such as "people that are interested in music"),
or specific areas of interest. For knowledge components representing groups, the LPD uses a learner's answers to
relevant qualitative questions to compute the probability of that learner belonging to each of these groups (cf. below for
technical details). Knowledge components representing specific areas of interest are associated with answer options
belonging to quantitative questions. When a learner submits relevant answers for a specific section of the LPD, the LPD
recalculates group membership probabilities and sends both group membership information and answer data from relevant
answer options to the Adaptive Engine. (Qualitative questions and answer options are considered *relevant* if they are
configured to influence group membership/influence recommendations, respectively.)

## Authoring Content

There are currently two options for authoring content: Via the Django shell and via a custom management command
(`load_data`). LPD does not provide a Django admin for creating LPD components (sections, questions, etc.). The
management command expects data to load into the LPD's database to be supplied in the form of CSV files that live
in a directory called `data`. This directory needs to be a sub-directory of the root directory of this repository. See
`lpd/management/commands/load_data.py` for details on the expected format of these CSV files.

# Development

This section describes how to set up a local development environment for Learner Profile Dashboard.

## Prerequisites

* SQLite or MySQL
* python-dev
* virtualenv

## Setting up the development server

1. Install python dependencies:

    ```bash
    virtualenv .virtualenv
    . .virtualenv/bin/activate
    pip install -r requirements/base.txt
    ```

1. Learner Profile Dashboard uses an LDA model and a tf-idf vectorizer to analyze learners' answers to relevant
qualitative questions. Please provide such a model and a vectorizer, replacing `lda.pkl` and `tfidf_vectorizer.pkl`
files in the root directory of the project with your files. (Currently, `lda.pkl` and `tfidf_vectorizer.pkl` are just
empty Python pickle files.) For more details, see `lpd/qualitative_data_analysis.py`.

1. Create `app/local_settings.py`, and set the sensitive settings:

    ```python
    SECRET_KEY = 'SET ME'
    LTI_CLIENT_KEY = 'SET ME'
    LTI_CLIENT_SECRET = 'SET ME'
    PASSWORD_GENERATOR_NONCE = 'SET ME'

    # Optional - can use default sqlite for development
    LPD_DB_PASSWORD = 'SET ME'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'lti_lpd',
            'USER': 'lti_lpd',
            'PASSWORD': LPD_DB_PASSWORD,
        }
    }

    # List of knowledge component IDs for which LDA model calculates probabilities.
    # The order of the components must match exactly the order in which probabilities are returned by LDA model.
    # For example, if the LDA model returns [0.2, 0.8] and GROUP_KCS are set to ['kc_id_1', 'kc_id_2'],
    # then 0.2 will be interpreted as the probability of a learner belonging to the knowledge component (group)
    # identified by 'kc_id_1', and 0.8 will be interpreted as the probability of the learner
    # belonging to the knowledge component (group) identified by 'kc_id_2'.
    GROUP_KCS = ['kc_id_1_set-me', 'kc_id_2_set-me']

    # Domain of the Open edX instance that this LPD deployment is connected to
    OPENEDX_INSTANCE_DOMAIN = 'development.domain.com'
    # URL of the Adaptive Engine deployment that this LPD deployment is connected to
    ADAPTIVE_ENGINE_URL = 'http://localhost'
    # Auth token for requests to Adaptive Engine deployment that this LPD deployment is connected to
    ADAPTIVE_ENGINE_TOKEN = 'development-token'
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

1. Run development server:

    ```bash
    # Use port 8080 to avoid conflicting with LMS/CMS ports
    ./manage.py runserver 8080
    ```

1. Run Django shell:

    ```bash
    ./manage.py shell
    ```

1. Run tests, and view coverage report:

    ```bash
    pip install -r requirements/test.txt
    coverage run --source=. manage.py test
    coverage report -m
    ```

## Using LPD with Open edX

1. If you haven't already, add `"lti_consumer"` to "Settings" > "Advanced Settings" > "Advanced Module List".

1. Create an LTI passport and add it to "Settings" > "Advanced Settings" > "LTI Passports" list:

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

1. Add an *LTI Consumer* block to a unit.

1. Configure the LTI Consumer block as follows:

    * Display Name: learner-profile-dashboard (or similar)
    * LTI ID: `lti-id` from LTI passport
    * LTI URL: `http://localhost:8080/lti/` (note that you might need to adjust the port to match the port that you supplied to the `runserver` command)

    You can leave the remaining settings at their defaults. After saving changes, the *LTI Consumer* block will render LPD.
