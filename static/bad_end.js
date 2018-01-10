/*$(document).ready(function() {
    $(".nxtbtn").click(function() {
        $(".text1").fadeOut();
        $(".text2").delay(500).fadeIn();
    });
});*/

text = ".text1"

$(document).ready(function() {
    $(".nxtbtn").click(function() {
    	$(text).fadeOut();
    	text = next_text(text);
        $(text).delay(300).fadeIn();
    });
});

function next_text(current_text) {
	next = current_text.slice(-1);
	nextint = parseInt(next)
	nextint ++;
	nextstr = nextint.toString();
	temp = ".text";
	return temp.concat(nextstr)
}