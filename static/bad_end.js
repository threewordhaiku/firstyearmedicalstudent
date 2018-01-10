$(document).ready(function() {
    $(".nxtbtn").click(function() {
        $(".text1").fadeOut();
        $(".text2").delay(500).fadeIn();
    });
});