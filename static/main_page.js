$(document).ready(function() {
    $(".SMB").click(function() {
        $(".template").animate({
            "padding": "1.5rem",
            "margin": "1rem"
        });
        $(".startmenu").fadeOut();
        $(".settings").fadeOut();
        $(".game-content").fadeIn()
    });

    $(".settingsbtn").click(function() {
   		$("a[rel]").overlay({
        mask: 'darkred',
        effect: 'apple',

        onBeforeLoad: function() {
            // grab wrapper element inside content
            var wrap = this.getOverlay().find(".contentWrap");
            // load the page specified in the trigger
            wrap.load(this.getTrigger().attr("href"));
        }
 
    	});
	});
 })
