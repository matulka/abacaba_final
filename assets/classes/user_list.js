rights = []
login = []
email = []
id = []

function create_header(){
    st = ' style="border: 1px solid grey;"'
    var html_str = '<table'+st+' id="tbl">'+
                '<tr'+st+'><th'+st+'>Username</th><th'+st+'>email</th><th'+st+'>Права</th><th'+st+'>Кнопка удаления пользователя</th></tr>' +
                '</table>'
    $('#table').append(html_str);
}


function add_tr(i){
    console.log(status)
    st = ' style="border: 1px solid grey;"'
    var html_str = '<tr'+st+' id="tr'+id[i]+'"><th'+st+' id="log'+id[i]+'">'+login[i]+'</th><th'+st+' id="email'+id[i]+'">'+email[i]+'</th>'+
                '<th'+st+' id="sel'+id[i]+'">'+
                '<select id="select'+id[i]+'">'+
                '<option id="is_staff'+id[i]+'">Права администратора</option>'+
                '<option id="no_staff'+id[i]+'">Обычный пользователь</option>'+
                '</selsect>'+
                '</th><th'+st+' id="del'+id[i]+'"><input type="button" value="Удалить" onclick="del_user('+id[i]+')"</th></tr>'
    $('#tbl').append(html_str);
    var sel = document.getElementById("select"+id[i]);
    if (rights[i]){
        sel.options[0].selected = true;
    }
    else{
         sel.options[1].selected = true;
    }
    $('#select'+id[i]).on('focus', function () {
        previous = this.value;
    }).change(function() {
        is_staff = true
        if (sel.value == "Обычный пользователь"){
            is_staff = false
        }
        $.ajax({
        url: '/change_user_rights',
        type: "POST",
        data:{
            id: id[i],
            is_staff: is_staff,
        }
    });
    });
}


function del_user(id){
     $.ajax({
        url: '/delete_user',
        type: "POST",
        data:{
            id: id,
        },
        success: function (response) {
            $('#tr'+id).remove()
        }
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
        url: '/get_users_except_this',
        type: "POST",
        success: function (response) {
            id = response['id']
            login = response['login']
            email = response['email']
            rights = response['is_staff']
            create_header()
            for (var i = 0; i < login.length; i += 1){
                add_tr(i)
            }
        }
    });

});
