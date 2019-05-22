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
                var order_product_id = response['order_product_ids'][i];
                var id = response[order_product_id]['stock_product_id'];
                window.stock_product_ids.push(id);
                $('#name-' + id.toString()).html(response[order_product_id]['name']);
                $('#img-' + id.toString()).attr('src', response[order_product_id]['image_url']);
                for (var key in response[order_product_id]['modifications']) {
                    var str_to_append = '<div class="col-sm-6"><input readonly class="form-control-plaintext" value="' + key.toString() + '"></div><div class="col-sm-6"><input readonly class="form-control-plaintext" value="' + response[order_product_id]['modifications'][key].toString() + '" style="text-align: right;"></div>';
                    $('#parameters-' + id.toString()).append(str_to_append);
                }
                $('#parameters-' + id.toString()).append('<div class="col-sm-6"><input readonly class="form-control-plaintext" value="Количество"></div><div class="col-sm-6"><input readonly id="quantity-' + id.toString() + '" class="form-control" type="number" value="' + response[order_product_id]['quantity'].toString() + '"style="text-align: right;"></div>');
            }
        }
    });
}

$('document').ready(function() {
    initialize_products();
});