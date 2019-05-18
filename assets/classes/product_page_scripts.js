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
        $('#cart-button').attr('disabled', true);
        $('#edit-button').html('Сохранить');
    } else if ($('#edit-button').html() == 'Сохранить') {
        $('#cart-button').attr('disabled', false);
        $('select').attr('disabled', true);
        $('#edit-button').html('Редактировать');
        get_current_images();
    }
}

function select_image(this_image) {
    $('img').each(function() {
        $(this).attr('style', '');
    });
    this_image.style = 'border: 2px solid red; border-radius: 5px;';
    $('#main-image').attr('src', this_image.src);
}

function get_current_images() {
    var modification_dict = {};
    $('select').each(function(){
        modification_dict[$(this).attr('name')] = $(this).val();
    });
    data = {};
    data['product_id'] = get_product_id();
    data['modification_dict_str'] = JSON.stringify(modification_dict);
    data['csrfmiddlewaretoken'] = window.kek;
    $.ajax({
        type: 'POST',
        url: '/get_images',
        data: data,
        success: function(response) {
            $('#subimages_row').empty();
            $('#main-image').attr('src', '');
            for (var index = 0; index < response['images'].length; index += 1) {
                var url = response['images'][index];
                var string_to_add = '';
                string_to_add += '<div class="col-3"><div class="square-box" style="width: 100%">';
                string_to_add += '<img class="centered-div mini-image" src="' + url + '" onclick="select_image(this)">';
                string_to_add += '</div></div>';
                $('#subimages_row').append(string_to_add);
                if (index == '0') {
                    $('img[src="' + url + '"]').each(function() {
                        if ($(this).hasClass('mini-image')) {
                            $(this).attr('style', 'border: 2px solid red; border-radius: 5px;');
                            $('#main-image').attr('src', $(this).attr('src'));
                        }
                    });
                }
            }
            $('#quantity').attr('max', response['quantity'])
        }
    });
}

function change_button_action(){
    var url = '/admin/product_page/change_product' + '?id=' + get_product_id()
    window.location.replace(url)
}

function cart_button_action(event) {
    if (quantity.checkValidity()) {
        data = {};
        $('select').each(function() {
            data[$(this).attr('name')] = $(this).val();
        });
        data['quantity'] = $('#quantity').val();
        data['product_id'] = get_product_id();
        data['csrfmiddlewaretoken'] = window.kek;
        $.ajax({
            type: 'POST',
            url: '/add_to_cart',
            data: data,
            success: function(response) {
                alert('Товар успешно добавлен в корзину.');
            }
        });
    }
    else {
        alert('К сожалению, у нас не такого количества этого товара! Пожалуйста, выберите количество меньше.');
    }
}

$(document).ready(function(){
    var product_id = get_product_id();
    initialize_modifications(product_id);
    $('#edit-button').on('click', edit_button_action);
    $('#change-button').on('click', change_button_action);
    $('#cart-button').on('click', cart_button_action);
});