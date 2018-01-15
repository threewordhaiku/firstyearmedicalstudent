$(document).ready(function() {
    $(".SMB_new").click(function() {
        $(".template").animate({
            "padding": "1.5rem",
            "margin": "1rem"
        });
        $(".startmenu").fadeOut();
        $(".settings").fadeOut();
        $(".game-content").fadeIn()
    });
});
