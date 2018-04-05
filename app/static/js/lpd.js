/*
 * JavaScript for Learner Profile Dashboard
 */

$(document).ready(function() {

    // Event handlers

    $('.section-title').click(function(e) {
        var $sectionForm = $(this).parent('form'),
            $questions = $sectionForm.children('.section-questions'),
            $controls = $sectionForm.children('.section-controls');

        $questions.toggle();
        $controls.toggle();
    });

});
