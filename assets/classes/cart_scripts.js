function delete_from_arr_by_value(arr, val) {
    var index = 0;
    for (var i = 0; i < arr.length; i += 1) {
        if (arr[i] == val) {
            index = i;
        }
    }
    arr.splice(index, 1);
    return arr;
}

function refresh_cart() {
    window.location.href = '/cart';
}

function clear_cart() {
    $.ajax({
        type: 'POST',
        url: '/clear_cart',
        data: {
            'csrfmiddlewaretoken': window.kek
        },
        success: function() {
            refresh_cart();
        }
    });
}

function refresh_total_cost() {
    var total_cost = 0;
    for (var i = 0; i < window.stock_product_ids.length; i += 1) {
        var id = window.stock_product_ids[i];
        var quantity = window.quantities[id];
        var price = window.prices[id];
        total_cost += quantity * price;
    }
    window.total_cost = total_cost;
    $('#cost-header').html('Итого: ' + window.total_cost.toString() + ' ₽');
}

function block_edit() {
    for (var i = 0; i < window.stock_product_ids.length; i += 1) {
        var id = window.stock_product_ids[i];
        $('#delete-' + id.toString()).prop('disabled', true);
        $('#quantity-' + id.toString()).prop('disabled', true);
    }
}

function fill_addresses() {
    $('#select_address').empty()
    $.ajax({
        type: 'POST',
        url: '/get_addresses',
        data: {
            'csrfmiddlewaretoken': window.kek
        },
        success: function(response) {
            for (var id in response) {
                var description = response[id];
                var str_to_add = '<option value="' + id.toString() + '">' + description.toString() + '</option>';
                $('#select_address').append(str_to_add);
            }
        }
    });
}

function make_order_btn() {
    block_edit();
    $('#make-order-container').css('display', 'flex');
    $('#make-order-btn').prop('disabled', true);
    if (window.is_auth) {
        fill_addresses();
    }
    $('html, body').animate({ scrollTop: $(document).height() }, 1000);
}

function check_address_form_validity() {
    if (window.is_auth) {
        return city_input.checkValidity() && street_input.checkValidity() && building_input.checkValidity() && entrance_input.checkValidity() && flat_input.checkValidity() && description_input.checkValidity();
    }
    else {
        return city_input.checkValidity() && street_input.checkValidity() && building_input.checkValidity() && entrance_input.checkValidity() && flat_input.checkValidity();
    }
}

function check_email_validity() {
    return email_input.checkValidity();
}

function get_address_data() {
    data = {};
    data['city'] = $('#city_input').val();
    data['street'] = $('#street_input').val();
    data['building'] = $('#building_input').val();
    data['entrance'] = $('#entrance_input').val();
    data['flat'] = $('#flat_input').val();
    if (window.is_auth) {
        data['description'] = $('#description_input').val();
    }
    return data;
}

function delete_input_values() {
    $('#city_input').value = '';
}

function add_address_btn() {
    if ($('#add_address_container').css('display') == 'none') {
        $('#add_address_container').css('display', 'block');
        $('#final_order_button').prop('disabled', true);
        $('html, body').animate({ scrollTop: $(document).height() }, 1000);
    }
    else {
        $('#add_address_container').css('display', 'none');
        $('#final_order_button').prop('disabled', false);
    }
    
}

function submit_address_btn() {
    if (check_address_form_validity()) {
        var data = get_address_data();
        data['csrfmiddlewaretoken'] = window.kek;
        $.ajax({
            type: 'POST',
            url: '/add_address',
            data: data,
            success: function(response) {
                if (response['result'] == 'found description') {
                    alert('У вас уже существует адрес с таким описанием');
                }
                else {
                    $('#add_address_container').css('display', 'none');
                    $('#final_order_button').prop('disabled', false);
                    delete_input_values();
                    fill_addresses();
                }
            }
        });
    }
}

