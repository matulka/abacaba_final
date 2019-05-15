function disable_all_tabs() {
    $('#my_profile_ref').removeClass('active');
    $('#my_orders_ref').removeClass('active');
    $('#my_address_ref').removeClass('active');
}

function get_current_tab_id() {
    var url = window.location.href;
    var path_array = url.split('/');
    var index = path_array.findIndex(function(el){if (el == 'accounts') return true; return false;});
    index += 1;
    var current_section = path_array[index];
    
    if (current_section.includes('profile')) return '#my_profile_ref';
    if (current_section.includes('orders')) return '#my_orders_ref';
    if (current_section.includes('addresses')) return '#my_address_ref';
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