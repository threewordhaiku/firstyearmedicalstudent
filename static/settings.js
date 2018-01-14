function show_value(vol_value,vol_id)
{
 document.getElementById(vol_id).innerHTML=vol_value;
}
function add_one(no,vol_id)
{
  slider_id = check(no);
  var x = $(slider_id).slider("value");
  x= x+1;
  $(slider_id).slider("value",x);
  show_value(x,vol_id);
}

function check(no){
    if (no==1){
        return ".master_volume"
    }
    else if (no==2){
        return ".sfx"
    }
    else if (no==3){
        return ".bgm"
    }
}

/*function subtract_one()
{
  document.f.master_volume.value=parseInt(document.f.master_volume.value)-1;
  show_value(document.f.master_volume.value,master_volume);
}*/