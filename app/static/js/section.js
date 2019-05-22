/*
 * JavaScript for Learner Profile Dashboard (sections)
 */

$(document).ready(function() {

    // Globals

    var RET = 13;
    var SPC = 32;

    // Functions

    var toggleSection = function($section) {
        var $sectionForm = $section.parent('form'),
            $sectionCollapse = $sectionForm.find('.section-collapse'),
            $intro = $sectionForm.children('.section-intro'),
            $questions = $sectionForm.children('.section-questions'),
            $controls = $sectionForm.children('.section-controls');

        $sectionCollapse.toggleClass('collapsed');
        $sectionCollapse.toggleClass('expanded');
        $intro.toggle('slow');
        $questions.toggle('slow');
        $controls.toggle('slow');
    };

    // Event handlers

    $('.section-title').on('click', function(e) {
        var $section = $(this);
        toggleSection($section);
    });

    $('.section-title').on('keydown', function(e) {
        if (e.which === RET || e.which === SPC) {
            e.preventDefault();
            var $section = $(this);
            toggleSection($section);
        }
    });

});
