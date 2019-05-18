function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}
ids = []
counter = -1;
function add_mod(val, q){
    counter += 1;
    var str_html = '<div class="row"><label>'+ val +':</label><input type="number" min="0" value="'+q+'" id="'+counter+'" name="q">'+
    '<label name="lab"></label></div>'
    $('#modifications').append(str_html)
}

$(document).ready(function(){
    window.counter_chars = -1;
    window.click = false;
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') {
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie != '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = jQuery.trim(cookies[i]);
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        }
    });
    $.ajax({
        url: '/find_prod_modifications',
        type: "POST",
        data: {
            id: get_product_id(),
        },
        success: function (response) {
            console.log(response['mod'])
            for (var i = 0; i < response['mod'].length; i += 1){
                add_mod(response['mod'][i], response['quantity'][i]);
                ids = response['ids'];
            }
        }
    });
});

function valid_form(){
    if(!window.click){
    var has_errors = false;
    var q = document.getElementsByName('q');
    var qs = []
    var lab = document.getElementsByName('lab');
    for (var i = 0; i < q.length; i += 1){
        if (q[i].value < 0 || q[i].value == ''){
            lab[i].textContent = 'Некорректное значение поля!'
            has_errors = true;
        }
        else{
            qs.push(q[i].value)
        }
    }
    if (!has_errors){
        $.ajax({
            url: '/form_stock_products',
            type: "POST",
            data: {
                id: get_product_id(),
                ids: ids,
                qs: qs,
            },
            success: function (response) {
                window.click = true
                $('#done').text("Продукты на складе успешно созданы!")
                $('#btn_submit').attr('value', 'Перейти на страницу администрации');
            }
        });
    }
    }
    else{
        window.location.replace('/admin')
    }
}