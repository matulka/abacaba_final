var global = this;
var modifications = {};

function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}

function string_to_array(string) {
    var arr = string.split(',');
    return arr;
}

function add_select_str(parameter, values) {
    var str_to_add = '';
    str_to_add += '<div class=\"col-sm-6\"><p>' + parameter.toString() + '</p></div>';
    str_to_add += '<div class=\"col-sm-6\"><select name=\"' + parameter.toString() + '\">';
    for (var i = 0; i < values.length; i += 1) {
        str_to_add += '<option value=\"' + values[i].toString() + '\">' + values[i].toString() + '</option>';
    }
    str_to_add += '</select></div>';
    return str_to_add;
}

function initialize_modifications(product_id) {
    $.ajax({
        url: '/get_modifications?product_id=' + product_id.toString(),
        success: function(response) {
            var html_str = '';
            for (var parameter in response) {
                html_str += add_select_str(parameter, response[parameter]);
            }
            $('#edit-div').html(html_str);
        }
    });
}

$(document).ready(function(){
    var product_id = get_product_id();
    initialize_modifications(product_id);
});