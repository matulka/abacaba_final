function add_val(id){
    console.log(id);
    window.counter_chars += 1;
    var html_str = '<div class="row"> <label>Значение характеристики:'+ window.counter_chars +'</label>'+
    '<input type="text" name="char'+ id +'"><label name="val_lab' + id +'"></label></div>'
    window.counter_chars -= 1;
    $('#div_char' + id).append(html_str);
}

function add_char(){
    window.counter_chars += 1;
    var html_str = '<div class="row"><div class="container" id="div_char'+ window.counter_chars +'">'+
    '<div class="row"><label>Характеристика:</label><input type="text" name="char" id="char' + window.counter_chars +
     '"> <label  name="lab" id="lab' + window.counter_categories +'"></label></div>'+
     '<div class="row"></div></div><input type="button" value="Доавить значение" onclick="add_val('+ window.counter_chars +')"></div>'
    $('#new-char').append(html_str);
    add_val(window.counter_chars);
}

function add_exist_val(id, val){
    console.log(id);
    window.counter_chars += 1;
    var html_str = '<div class="row"> <label>Значение характеристики:'+ window.counter_chars +'</label>'+
    '<input type="text" name="char'+ id +'" value="' + val + '"><label name="val_lab' + id +'"></label></div>'
    window.counter_chars -= 1;
    $('#div_char' + id).append(html_str);
}

function add_exist_char(char_val, values){
    window.counter_chars += 1;
    var html_str = '<div class="row"><div class="container" id="div_char'+ window.counter_chars +'">'+
    '<div class="row"><label>Характеристика:</label><input type="text" name="char" id="char' + window.counter_chars +
     '" value="' + char_val + '"> <label  name="lab" id="lab' + window.counter_categories +'"></label></div>'+
     '<div class="row"></div></div><input type="button" value="Доавить значение" onclick="add_val('+ window.counter_chars +')"></div>'
    $('#new-char').append(html_str);
    for (var i = 0; i < values.length; i += 1){
        add_exist_val(window.counter_chars, values[i])
    }
}

function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}

$(document).ready(function(){
    window.counter_chars = -1;
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
        url: '/have_modifications',
        type: "POST",
        data: {
            id: get_product_id(),
        },
        success: function (response) {
            if (response['have']){
                console.log(response['values'])
                for (var i = 0; i < response['char'].length; i += 1){
                    add_exist_char(response['char'][i], response['values'][i])
                }
                $('#title').text('Изменение модификаций')
            }
            else{
                add_char();
            }
        }
    });
});

function check_characteristics(){
    var char = document.getElementsByName('char');
    var lab = document.getElementsByName('lab');
    var answer = false;
    for (var i = 0; i < char.length; i += 1){
        lab[i].textContent = ""
        for (var j = i + 1; j < char.length; j += 1){
            if (char[i].value == char[j].value){
                lab[i].textContent = "Поля совпадают!";
                lab[j].textContent = "Поля совпадают!";
                answer = true;
            }
        }
        if (char[i].value == ""){
            lab[i].textContent = "Заполните поле!";
            answer = true;
        }
    }
    return answer;
}

function check_values(){
    var char = document.getElementsByName('char');
    var answer = false;
    for (var i = 0; i < char.length; i += 1){
        var id = char[i].id;
        id = id.substring(4);
        var values = document.getElementsByName('char' + id);
        var labs = document.getElementsByName('val_lab' + id);
        for (var j = 0; j < values.length; j += 1){
            labs[j].textContent = ""
            for (var k = j + 1; k < values.length; k += 1){
                if (values[k].value == values[j].value){
                labs[j].textContent = "Поля совпадают!";
                labs[k].textContent = "Поля совпадают!";
                answer = true;
            }
            }
            if (values[j].value == ""){
                labs[j].textContent = "Заполните поле!";
                answer = true;
            }
        }
    }
    return answer;
}

function valid_form(){
        var has_errors = false;
        check_characteristics();
        has_errors = has_errors || check_characteristics();
        check_values();
        has_errors = has_errors || check_values();
        if (!has_errors){
            var char = document.getElementsByName('char');
            var char_names = []
            var val = []
            for (var i = 0; i < char.length; ++i){
                char_names.push(char[i].value)
            }
            console.log(char_names)
            for (var i = 0; i < char.length; i += 1){
                var id = char[i].id;
                val.push([])
                id = id.substring(4);
                var values = document.getElementsByName('char' + id);
                for (var j = 0; j < values.length; j += 1){
                    val[i].push(values[j].value);
                }
            }
            console.log(val)
            $.ajax({
            url: '/form_modifications',
            type: "POST",
            data: {
                 characteristics: char_names,
                 'values[]': val,
                 id: get_product_id,
            },
            success: function (response) {
                console.log('TES');
            },
            error: function(xhr, textStatus, errorThrown) {
                    alert("pl report: " + errorThrown + xhr.status + xhr.responseText);
            }
        });
        }
}