LTI Learner Profile Dashboard
=============================

# Overview

Learner Profile Dashboard (LPD) is an LTI application that allows course authors to collect information about the
background and interests of learners that are enrolled in a course, and to (optionally) use that information to drive
course content selection for individual learners. (Technically, the LPD application can be used to collect
*any* kind of information from learners but it was developed for the use case mentioned here,
i.e., asking learners about their background and interests.) It integrates with Harvard VPAL's Adaptive Engine
(https://github.com/harvard-vpal/adaptive-engine) which

> powers the recommendation of learning resources to learners based on real-time activity.

The following sections describe the basic structure of an LPD instance as well as available questions types and associated
configuration options, and mention options for authoring content that the LPD application provides.

# Basic Structure of an LPD instance

An LPD instance consists of a set of sections and associated questions. Aside from a set of questions, each section
has a title and some introductory text (which is optional). Learners submit answers to questions at section-level:
Each section includes a "Submit your answers" button at the bottom that learners can click to save their answers to questions
belonging to the section. Learners can click the title of a section to expand/collapse its content as needed.
Sections are collapsed by default. Irrespective of its type (cf. below), each question consists of a number
(relative to the parent section), text that represents the question, and some framing text (which is optional).
It is also possible to store author notes for a given question; the LPD application will not show these notes to the learner.

## Sections

### Configuration Options

- `lpd`:
    - No default
    - Learner Profile Dashboard that this section belongs to.
- `title`:
    - No default
    - Text to display at the top of this section (optional).
- `intro_text`
    - No default
    - Introductory text to display below section title and above questions belonging to this section (optional).

## Questions

The LPD application currently support the following question types:

- Qualitative questions
    - Short Answers
    - Essays
- Quantitative questions
    - Multiple choice questions
    - Ranking questions
    - Likert scale questions

Each of these question types is described in more detail below.

All questions share the following configuration options:

- `section`:
    - No default
    - Section that this question belongs to.
- `number`:
    - Default: `1`
- `question_text`:
    - No default
    - Text that represents this question. Displayed above `framing_text`, answer options (if any), and input fields.
- `framing_text`:
    - No default
    - Introductory text to display below question text and above answer options and input fields
      belonging to this question (optional).
- `notes`:
    - No default
    - Author notes about this question (optional).

### Qualitative Questions

*Qualitative questions* are questions that require learners to provide free-text answers.

#### Short Answers

*Short Answer* questions prompt learners for short free-text answers that consist of a few words, or maybe one full
sentence. The LPD application displays a small text field for learners to enter their answers to these types of questions.

#### Essays

*Essay* questions prompt learners for longer answers that consist of multiple sentences or paragraphs. The LPD application
displays a large text area for learners to enter their answers to these types of questions.

#### Configuration Options

- `question_type`:
    - No default
    - Set to `'short-answer'` or `'essay'`.
- `influences_group_membership`:
    - Default: `False`
    - When set to `True`, LPD application will take this question into account when analyzing learners' answers
      to qualitative questions (for the purpose of driving content selection).
- `split_answer`:
    - Default: `False`
    - Whether answers to this question consist of a comma-separated list of values
      that should be stored as separate answers to facilitate certain post-processing steps after export.
    - When set to `True`, LPD application will split answers to this question at commas
      and store reach resulting answer component as a separate answer.

### Quantitative Questions

*Quantitative questions* are questions that require learners to choose from a pre-defined set of *answer options* (cf. below).

#### Configuration Options

- `randomize_options`:
    - Default: `False` (results in alphabetical ordering of answer options)
    - When set to `True`, LPD application will display answer options in random order.

#### Multiple Choice Questions

*Multiple choice* questions prompt learners to select one or more answer options. For questions that prompt learners to
select a single answer option the LPD application displays the set of answer options using radio buttons.
For questions that prompt learners to select two or more answer options, the LPD application displays
the set of answer options using check boxes.

##### Configuration Options

- `max_options_to_select`:
    - Default: `1`
    - Maximum number of answer options that learner is allowed to select for this question.

#### Ranking Questions

*Ranking* questions prompt learners to rank (a subset of) their answer options, on a scale of `1` to the maximum number
of options to rank (cf. below). For example, if a ranking question is configured to allow learners to rank three
options, learners can assign ranks `1`, `2`, and `3` to exactly one answer option each. The maximum number of options to
rank does not place any restrictions on the number of answer options that can be associated with a ranking question. In
other words, the number of answer options defined for a ranking question can be less than, equal to, or greather than
the maximum number of options to rank. For each answer option that belongs to a ranking question, the LPD application
displays a radio button for each rank that a learner may choose for the answer option. For example, if a ranking question is
configured to allow learners to rank three options, the LPD application will display three radio buttons
(labeled "1", "2", and "3") next to each answer option.

##### Configuration Options

- `number_of_options_to_rank`:
    - Default: `3`
    - Number of answer options belonging to this question that learners are allowed to rank.

#### Likert Scale Questions

*Likert scale* questions prompt learners to choose from a predefined range of values for each answer option. There are
currently two ranges of values to choose from, *agreement* and *value* (cf. below). For each raw value belonging to the chosen range,
the LPD application will display an appropriate label (such as "Strongly Disagree", "Undecided", "Agree", etc.)
and a radio button for selecting the value.

##### Configuration Options

- `answer_option_range`:
    - Default: `'agreement'`
    - Set to `'agreement'` or `'value'`.
    - Range of values to display for answer options belonging to this question.
    - When set to `'agreement'`, the range of values to select from is as follows:
        - Strongly Disagree (raw value: `1`)
        - Disagree (raw value: `2`)
        - Undecided (raw value: `3`)
        - Agree (raw value: `4`)
        - Strongly Agree (raw value: `5`)
    - When set to `'value'`, the range of values to select from includes is as follows:
        - Not Very Valuable (raw_value: `1`)
        - Slightly Valuable (raw_value: `2`)
        - Valuable  (raw_value: `3`)
        - Very Valuable (raw_value: `4`)
        - Extremely Valuable (raw_value: `5`)

## Answer Options

As mentioned above, each *answer option* is associated with a specific quantitative question. How it will be displayed
depends on the type of quantitative question that it is associated with.

### Configuration Options

- `content_object`:
    - No default
    - Question that this answer option belongs to.
- `knowledge_component`:
    - No default
    - Knowledge component that this answer option is associated with (optional).
- `option_text`:
    - No default
    - Text to display for this answer option.
- `allows_custom_input`:
    - Default: `False`
    - Whether this answer option allows learners to specify custom input.
    - When set to `True`, LPD application will display a text input field next to `option_text`
      that learners can use to further define a given option.
      For example, if `option_text` of this answer option is set to something like "Other:"
      (and `allows_custom_input` is set to `True`), LPD application will render the answer option as

      "Other: \_\_\_\_\_\_\_\_\_\_\_\_\_\_"

      (and record the learner's input along with the value that they chose for this answer option).
- `influences_recommendations`:
    - Default: `False`
    - When set to `True`, LPD application will send answers to this answer option to the Adaptive Engine
      (for the purpose of driving content selection). Note that the answer option also needs to be
      associated with a *knowledge component* for this to work.
- `fallback_option`:
    - Default: `False`
    - Whether this is a catch-all option (such as "Don't know", or "Other:") that learners would choose
      if none of the other options apply to them.
    - When set to `True`, LPD application will display this option below regular options
      (i.e., options that have `fallback_option` set to `False`), in reverse alphabetical order.
      Note that the LPD application's behavior regarding fallback options is the same
      regardless of whether a quantitative question has been configured
      to display answer options in random order or not.

## Knowledge Components

*Knowledge components* represent groups that a learner might belong to (such as "people that are interested in music"),
or specific areas of interest. For knowledge components representing groups, the LPD application uses a learner's answers to
relevant qualitative questions to compute the probability of that learner belonging to each of these groups (cf. below for
technical details). Knowledge components representing specific areas of interest are associated with answer options
belonging to quantitative questions. When a learner submits relevant answers for a specific section of an LPD instance,
the LPD application recalculates group membership probabilities (only taking into account learner answers
from the current LPD instance) and sends both group membership information and answer data from relevant answer options
to the Adaptive Engine. (Qualitative questions and answer options are considered *relevant* if they are configured
to influence group membership/influence recommendations, respectively.)

### Configuration Options

- `lpd`:
    - No default
    - Learner Profile Dashboard that this knowledge component belongs to.
      Optional for knowledge components that are associated with answer options
      (since answer options are linked to specific LPD instances via the questions they belong to),
      but should be set if this knowledge component represents a group
      (to enable filtering of group scores by LPD instance/course run).
- `kc_id`:
    - No default
    - String that LPD application and adaptive engine use to uniquely identify this knowledge component.
- `kc_name`:
    - No default
    - Verbose name for this knowledge component.

# Authoring Content

There are currently two options for authoring content: Via the Django shell and via the Django admin.
There is also a custom management command (`load_data`). This command expects data to load into the LPD applications's
database to be supplied in the form of CSV files that live in a directory called `data`. The `data` directory
needs to be a sub-directory of the root directory of this repository:

```
$ tree learner-profile-dashboard
learner-profile-dashboard
├── ...
├── data
│   ├── answer_options.csv
│   ├── knowledge_components.csv
│   ├── qualitative_questions.csv
│   ├── quantitative_questions.csv
│   └── sections.csv
├── ...
```

See `lpd/management/commands/load_data.py`
for details on the expected format of the CSV files to add to the `data` directory.

*Note, however, that the `load_data` command has not been updated since [v1.0.0](https://github.com/open-craft/learner-profile-dashboard/releases/tag/v1.0.0)
of this project, so it should only be used if you are trying to bootstrap an initial definition of an LPD instance
from CSV data.* This was the main reason for creating the `load_data` command, which assumes that the database either
contains a single LPD instance named "Learner Profile", or no LPD instances at all.
Lastly, if you choose to use the `load_data` command to bootstrap an LPD definition, note that further editing
via the Django shell and/or the Django admin might be necessary to establish necessary relations between
individual components of an LPD instance populated via the `load_data` command.

# Additional Features

## LPD and Section-Level Completeness

To indicate to a learner the extent to which their learner profile is complete, LPD instances display:

- LPD-level completion status as a percentage at the top of the page.
- Section-level completion status as a percentage at the top of each section.

### Definition of Completeness

A learner's profile is _complete_ if and only if they submitted an answer to each available question.
What constitutes an answer differs based on question type:

- _Qualitative questions (short answer/essay)_: Any text submitted by the learner counts as an answer.
- Quantitative questions:
    - _Multiple Choice questions_:
      Learner must select at least one answer option for the LPD application to consider the question answered.
    - _Ranking questions_:
      Learner must rank [required number of answer options](https://github.com/open-craft/learner-profile-dashboard#configuration-options-3)
      for the LPD application to consider the question answered.
      Note that the logic for determining whether a ranking question has been answered does not treat fallback options differently.
      For example, if the number of options to rank for a given question is `3` and the learner ranked three options,
      the system will consider it answered if any of the following is true:
        - Learner ranked 3 regular options.
        - Learner ranked 2 regular options and 1 fallback option.
        - Learner ranked 1 regular option and 2 fallback options.
        - Learner ranked 3 fallback options.
    - _Likert Scale questions_: Learner must select value for each answer option
      (except for [fallback options](https://github.com/open-craft/learner-profile-dashboard#configuration-options-5))
      for the LPD application to consider the question answered.

A learner's profile is _partially complete_ if they submitted answers for less than 100% of all questions
belonging to a given LPD instance.

Similarly, a section is complete if and only if a learner submitted an answer to each question belonging to that section.
It is partially complete if the learner submitted answers for less than 100% of all questions belonging to it.

## Export Functionality

LPD instances display a "Download profile data" button above and below the sections that belong to them.
Learners can use this button to download a PDF copy of their learner profile (which represents a snapshot of
their answers at that point in time).

PDFs exports of learner profile data look similar to HTML renderings of LPD instances:
They list sections and questions in the same order, and their approach to ordering answer options
for quantitative questions matches the approach that the LPD application uses when rendering full-LPD
or single-question embeds:

- The LPD application will insert answer options into PDF exports in random order
  if a quantitative question is configured to display answer options in random order.
- The LPD application will insert answer options into PDF exports alphabetically
  if a quantitative question is configured _not_ to display answer options in random order.
- The LPD application will insert fallback options below regular options and order them in reverse alphabetical order.

However, there are also some small differences worth noting:

- PDF exports do not include `framing_text` of questions.
- PDF exports do not include any parenthesized notes belonging to `question_text`
  (such as "Answer options appear in random order").
- For multiple choice questions and ranking questions, PDF exports only include answer options
  that the learner selected/ranked.

Lastly, if the LPD application is configured to `USE_REMOTE_STORAGE` (cf. below), it will store
PDF exports in an S3 bucket (the name of which needs to be specified via `AWS_STORAGE_BUCKET_NAME`).
When not using remote storage, PDF exports will be stored in the local file system.

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
    # LPD_DB_PASSWORD = 'SET ME'
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'lti_lpd',
    #         'USER': 'lti_lpd',
    #         'PASSWORD': LPD_DB_PASSWORD,
    #     }
    # }

    # Optional - can store media files (exports) locally for development
    # USE_REMOTE_STORAGE = True

    # AWS_ACCESS_KEY_ID = 'SET ME'
    # AWS_SECRET_ACCESS_KEY = 'SET ME'
    # AWS_STORAGE_BUCKET_NAME = 'SET ME'

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

    You can use the following script to generate secret keys (i.e., `SECRET_KEY`, `LTI_CLIENT_KEY`, `LTI_CLIENT_SECRET`,
    and `PASSWORD_GENERATOR_NONCE`):

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

There are two options for using the LPD application with Open edX: Course authors can create LTI components
referencing LPD instances (one instance per LTI component), and they can create LTI components
referencing specific questions (one question per LTI component).

Learners can submit answers to single-question embeds using a "Submit your answer" button
displayed below the question referenced by the LTI component.

Before adding LPD instances or specific questions to an Open edX course you will need to perform the following steps
to integrate the LPD application with that course:

### Basic Configuration

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

### Embedding LPD instances

Once the basic LTI configuration is in place for a given course, follow these steps to embed an LPD instance into the course:

1. Add an *LTI Consumer* block to a unit.

1. Configure the LTI Consumer block as follows:

    - **Display Name**: Learner Profile Dashboard (or similar)
    - **LTI ID**: `lti-id` from LTI passport
    - **LTI URL**: `http://localhost:8080/lti/`
        - Note that you might need to adjust the port to match the port that you supplied to the `runserver` command.
        - In a production setting, replace `http://localhost:8080` with the domain of your LPD deployment.
    - **Custom Parameters**: `["lpd_id=<id>"]`
        - Replace `<id>` with the ID of the LPD instance you'd like to embed. You can obtain the ID using the Django shell
          or by finding the LPD instance in the Django admin (via list of [LPD instances](http://localhost:8080/admin/lpd/learnerprofiledashboard/))
          and copying the ID from the URL, e.g. `http://localhost:8080/admin/lpd/learnerprofiledashboard/<id>/change/`.

    You can leave the remaining settings at their defaults. After saving changes, the *LTI Consumer* block
    will render the LPD instance identified by `<id>`.

### Embedding specific questions

To embed a specific question into an Open edX course, follow these steps:

1. Add an *LTI Consumer* block to a unit.

1. Configure the LTI Consumer block as follows:

    - **Display Name**: A very important question (or similar)
    - **LTI ID**: `lti-id` from LTI passport
    - **LTI URL**: `http://localhost:8080/lti/`
        - Note that you might need to adjust the port to match the port that you supplied to the `runserver` command.
        - In a production setting, replace `http://localhost:8080` with the domain of your LPD deployment.
    - **Custom Parameters**: `["question_id=<id>", "question_type=<type>"]`
        - Replace `<id>` with the ID of the question you'd like to embed. You can obtain the ID using the Django shell
          or by finding the question in the Django admin (via list of
          [qualitative questions](https://lpd-stage.opencraft.hosting/admin/lpd/qualitativequestion/),
          [multiple choice questions](https://lpd-stage.opencraft.hosting/admin/lpd/multiplechoicequestion/),
          [ranking questions](https://lpd-stage.opencraft.hosting/admin/lpd/rankingquestion/), or
          [Likert scale questions](https://lpd-stage.opencraft.hosting/admin/lpd/likertscalequestion/))
          and copying the ID from the URL, e.g.:
            - `https://lpd-stage.opencraft.hosting/admin/lpd/qualitativequestion/<id>/change/`
            - `https://lpd-stage.opencraft.hosting/admin/lpd/multiplechoicequestion/<id>/change/`
            - `https://lpd-stage.opencraft.hosting/admin/lpd/rankingquestion/<id>/change/`
            - `https://lpd-stage.opencraft.hosting/admin/lpd/likertscalequestion/<id>/change/`
        - Replace `<type>` with `qualitative`, `mcq`, `ranking`, or `likert`,
          depending on the type of question you are looking to embed.

    You can leave the remaining settings at their defaults. After saving changes, the *LTI Consumer* block
    will render the question identified by `<id>` and `type`.
