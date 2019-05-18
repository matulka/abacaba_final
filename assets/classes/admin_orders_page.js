date = []
author = []
email = []
status = []
id = []

function create_header(){
    st = ' style="border: 1px solid grey;"'
    var html_str = '<table'+st+' id="tbl">'+
                '<tr'+st+'><th'+st+'>Дата</th><th'+st+'>Автор</th><th'+st+'>Наполнение</th><th'+st+'>Адрес</th>' +
                '<th'+st+'>email</th><th'+st+'>Статус</th></tr>'
                '</table>'
    $('#table').append(html_str);
}

function add_tr(i, id){
    st = ' style="border: 1px solid grey;"'
    var html_str = '<tr'+st+'><th'+st+'>'+date[i]+'</th><th'+st+'>'+author[i]+'</th>'
                +'<th'+st+'><input type="button"></th><th'+st+'><input type="button"></th>' +
                '<th'+st+'>'+email[i]+'</th><th'+st+'></th>'+status[i]+'</tr>'
    $('#tbl').append(html_str);
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
            status = response['status']
            create_header()
            for (var i = 0; i < id.length; i += 1){
                add_tr(i, id[i])
            }
        }
    });
});
