$('document').ready(function() {
    var data = {};
    data['order_product_id'] = window.order_product_ids;
    data['csrfmiddlewaretoken'] = window.kek;
    $.ajax({
        type: 'POST',
        url: '/get_order_product_modifications',
        data: data,
        success: function(response) {
            console.log(response);
        }
    });
});