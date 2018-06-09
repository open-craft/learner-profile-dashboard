/*
 * JavaScript for Learner Profile Dashboard
 */

$(document).ready(function() {

    // Constants

    const MC_QUESTION_TYPES = ['mcq', 'mrq'],
          RANKING_QUESTION_TYPES = ['ranking', 'likert'],
          QUANTITATIVE_QUESTION_TYPES = MC_QUESTION_TYPES.concat(RANKING_QUESTION_TYPES),
          QUALITATIVE_QUESTION_TYPES = ['essay', 'short-answer'],
          ANSWER_OPTION_SELECTORS = {
              'mcq': '.mc-option',
              'mrq': '.mr-option',
              'ranking': '.ranking-option',
              'likert': '.likert-option'
          };


    // Functions

    var renderChecked = function() {
        var optionInputs = $('.mc-option, .mr-option, .option-rank');
        optionInputs.each(function(i, optionInput) {
            var $optionInput = $(optionInput);
            if ($optionInput.attr('checked') === 'checked') {
                $optionInput.prop('checked', true);
            } else {
                $optionInput.prop('checked', false);
            }
        });
    };

    var updateOptionGroups = function() {
        var $optionGroups = $('.mr-options');
        $optionGroups.each(function(i, optionGroup) {
            disableOptions($(optionGroup));
        });
    };

    var disableOptions = function($optionGroup) {
        var maxOptionsToSelect = $optionGroup.data('max-options-to-select'),
            $options = $optionGroup.find('.mr-option'),
            $selectedOptions = $options.filter(':checked'),
            $unselectedOptions = $options.not(':checked');

        if ($selectedOptions.length >= maxOptionsToSelect) {
            $unselectedOptions.attr('disabled', true);
        } else {
            $unselectedOptions.attr('disabled', false);
        }

    };

    var uncheckSameValueRanks = function(rank) {
        var $rank = $(rank),
            rankValue = $rank.val(),
            $optionGroup = $rank.parents('.ranking-options'),
            $sameValueRanks = $optionGroup.find('.option-rank').not(rank).filter(function(i) {
                return $(this).val() === rankValue;
            });

        $sameValueRanks.each(function(i, sameValueRank) {
            var $sameValueRank = $(sameValueRank);
            if ($sameValueRank.is(':checked')) {
                $sameValueRank.prop('checked', false);
            }
        });
    };

    var collectAnswers = function($sectionForm) {
        var $questions = getUpdatedQuestions($sectionForm),
            qualitativeAnswers = [],
            quantitativeAnswers = [];

        console.log($questions);

        $questions.each(function(i, question) {
            var $question = $(question),
                questionID = $question.data('question-id'),
                questionType = $question.data('question-type');

            if ($.inArray(questionType, QUALITATIVE_QUESTION_TYPES) !== -1) {
                var answerData = collectAnswerData($question, questionID);
                qualitativeAnswers.push(answerData);
            } else if ($.inArray(questionType, QUANTITATIVE_QUESTION_TYPES) !== -1) {
                var answerOptionData = collectAnswerOptionData($question, questionID, questionType);
                quantitativeAnswers = quantitativeAnswers.concat(answerOptionData);
            }
        });

        console.log(qualitativeAnswers);
        console.log(quantitativeAnswers);

        return {
            'qualitative_answers': JSON.stringify(qualitativeAnswers),
            'quantitative_answers': JSON.stringify(quantitativeAnswers)
        };
    };

    var getUpdatedQuestions = function($sectionForm) {
        return $sectionForm.find('.question').filter(function() {
            return $(this).data('answer-changed') === true;
        });
    };

    var collectAnswerData = function($question, questionID) {
        var $answerText = $question.find('.answer-text'),
            answerData = {
                question_id: questionID,
                answer_text: $answerText.val()
            };
        return answerData;
    };

    var collectAnswerOptionData = function($question, questionID, questionType) {
        var $answerOptions = $question.find(ANSWER_OPTION_SELECTORS[questionType]),
            results = [];

        $answerOptions.each(function(i, answerOption) {
            var $answerOption = $(answerOption),
                answerOptionID = $answerOption.data('answer-option-id'),
                answerOptionValue = getAnswerOptionValue(questionType, $answerOption),
                $customInput = getCustomInput(questionType, $answerOption),
                answerOptionData = {
                    question_id: questionID,
                    question_type: questionType
                };

            answerOptionData['answer_option_id'] = answerOptionID;
            answerOptionData['answer_option_value'] = answerOptionValue;

            if ($customInput.length > 0) {
                answerOptionData['answer_option_custom_input'] = $customInput.val();
            }

            results.push(answerOptionData);
        });
        return results;
    };

    var getAnswerOptionValue = function(questionType, $answerOption) {
        var answerOptionValue;
        if ($.inArray(questionType, MC_QUESTION_TYPES) > -1) {
            answerOptionValue = $answerOption.is(':checked') ? 1 : 0;
        } else if ($.inArray(questionType, RANKING_QUESTION_TYPES) > -1) {
            var rawValue = $answerOption.find('.option-rank:checked').val();
            answerOptionValue = parseInt(rawValue, 10);
        }
        return answerOptionValue;
    };

    var getCustomInput = function(questionType, $answerOption) {
        var $customInput;
        if ($.inArray(questionType, MC_QUESTION_TYPES) > -1) {
            $customInput = $answerOption.next('.custom-input');
        } else if ($.inArray(questionType, RANKING_QUESTION_TYPES) > -1) {
            $customInput = $answerOption.find('.custom-input');
        }
        return $customInput;
    };

    var resetQuestionState = function($sectionForm) {
        var $questions = getUpdatedQuestions($sectionForm);
        $questions.each(function(i, question) {
            $(question).data('answer-changed', false);
        });
    };

    var updateSubmissionInfo = function($sectionForm, data) {
        var $submissionInfo = $sectionForm.find('.submission-info'),
            lastUpdate = data.last_update;
        $submissionInfo.text(lastUpdate);
    };


    // Event handlers

    $('.section-title').click(function(e) {
        var $sectionForm = $(this).parent('form'),
            $intro = $sectionForm.children('.section-intro'),
            $questions = $sectionForm.children('.section-questions'),
            $controls = $sectionForm.children('.section-controls');

        $intro.toggle('slow');
        $questions.toggle('slow');
        $controls.toggle('slow');
    });

    $('.question').change(function(e) {
        $(this).data('answer-changed', true);
    });

    $('.mr-option').click(function(e) {
        var $optionGroup = $(this).parents('.mr-options');
        disableOptions($optionGroup);
    });

    $('.option-rank').click(function(e) {
        uncheckSameValueRanks(this);
    });

    $('.section-submit').click(function(e) {
        e.preventDefault();
        console.log('Submitting answers ...');

        var $sectionForm = $(this).parents('form'),
            sectionID = $sectionForm.data('section-id'),
            answers = collectAnswers($sectionForm);

        answers['section_id'] = sectionID;

        $.ajax({
            url: 'submit',
            type: 'POST',
            data: answers,
            success: function(data) {
                console.log('SUCCESS');
                console.log(data);
                resetQuestionState($sectionForm);
                updateSubmissionInfo($sectionForm, data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('ERROR');
                console.log(jqXHR.status);
                console.log(jqXHR.responseText);
            }
        });

    });


    // Initialization

    var init = function() {
        console.log('Initializing ...');

        $.ajaxSetup({
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken')
            },
            dataType: 'json'
        });

        renderChecked();
        updateOptionGroups();
    };

    init();

});
