function add_cat(){
    window.counter_categories += 1;
    var html_str = '<div class="row"><input list="categories" name="cat" id="cat' + window.counter_categories + '"> <label list="categories" name="lab" id="lab' + window.counter_categories +'"></label></div>'
    $('#new-cat').prepend(html_str);
}
categories = [];
string_to_add = "";
product_names = [];

class Category {
    constructor(id, name, parent_id) {
        this.id = id;
        this.name = name;
        if (parent_id == 'None'){
            this.parent_id = null;
        }
        else {
            this.parent_id = parent_id;
        }
        this.child_categories = new Array();
    }
}

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
function form_categories() {
    answer = []
    var cat = document.getElementsByName('cat');
    for (var i = 0; i < cat.length; i += 1){
        var name_cat = '#cat' + i;
        answer.push($(name_cat).val());
    }
    return answer;
}

$(document).ready(function(){
    console.log('af');
    window.counter_categories = 0;
    window.click = false;
    $.ajax({
        url: '/get_http_categories',
        success: function (response) {
            var string = response['1'];
            decode_categories(string);
        }
    });
    $.ajax({
        url: '/get_http_products',
        success: function (response) {
            product_names = response['product_names'];
        }
    });
});
function valid_form(){
    if (!window.click){
        var has_errors = false
        if ($('#id_name').val().length < 1){
            has_errors =true;
            $('#name_err').text("Заполните поле!")
        }
        for (var i = 0; i < product_names.length; i += 1){
            if ($('#id_name').val() == product_names[i]){
                has_errors =true;
                $('#name_err').text("Продукт с таким именем уже существует!")
            }
        }
        if ($('#id_price').val().length < 1){
            has_errors =true;
            $('#price_err').text("Заполните поле!")
        }
        if ($('#id_price').val() < 0){
            has_errors =true;
            $('#price_err').text("Цена должна быть положительной!")
        }
         if ($('#id_rating').val().length > 0){
             if ($('#id_rating').val() < 0 || $('#id_rating').val() > 5){
                has_errors =true;
                $('#rating_err').text("Рейтинг должен быть в пределах от 0 до 5!")
             }
        }
        var cat = document.getElementsByName('cat');
        for (var i = 0; i < cat.length; i += 1){
            var name_cat = '#cat' + i;
            var founded = false;
            for (var j = 0; j < categories.length; j += 1){
                if ($(name_cat).val() == categories[j].name) {
                    founded = true;
                    break;
                }
            }
            if (!founded){
                has_errors = true;
                var name_label = '#lab' + i;
                $(name_label).text("Такой категории не существует!")
            }
            var name_label = '#lab' + i;
            if ($(name_cat).val() == ''){
                $(name_label).text("Заполните поле!")
                has_errors = true;
            }
        }
        founded = false;
        for (var j = 0; j < categories.length; j += 1){
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
            url: '/form_product',
            type: "POST",
            data: {
                 cat: form_categories(),
                 main: $('#main-cat').val(),
                 name: $('#id_name').val(),
                 price: $('#id_price').val(),
                 rating: $('#id_price').val(),
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
            success: function (response) {
                window.click = true
                console.log('YES!')
                $('#done').text("Продукт успешно создан!")
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