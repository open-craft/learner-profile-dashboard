/*
 * JavaScript for Learner Profile Dashboard
 */

$(document).ready(function() {

    // Functions

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
            if ($(sameValueRank).is(':checked')) {
                $(sameValueRank).prop('checked', false);
            }
        });
    };


    // Event handlers

    $('.section-title').click(function(e) {
        var $sectionForm = $(this).parent('form'),
            $questions = $sectionForm.children('.section-questions'),
            $controls = $sectionForm.children('.section-controls');

        $questions.toggle();
        $controls.toggle();
    });

    $('.mr-option').click(function(e) {
        var $optionGroup = $(this).parents('.mr-options');
        disableOptions($optionGroup);
    });

    $('.option-rank').click(function(e) {
        uncheckSameValueRanks(this);
    });


    // Initialization

    var init = function() {
        console.log('Initializing ...');
        updateOptionGroups();
    };

    init();

});
