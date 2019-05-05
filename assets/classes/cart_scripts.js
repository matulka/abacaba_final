function initialize_products() {
    var data = {};
    data['order_product_id'] = window.order_product_ids;
    data['csrfmiddlewaretoken'] = window.kek;
    $.ajax({
        type: 'POST',
        url: '/get_order_product_modifications',
        data: data,
        success: function(response) {
            for (var i = 0; i < response['order_product_ids'].length; i += 1) {
                var id = response['order_product_ids'][i];
                window.prices[id] = response[id]['price'];
                window.stock_product_ids[id] = response[id]['stock_product_id'];
                $('#name-' + id.toString()).html(response[id]['name']);
                $('#img-' + id.toString()).attr('src', response[id]['image_url']);
                $('#cost-' + id.toString()).append((response[id]['price'] * response[id]['quantity']).toString() + '₽');
                for (var key in response[id]['modifications']) {
                    var str_to_append = '<div class="col-sm-6"><input readonly class="form-control-plaintext" value="' + key.toString() + '"></div><div class="col-sm-6"><input readonly class="form-control-plaintext" value="' + response[id]['modifications'][key].toString() + '" style="text-align: right;"></div>';
                    $('#parameters-' + id.toString()).append(str_to_append);
                }
                $('#parameters-' + id.toString()).append('<div class="col-sm-6"><input readonly class="form-control-plaintext" value="Количество"></div><div class="col-sm-6"><input id="quantity-' + id.toString() + '" class="form-control" type="number" value="' + response[id]['quantity'].toString() + '" min="1" style="text-align: right;"></div>');
                $('#quantity-' + id.toString()).attr('max', response[id]['max_quantity'].toString());
                $('#quantity-' + id.toString()).on('change', function(event) {
                    if (this.checkValidity()) {
                        var cur_id = this.id.toString().split('-')[1];
                        var new_price = window.prices[cur_id] * this.value;
                        $('#cost-' + cur_id.toString()).html('Стоимость: ' + new_price.toString() + '₽');
                    }
                });
                $('#delete-' + id.toString()).on('click', function(event) {
                    var data = {};
                    var cur_id = this.id.toString().split('-')[1];
                    data['csrfmiddlewaretoken'] = window.kek;
                    data['stock_product_id'] = window.stock_product_ids[cur_id];
                    $.ajax({
                        type: 'POST',
                        url: '/del_from_cart',
                        data: data,
                        success: function(response) {
                            $('#container-' + cur_id.toString()).remove();
                            alert('Товар успешно удален из корзины');
                        }
                    });
                });
            }
        }
    });
}


$('document').ready(function() {
    initialize_products();
});