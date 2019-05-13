categories = [];
string_to_add = "";

$(document).ready(function(){
    window.counter_categories = -1;
    window.click = false;
    $.ajax({
        url: '/get_http_categories',
        success: function (response) {
            var string = response['1'];
            decode_categories(string);
        }
    });
});

function decode_categories(string) {
    var category_tuples = string.split(";");
    for (var i = 0; i < category_tuples.length; i += 1) {
        tuple = category_tuples[i];
        var category_array = tuple.split(",");
        var id = category_array[0];
        var name = category_array[1];
        var parent_id = category_array[2];
        var new_category = new Category(id, name, parent_id);
        categories.push(new_category);
    }
    for (var i = 0; i < categories.length; i += 1) {
        if (categories[i].parent_id != null){
            for (var j = 0; j < categories.length; j += 1) {
                if (categories[j].id == categories[i].parent_id) {
                    categories[j].child_categories.push(categories[i]);
                }
            }
        }
    }
}

function valid_form(){
    if (!window.click){
        console.log('UUUUUUUUUF')
        var has_errors = false
        if ($('#id_name').val().length < 1){
            has_errors =true;
            $('#name_err').text("Заполните поле!")
        }
        for (var i = 0; i < product_names.length; i += 1){
            if ($('#id_name').val() == product_names[i] && $('#id_name').val() != product_name){
                has_errors =true;
                $('#name_err').text("Продукт с таким именем уже существует!")
            }
        }
        for (var j = 0; j < categories.length; j += 1){
            var founded = false;
            if ($('#main-cat').val() == categories[j].name) {
                 founded = true;
                 break;
            }
        }
        if (!founded){
           has_errors = true;
           $('#main-lab').text("Такой категории не существует!")
        }
        if ($('#main-cat').val() == '') {
            has_errors = true;
            $('#main-lab').text("Заполните поле!")
        }
        if (!has_errors){
            var csrf_token = $('meta[name="csrf-token"]').attr('content');
            $.ajax({
            url: '/change_exist_product',
            type: "POST",
            data: {
                 cat: form_categories(),
                 main: $('#main-cat').val(),
                 name: $('#id_name').val(),
                 price: $('#id_price').val(),
                 rating: $('#id_price').val(),
                 id: get_product_id(),
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
            success: function (response) {
                window.click = true
                console.log('YES!')
                $('#done').text("Продукт успешно изменен!")
                $('#btn_submit').attr('value', 'Перейти к редактированию товаров');
            },
            error: function(xhr, textStatus, errorThrown) {
                    alert("pl report: " + errorThrown + xhr.status + xhr.responseText);
            }
        });
        }
    }
    else{
        window.location.replace('/admin/product_page/')
    }
}