$(document).ready(function() {
    $(".startmenu").click(function() {
        $(".template").animate({
            "padding": "1.5rem",
            "margin": "1rem"
        });
        $(".startmenu").fadeOut();
        $(".game-content").fadeIn()
    });
});