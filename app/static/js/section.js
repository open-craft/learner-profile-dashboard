/*
 * JavaScript for Learner Profile Dashboard (sections)
 */

$(document).ready(function() {

    // Event handlers

    $('.section-title').click(function(e) {
        var $sectionForm = $(this).parent('form'),
            $sectionCollapse = $sectionForm.find('.section-collapse'),
            $intro = $sectionForm.children('.section-intro'),
            $questions = $sectionForm.children('.section-questions'),
            $controls = $sectionForm.children('.section-controls');

        $sectionCollapse.toggleClass('expanded');
        $sectionCollapse.toggleClass('collapsed');
        $intro.toggle('slow');
        $questions.toggle('slow');
        $controls.toggle('slow');
    });

});
