var char_vals = []
var list_of_exist_values_id = []

function del_val(char_id, val_id){
    var pre_id = '#char' + char_id;
    $(pre_id + 'val' + val_id).remove()
    $(pre_id + 'lab' + val_id).remove()
    $(pre_id + 'btn' + val_id).remove()
    $(pre_id + 'infolab' + val_id).remove()
    for (var i = 0; i < list_of_exist_values_id[char_id].length; i += 1){
        if (list_of_exist_values_id[char_id][i] == val_id){
            list_of_exist_values_id[char_id].splice(i, 1);
            break;
        }
    }
}

function del_char(char_id){
    for (var i = 0; i < list_of_exist_values_id[char_id].length; i += 1){
        console.log(list_of_exist_values_id[char_id])
        del_val(char_id, list_of_exist_values_id[char_id][i])
        i -= 1;
    }
    $('#btn_add_val' + char_id).remove()
    $('#infolab' + char_id).remove()
    $('#btn_remove' + char_id).remove()
    $('#char' + char_id).remove()
}

function add_val(id){
    char_vals[id] += 1;
    list_of_exist_values_id[id].push(char_vals[id])
    var html_str = '<div class="row"> <label id="char'+id+'infolab'+char_vals[id]+'">Значение характеристики:</label>'+
    '<input type="text" name="char'+ id +'" id="char'+id+'val'+char_vals[id]+'">'+
    '<input type="button" value="Удалить значение" onclick="del_val('+ id +', ' + char_vals[id] +')" id="char'+id+'btn'+char_vals[id]+'">'+
    '<label name="val_lab' + id +'" id="char'+id+'lab'+char_vals[id]+'"></label></div>'
    $('#div_char' + id).append(html_str);
}

function add_char(){
    window.counter_chars += 1;
    char_vals.push(0);
    list_of_exist_values_id.push([])
    var html_str = '<div class="row"><div class="container" id="div_char'+ window.counter_chars +'">'+
    '<div class="row"><label id="infolab' + window.counter_chars +'">Характеристика:</label><input type="text" name="char" id="char' + window.counter_chars +'">'+
    '<input type="button" value="Удалить характеристику" onclick="del_char('+ window.counter_chars +')" id="btn_remove'+window.counter_chars+'">'+
     '<label  name="lab" id="lab' + window.counter_categories +'"></label></div>'+
     '<div class="row"></div></div><input type="button" value="Добавить значение" onclick="add_val('+ window.counter_chars +')" id="btn_add_val'+window.counter_chars+'"></div>'
    $('#new-char').append(html_str);
    add_val(window.counter_chars);
}

function add_exist_val(id, val){
    char_vals[id] += 1;
    list_of_exist_values_id[id].push(char_vals[id])
    var html_str = '<div class="row"> <label id="char'+id+'infolab'+char_vals[id]+'">Значение характеристики:</label>'+
    '<input type="text" name="char'+ id +'" value="' + val + '" id="char'+id+'val'+char_vals[id]+'">'+
    '<input type="button" value="Удалить значение" onclick="del_val('+ id +', ' + char_vals[id] +')" id="char'+id+'btn'+char_vals[id]+'">'+
    '<label name="val_lab' + id +'" id="char'+id+'lab'+char_vals[id]+'"></label></div>'
    $('#div_char' + id).append(html_str);
}

function add_exist_char(char_val, values){
    char_vals.push(0);
    list_of_exist_values_id.push([])
    window.counter_chars += 1;
    var html_str = '<div class="row"><div class="container" id="div_char'+ window.counter_chars +'">'+'<div class="row">'+
    '<label id="infolab' + window.counter_chars +'">Характеристика:</label><input type="text" name="char" id="char' + window.counter_chars +'" value="' + char_val + '">'+
    '<input type="button" value="Удалить характеристику" onclick="del_char('+ window.counter_chars +')" id="btn_remove'+window.counter_chars+'">'+
     '<label  name="lab" id="lab' + window.counter_categories +'"></label></div>'+
     '<div class="row"></div></div>'+
     '<input type="button" value="Добавить значение" onclick="add_val('+ window.counter_chars +')" id="btn_add_val'+window.counter_chars+'"></div>'
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
        if (!window.click){
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
                    window.click = true
                    console.log('YES!')
                    $('#done').text("Модификации успешно созданы!")
                    $('#btn_submit').attr('value', 'Перейти к созданию продуктов на складе');
                },
                error: function(xhr, textStatus, errorThrown) {
                        alert("pl report: " + errorThrown + xhr.status + xhr.responseText);
                }
            });
            }
        }
        else{
            window.location.replace('/admin/stock_products/add_stock_product?id=' + get_product_id())
        }
}