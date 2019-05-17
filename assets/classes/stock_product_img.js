function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}

ids = []
counter = -1;
function add_img(url, id){
    counter += 1;
    var str_html = '<div class="row"> <img id="img'+id+'" src="'+url+'" alt="Изображение товара"> <input type="button" id="btn'+id+'" value="Удалить картинку" onclick="btn_del('+id+')">'+
    '</div>'
    $('#images').append(str_html)
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
                            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        }
    });
    $.ajax({
        url: '/find_sp_images',
        type: "POST",
        data: {
            id: get_product_id(),
        },
        success: function (response) {
            for (var i = 0; i < response['ids'].length; i += 1){
                add_img(response['urls'][i], response['ids'][i]);
            }
        }
    });
    console.log('OOOOOOOOOOOOOOo')
});

function btn_del(id){
    $.ajax({
        url: '/del_img',
        type: "POST",
        data: {
            id: id,
            prod_id: get_product_id,
        },
        success: function (response) {
            $('#btn'+id).remove()
            $('#img'+id).remove()
        }
    });
}