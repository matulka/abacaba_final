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