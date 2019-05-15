function disable_all_tabs() {
    $('#my_profile_ref').removeClass('active');
    $('#my_orders_ref').removeClass('active');
    $('#my_address_ref').removeClass('active');
}

function get_current_tab_id() {
    var url = window.location.href;
    var path_array = url.split('/');
    var current_section = path_array[path_array.length - 1];
    
    if (current_section == 'profile') return '#my_profile_ref';
    if (current_section == 'orders') return '#my_orders_ref';
    if (current_section == 'addresses') return '#my_address_ref';
    return null;
}

function change_active_tab() {
    disable_all_tabs();
    var id = get_current_tab_id();
    $(id).addClass('active');
}

$(document).ready(function() {
    change_active_tab();
});