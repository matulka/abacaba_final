categories = [];
string_to_add = "";

$('document').ready(function(){
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

function valid_form(){
    if (!window.click){
        console.log('UUUUUUUUUF')
        var has_errors = false
        if ($('#id_name').val().length < 1){
            has_errors =true;
            $('#name_err').text("Заполните поле!")
        }
        for (var i = 0; i < categories.length; i += 1){
            if ($('#id_name').val() == categories[i].name){
                has_errors =true;
                $('#name_err').text("Категория с таким именем уже существует!")
            }
        }
        var founded = false
        for (var j = 0; j < categories.length; j += 1){
            if ($('#par-cat').val() == categories[j].name) {
                 founded = true;
                 break;
            }
        }
        if (!founded && $('#par-cat').val() != ''){
           has_errors = true;
           $('#par-lab').text("Такой категории не существует!")
        }
        if (!has_errors){
            var csrf_token = $('meta[name="csrf-token"]').attr('content');
            $.ajax({
            url: '/form_category',
            type: "POST",
            data: {
                 parent: $('#par-cat').val(),
                 name: $('#id_name').val(),
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
            success: function (response) {
                window.click = true
                console.log('YES!')
                $('#done').text("Категория успешно создана!")
                $('#btn_submit').attr('value', 'Перейти к редактированию категорий');
            },
            error: function(xhr, textStatus, errorThrown) {
                    alert("pl report: " + errorThrown + xhr.status + xhr.responseText);
            }
        });
        }
    }
    else{
        window.location.replace('/admin/category_page/')
    }
}