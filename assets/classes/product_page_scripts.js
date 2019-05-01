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
    str_to_add += '<div class="col-sm-6"><p>' + parameter.toString() + '</p></div>';
    str_to_add += '<div class="col-sm-6"><select class="form-control form-control-sm" name="' + parameter.toString() + '" disabled>';
    for (var i = 0; i < values.length; i += 1) {
        str_to_add += '<option value="' + values[i].toString() + '">' + values[i].toString() + '</option>';
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
            $('#edit-div').prepend(html_str);
            get_current_images();
        }
    });
}

function edit_button_action(event) {
    if ($('#edit-button').html() == 'Редактировать') {
        $('select').attr('disabled', false);
        $('#edit-button').html('Сохранить');
    } else if ($('#edit-button').html() == 'Сохранить') {
        $('select').attr('disabled', true);
        $('#edit-button').html('Редактировать');
    }
}

function select_image(this_image) {
    $('img').each(function() {
        $(this).attr('style', '');
    })
    this_image.style = 'border: 2px solid red; border-radius: 5px;';
    $('#main-image').attr('src', this_image.src);
}

function get_current_images() {
    var modification_dict = {};
    $('select').each(function(index){
        modification_dict[$(this).attr('name')] = $(this).val();
    });
    data = {};
    data['product_id'] = get_product_id();
    data['modification_dict_str'] = JSON.stringify(modification_dict);
    $.ajax({
        type: 'POST',
        url: '/get_images',
        data: data,
        success: function(response) {
            for (var index in response) {
                var url = response[index];
                var string_to_add = '';
                string_to_add += '<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3"><div class="square-box" style="width: 100%">';
                string_to_add += '<img class="centered-div mini-image" src="' + url + '" onclick="select_image(this)">';
                string_to_add += '</div></div>';
                $('#subimages_row').append(string_to_add);
                if (index == '0') {
                    $('img[src="' + url + '"]').each(function() {
                        if ($(this).hasClass('mini-image')) {
                            $(this).attr('style', 'border: 2px solid red; border-radius: 5px;');
                            $('#main_image').attr('src', $(this).attr('src'));
                        }
                    });
                }
            }
            $()
        }
    });
}

$(document).ready(function(){
    var product_id = get_product_id();
    initialize_modifications(product_id);
    $('#edit-button').on('click', edit_button_action);
});