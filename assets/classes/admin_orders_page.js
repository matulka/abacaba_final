date = []
author = []
email = []
state = []
id = []
address = []

function create_header(){
    st = ' style="border: 1px solid grey;"'
    var html_str = '<table'+st+' id="tbl">'+
                '<tr'+st+'><th'+st+'>Дата</th><th'+st+'>Автор</th><th'+st+'>Наполнение</th><th'+st+'>Адрес</th>' +
                '<th'+st+'>email</th><th'+st+'>Статус</th></tr>'
                '</table>'
    $('#table').append(html_str);
}

function order_info(i){
    window.location.replace('/admin/oders_page/order?id=' + i)
}

function add_tr(i){
    console.log(status)
    st = ' style="border: 1px solid grey;"'
    var html_str = '<tr'+st+'><th'+st+'>'+date[i]+'</th><th'+st+'>'+author[i]+'</th>'
                +'<th'+st+'><input type="button" value="Подробнее" onclick="order_info('+id[i]+')"></th><th'+st+'>' + address[i]+
                '<th'+st+'>'+email[i]+'</th><th'+st+'>'+
                '<select id="select'+id[i]+'">'+
                '<option id="vaiting'+id[i]+'">Ожидает подтверждения</option>'+
                '<option id="confirmed'+id[i]+'">Подтвержден</option>'+
                '<option id="delivered'+id[i]+'">Доставлен</option>'+
                '</selsect>'+
                '</th></tr>'
    $('#tbl').append(html_str);
    var sel = document.getElementById("select"+id[i]);
    if (state[i] == 'Ожидает подтверждения'){
        sel.options[0].selected = true;
    }
    else if (state[i] == 'Подтвержден'){
         sel.options[1].selected = true;
    }
    else{
         sel.options[2].selected = true;
    }
    $('#select'+id[i]).on('focus', function () {
        previous = this.value;
    }).change(function() {
        $.ajax({
        url: '/change_order_status',
        type: "POST",
        data:{
            id: id[i],
            state: sel.value,
        }
    });
        previous = this.value;
    });
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
        url: '/get_all_orders',
        type: "POST",
        success: function (response) {
            date = response['date']
            id = response['id']
            author = response['author']
            email = response['email']
            state = response['status']
            address = response['address']
            create_header()
            for (var i = 0; i < id.length; i += 1){
                add_tr(i)
            }
        }
    });

});
