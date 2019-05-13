function add_cat(){
    window.counter_categories += 1;
    var html_str = '<div class="row"><input list="categories" name="cat" id="cat' + window.counter_categories + '"> <label list="categories" name="lab" id="lab' + window.counter_categories +'"></label></div>'
    $('#new-cat').prepend(html_str);
}
function add_exist_cat(name){
    window.counter_categories += 1;
    var html_str = '<div class="row"><input list="categories" name="cat" id="cat' + window.counter_categories +
    '" value="' + name +
     '"> <label list="categories" name="lab" id="lab' + window.counter_categories +'"></label></div>'
     if (window.counter_categories != 0){
        html_str = '<div class="row"><input list="categories" name="cat" id="cat' + window.counter_categories +
        '" value="' + name +
         '"> <input type="button" value="Удалить категорию" id="btn-remove' + window.counter_categories + '" onclick="del_cat('+window.counter_categories+')"><label list="categories" name="lab" id="lab' + window.counter_categories +'"></label></div>'
     }
    $('#new-cat').prepend(html_str);
}
function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}

function del_cat(id){
    console.log(id)
    $("#btn-remove" + id).remove()
    $("#cat" + id).remove()
}
categories = [];
string_to_add = "";
product_names = [];
product_name = ""

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
        answer.push(cat[i].value);
    }
    return answer;
}

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
    $.ajax({
        url: '/get_http_products',
        success: function (response) {
            product_names = response['product_names'];
        }
    });
    $.ajax({
        url: '/get_categories_by_id',
        type: "POST",
            data: {
                 id: get_product_id(),
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
        success: function (response) {
            console.log(response['cat']);
            console.log(response['name']);
            product_name = response['name'];
            for (var i=0; i < response['cat'].length; i+=1){
                add_exist_cat(response['cat'][i]);
            }
        }
    });
});
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
        var lab = document.getElementsByName('lab');
        for (var i = 0; i < cat.length; i += 1){
            var c = cat[i];
            var founded = false;
            for (var j = 0; j < categories.length; j += 1){
                if (c.value == categories[j].name) {
                    founded = true;
                    break;
                }
            }
            if (!founded){
                has_errors = true;
                var lable = lab[i];
                lable.textContent = "Такой категории не существует!"
            }
            if (c.value == ''){
                able.textContent = "Заполните поле!"
                has_errors = true;
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