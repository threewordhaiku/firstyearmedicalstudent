$(document).ready(function() {
    $(".nxtbtn").click(function() {
        $(".template").animate({
            "padding": "1.5rem",
            "margin": "1rem"
        });
        $(".text1").fadeOut();
        $(".game-content").fadeIn()
    });
});