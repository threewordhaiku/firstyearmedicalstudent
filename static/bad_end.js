text = ".text1";
counter = 1;

$(document).ready(function() {
    $(".nxtbtn").click(function() {
    	$(text).fadeOut();
    	text = next_text(text);
        $(text).delay(300).fadeIn();
    });
});

function next_text(current_text) {
	if (counter<10){
	next = current_text.slice(-1);
	} else {
	next = current_text.slice(-2);
	}
	nextint = parseInt(next)
	nextint ++;
	nextstr = nextint.toString();
	temp = ".text";
	counter++;
	return temp.concat(nextstr)
}