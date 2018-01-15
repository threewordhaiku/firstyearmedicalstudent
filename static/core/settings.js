/*Settings Button Toggle Function*/
$(document).ready(function(){
  
  function toggle_settings() {
    $("#settings_screen").toggle();
    $("#cover").toggle();
  };
  
  #(".cancel_button").click(toggle_settings);
  $(".settings_toggle").click(toggle_settings);
});

/*Settings Menu Fuctions*/
/*Setting Screen Classes 
--------------------------------------------------*/
/*Containers for the words and sliders*/
.settings{ 
  padding: 3rem 
}

/*Box containing above container and the X button*/
#settings_screen
{
    height:380px;
    width:340px;
    margin: auto;
    margin-top: 10rem;
    position:relative;
    z-index:10;
    display:none;
    background:#fff;
    border:5px solid #cccccc;
    /*border-radius:10px;*/
}
#settings_screen, #cover{
    display:block;
    opacity:2;
}

/*X button*/
.cancel_button
{
    display:block;
    position:absolute;
    top:3px;
    right:2px;
    background:none;
    color:black;
    height:30px;
    width:35px;
    font-size:30px;
    text-decoration:none;
    text-align:center;
    font-weight:bold;
}

.cancel_button:hover {
  text-decoration: none;
}

/*The greying out of the page (its an overlay)*/
#cover{
    position:fixed;
    top:0;
    left:0;
    background:rgba(0,0,0,0.6);
    z-index:5;
    width:100%;
    height:100%;
    display:none;
}

/*sliders*/
/*Previous slider code (works fine but cant work with buttons)*/
/*.slider {
    -webkit-appearance: none;
    width: 100%;
    height: 10px;
    //border-radius:5px;
    background: #d3d3d3;
    outline: none;
    opacity: 0.7;
    -webkit-transition: .2s;
    transition: opacity .2s;
}

.slider:hover {
    opacity: 1;
}

.slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius:50%;
    background: #000;
    cursor: pointer;
} */

/*Overwriting Jquery-ui css for the sliders*/
.ui-slider {
  border-radius: 0;
}

/*Overwriting Jquery-ui css for the handle*/
.ui-slider .ui-slider-handle{
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius:50%;
    background: #000;
    cursor: pointer;
}

/*Numerical display*/
.slider_value{
  background: #C9C9C9;
  border-color:#000;
  border: 1px solid;
  padding: 0px 10px;
}

/*-/+ buttons on settings menu*/
.plusminusbtn{
  border:none;
  //background-color: #FFF;
  //border:1px solid;
  //border-radius:10%;
  width:25px;
  height:23px;
  text-align: center;
}
/*<< Setting Screen Classes */


.settingsbtn {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 58.5px; /* Set the fixed height of the footer here */
  line-height: 60px; /* Vertically center the text there */
  margin-left: 5px; 
}

.settings_toggle {
}

.slider_value {
  color: black;
  font-weight: bold;
}



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