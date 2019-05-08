function add_cat(){
    var html_str = '<input list="categories" name="category">'+
            +'<datalist id="categories">'+
                +'{% for cat in categories %}'
                    +'<option>{{ cat.name }}'
                +'{% endfor %}'
            +'</datalist>'
    $('#new-cat').prepend(html_str);
}

$(document).ready(function(){
    $('#add-existing-cat').on('click', add_cat);
});