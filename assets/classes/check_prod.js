categories = [];
string_to_add = "";

$(document).ready(function(){
    product_names = [];
    $.ajax({
        url: '/get_http_products',
        success: function (response) {
            product_names = response['product_names'];
        }
    });
});

function valid_form(){
        var has_errors = false
        $('#lab').text("")
        if ($('#prod').val().length < 1){
            has_errors =true;
            $('#lab').text("Заполните поле!")
        }
        var founded = false
        for (var i = 0; i < product_names.length; i += 1){
            if ($('#prod').val() == product_names[i]){
                founded = true;
                break;
            }
        }
        if (!founded){
           has_errors = true;
           $('#lab').text("Такого продукта не существует!")
        }
        if (!has_errors){
            var csrf_token = $('meta[name="csrf-token"]').attr('content');
            $.ajax({
            url: '/get_prod_by_name',
            type: "POST",
            data: {
                 name: $('#prod').val(),
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
            success: function (response) {
                id = response['id']
                window.location.replace('/admin/modification_page/add_modification' + '?id=' + id)
            },
            error: function(xhr, textStatus, errorThrown) {
                    alert("pl report: " + errorThrown + xhr.status + xhr.responseText);
            }
        });
        }
}