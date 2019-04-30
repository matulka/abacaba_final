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

categories = [];
string_to_add = "";

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

function begin_parent_dropdown(name) {
    var string = "<li class=\"nav-item dropdown\"><a class=\"nav-link dropdown-toggle category_parent_dropdown\" href=\"#\" id=\"navbarDropdownMenuLink\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\">" + name + "</a><ul class=\"dropdown-menu\">";
    string_to_add += string;
}

function end_parent_dropdown() {
    var string = "</ul></li>";
    string_to_add += string; 
}

function begin_child_dropdown(name) {
    var string = "<li class=\"dropdown-submenu\"><a class=\"dropdown-item dropdown-toggle\" href=\"#\">" + name + "</a><ul class=\"dropdown-menu\">";
    string_to_add += string;
}

function end_child_dropdown() {
    var string = "</ul></li>";
    string_to_add += string;
}

function insert_action(name, id) {
    var string = "<li><a class=\"dropdown-item\" href=\"/?category_id=" + id + "\">" + name + "</a></li>";
    string_to_add += string;
}

function load_category(category) {
    var is_child = false;
    if (category.parent_id != null) {
        is_child = true;
    }
    var is_parent = false;
    if (category.child_categories.length != 0) {
        is_parent = true;
    }
    if (is_parent && is_child) {
        begin_child_dropdown(category.name);
        for (var i = 0; i < category.child_categories.length; i += 1) {
            load_category(category.child_categories[i]);
        }
        end_child_dropdown();
    }
    if (is_parent && !is_child) {
        begin_parent_dropdown(category.name);
        for (var i = 0; i < category.child_categories.length; i += 1) {
            load_category(category.child_categories[i]);
        }
        end_parent_dropdown();
    }
    if (!is_parent) {
        insert_action(category.name, category.id);
    }
}

function get_id_category(categories_list, name) {
    id = null;
    for (var i = 0; i < categories_list.length; i += 1) {
        if (categories_list[i].name == name) {
            id = categories_list[i].id;
        }
    }
    return id;
}

$(document).ready(function () {
    $.ajax({
        url: '/get_http_categories',
        success: function (response) {
            var string = response['1'];
            decode_categories(string);
            for (var i = 0; i < categories.length; i += 1) {
                if (categories[i].parent_id == null) {
                    load_category(categories[i]);
                }
            }
            $('#main_navbar').append(string_to_add);
            $('a.category_parent_dropdown').on('click', function(e) {
                if ($(this).attr('aria-expanded') == 'true') {
                    id = get_id_category(categories, $(this).html());
                    window.location.replace('/?category_id=' + id);
                }
            });
            $('.dropdown-menu a.dropdown-toggle').on('click', function (e) {
                if ($(this).next().hasClass('show')) {
                    id = get_id_category(categories, $(this).html());
                    window.location.replace('/?category_id=' + id);
                }
                var $subMenu = $(this).next(".dropdown-menu");
                $subMenu.toggleClass('show');


                $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function (e) {
                    $('.dropdown-submenu .show').removeClass("show");
                });


                return false;
            });
        }
    });

});