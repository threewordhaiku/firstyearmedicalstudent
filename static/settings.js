/*Settings Menu Fuctions*/

/* Master Volume Functions */
function slidecalc_master(sliderCurrentValue) {
   var sliderCurrentValue = sliderCurrentValue.toFixed();
   $("#master_volume_value").text(sliderCurrentValue);
   }
   $(function() { 
   $("#master_volume").slider({
    range: "min",
    value: 50,
    min:  0,
    max: 100,
    step: 1,
    slide: function( event, ui ) {
      slidecalc_master(ui.value);
     }// ends the  slide event
    });

   $('#plus_mastervol').click(function() {
    var sliderCurrentValue = $( "#master_volume" ).slider( "option", "value" );
    $("#master_volume").slider( "value", sliderCurrentValue + 1 );
     slidecalc_master(sliderCurrentValue);
    });

   $('#minus_mastervol').click(function() {
    var sliderCurrentValue = $( "#master_volume" ).slider( "option", "value" );
    $("#master_volume").slider( "value", sliderCurrentValue - 1 );
    slidecalc_master(sliderCurrentValue);
    });

   });

/* SFX Volume Functions */
function slidecalc_sfx(sliderCurrentValue) {
   var sliderCurrentValue = sliderCurrentValue.toFixed();
   $("#sfx_volume_value").text(sliderCurrentValue);
   }
   $(function() { 
   $("#sfx_volume").slider({
    range: "min",
    value: 50,
    min:  0,
    max: 100,
    step: 1,
    slide: function( event, ui ) {
      slidecalc_sfx(ui.value);
     }
    });

   $('#plus_sfxvol').click(function() {
    var sliderCurrentValue = $( "#sfx_volume" ).slider( "option", "value" );
    $("#sfx_volume").slider( "value", sliderCurrentValue + 1 );
     slidecalc_sfx(sliderCurrentValue);
    });

   $('#minus_sfxvol').click(function() {
    var sliderCurrentValue = $( "#sfx_volume" ).slider( "option", "value" );
    $("#sfx_volume").slider( "value", sliderCurrentValue - 1 );
    slidecalc_sfx(sliderCurrentValue);
    });
   });

/* BGM Functions */
function slidecalc_bgm(sliderCurrentValue) {
   var sliderCurrentValue = sliderCurrentValue.toFixed();
   $("#bgm_volume_value").text(sliderCurrentValue);
   }
   $(function() { 
   $("#bgm_volume").slider({
    range: "min",
    value: 50,
    min:  0,
    max: 100,
    step: 1,
    slide: function( event, ui ) {
      slidecalc_bgm(ui.value);
     }
    });

   $('#plus_bgmvol').click(function() {
    var sliderCurrentValue = $( "#bgm_volume" ).slider( "option", "value" );
    $("#bgm_volume").slider( "value", sliderCurrentValue + 1 );
     slidecalc_bgm(sliderCurrentValue);
    });

   $('#minus_bgmvol').click(function() {
    var sliderCurrentValue = $( "#bgm_volume" ).slider( "option", "value" );
    $("#bgm_volume").slider( "value", sliderCurrentValue - 1 );
    slidecalc_bgm(sliderCurrentValue);
    });
   });