function add_char(){
    window.counter_chars += 1;

    var html_str = '<div class="row"><div class="container" id="div_char'+ window.counter_chars +'">'+
    '<div class="row"><label>Характеристика:</label><input type="text" name="char" id="char' + window.counter_chars +
     '"> <label  name="lab" id="lab' + window.counter_categories +'"></label></div>'+
     '<div class="row"></div></div><input type="button" value="Доавить значение" onclick="add_val('+ window.counter_chars +')"></div>'
     add_val(window.counter_chars);
    $('#new-char').append(html_str);
}

function get_product_id() {
    var paramstr = window.location.search.substr(1);
    var arr = paramstr.split('=');
    return arr[1];
}

function add_val(id){
    window.counter_chars += 1;
    var html_str = '<div class="row"> <label>Значение характеристики:'+ window.counter_chars +'</label>'+
    '<input type="text" name="char'+ id +'"><label name="val_lab' + id +'"></label></div>'
    window.counter_chars -= 1;
    $('#div_char' + id).append(html_str);
}

$(document).ready(function(){
    window.counter_chars = -1;
    add_char();
    add_val(0);
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
            labs[i].textContent = ""
            for (var k = j + 1; k < values.length; k += 1){
                if (values[i].value == values[j].value){
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
            var csrf_token = $('meta[name="csrf-token"]').attr('content');
            for 
            $.ajax({
            url: '/get_prod_by_name',
            type: "POST",
            data: {
                 name: $('#prod').val(),
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
            success: function (response) {
                id = response['id']
                window.location.replace('/admin/modification_page/add_modification' + '?id=' + id)
            },
            error: function(xhr, textStatus, errorThrown) {
                    alert("pl report: " + errorThrown + xhr.status + xhr.responseText);
            }
        });
        }
}