function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}
ids = []
counter = -1;
function add_mod(val, id){
    counter += 1;
    var str_html = '<div class="row"><label>'+ val +':</label><input type="button" id="'+id+'" value="Добавить картинки" onclick="btn_click('+id+')">'+
    '</div>'
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
        url: '/find_prod_sps',
        type: "POST",
        data: {
            id: get_product_id(),
        },
        success: function (response) {
            console.log(response['mod'])
            for (var i = 0; i < response['mod'].length; i += 1){
                add_mod(response['mod'][i], response['ids'][i]);
                ids = response['ids'];
            }
        }
    });
});

function btn_click(id){
    window.location.replace('/admin/stock_products/change_img?id=' + id)
}