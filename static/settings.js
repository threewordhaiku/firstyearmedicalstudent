function show_value(vol_value,vol_id)
{
 document.getElementById(vol_id).innerHTML=vol_value;
}
function add_one()
{
  document.f.sld6.value=parseInt(document.f.sld6.value)+1;
  show_value(document.f.sld6.value);
}
function subtract_one()
{
  document.f.sld6.value=parseInt(document.f.sld6.value)-1;
  show_value(document.f.sld6.value);
}