function final_order_btn() {
    if (window.is_auth) {
        if (select_address.checkValidity()) {
            var address_id = $('#select_address').val();
            $.ajax({
                type: 'POST',
                url: '/make_order',
                data: {
                    'address_id': address_id,
                    'csrfmiddlewaretoken': window.kek
                },
                success: function() {
                    alert('Заказ успешно добавлен.');
                    clear_cart();
                }
            });
        }
    }
    else {
        if (check_address_form_validity() && check_email_validity()) {
            var data = get_address_data();
            data['email'] = $('#email_input').val();
            data['csrfmiddlewaretoken'] = window.kek;
            $.ajax({
                type: 'POST',
                url: '/make_order',
                data: data,
                success: function() {
                    alert('Заказ успешно добавлен.');
                    clear_cart();
                }
            });
        }
    }
}

function initialize_products() {
    var data = {};
    data['order_product_id'] = window.starting_order_product_ids;
    data['csrfmiddlewaretoken'] = window.kek;
    $.ajax({
        type: 'POST',
        url: '/get_order_product_modifications',
        data: data,
        success: function(response) {
            for (var i = 0; i < response['order_product_ids'].length; i += 1) {
                var order_product_id = response['order_product_ids'][i];
                var id = response[order_product_id]['stock_product_id'];
                window.stock_product_ids.push(id);
                window.prices[id] = response[order_product_id]['price'];
                $('#name-' + id.toString()).html(response[order_product_id]['name']);
                $('#img-' + id.toString()).attr('src', response[order_product_id]['image_url']);
                var cost = response[order_product_id]['price'] * response[order_product_id]['quantity'];
                $('#cost-' + id.toString()).append(cost.toString() + '₽');
                for (var key in response[order_product_id]['modifications']) {
                    var str_to_append = '<div class="col-sm-6"><input readonly class="form-control-plaintext" value="' + key.toString() + '"></div><div class="col-sm-6"><input readonly class="form-control-plaintext" value="' + response[order_product_id]['modifications'][key].toString() + '" style="text-align: right;"></div>';
                    $('#parameters-' + id.toString()).append(str_to_append);
                }
                $('#parameters-' + id.toString()).append('<div class="col-sm-6"><input readonly class="form-control-plaintext" value="Количество"></div><div class="col-sm-6"><input id="quantity-' + id.toString() + '" class="form-control" type="number" value="' + response[order_product_id]['quantity'].toString() + '" min="1" style="text-align: right;"></div>');
                $('#quantity-' + id.toString()).attr('max', response[order_product_id]['max_quantity'].toString());
                window.quantities[id] = response[order_product_id]['quantity'];
                $('#quantity-' + id.toString()).on('change', function(event) {
                    if (this.checkValidity()) {
                        var cur_id = this.id.toString().split('-')[1];
                        var cur_val = this.value;
                        data = {
                            'new_quantity': cur_val,
                            'stock_product_id': cur_id,
                            'csrfmiddlewaretoken': window.kek
                        };
                        $.ajax({
                            type: 'POST',
                            url: '/change_order_product_quantity',
                            data: data,
                            success: function(response) {
                                window.quantities[cur_id] = cur_val;
                                var new_price = window.prices[cur_id] * cur_val;
                                $('#cost-' + cur_id.toString()).html('Стоимость: ' + new_price.toString() + '₽');
                                refresh_total_cost();
                            }
                        });
                    }
                });
                $('#delete-' + id.toString()).on('click', function(event) {
                    var data = {};
                    var cur_id = this.id.toString().split('-')[1];
                    data['csrfmiddlewaretoken'] = window.kek;
                    data['stock_product_id'] = cur_id;
                    $.ajax({
                        type: 'POST',
                        url: '/del_from_cart',
                        data: data,
                        success: function(response) {
                            $('#container-' + cur_id.toString()).remove();
                            window.stock_product_ids = delete_from_arr_by_value(window.stock_product_ids, cur_id);
                            delete window.prices[cur_id];
                            delete window.quantities[cur_id];
                            refresh_total_cost();
                            if (window.stock_product_ids.length == 0) {
                                $('#cost-header').remove();
                                $('#make-order-btn').remove();
                                $('#content-row').before('<h2 style="text-align: center; margin-bottom: 10px; margin-top: 10px; color: gray;">Корзина пуста</h2>');
                            }
                            alert('Товар успешно удален из корзины');
                        }
                    });
                });
            }
            refresh_total_cost();
        }
    });
}


$('document').ready(function() {
    initialize_products();
});