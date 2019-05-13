function add_cat(id, name){
    var html_str = '<div class="row"><label name="cat" id="cat' + id + '">' + name + ' </label>'                                                                     +
    '<input type="button" name="btn" id="btn' + id +'" value="Редактировать категорию" onclick="go_to_cat(' + id + ')">'
     +'</div>'
    $('#form-cat').prepend(html_str);
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

$(document).ready(function(){
    console.log('af');
    window.counter_categories = 0;
    window.click = false;
    $.ajax({
        url: '/get_http_categories',
        success: function (response) {
            var string = response['1'];
            decode_categories(string);
            form_category_list();
        }
    });
});

function form_category_list(){
    for (var i = 0; i < categories.length; i += 1) {
        add_cat(categories[i].id, categories[i].name);
    }
}

function go_to_cat(id){
    window.location.replace('/admin/category_page/category_list/change_category?id=' + id)
}
