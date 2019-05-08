function add_cat(){
    window.counter_categories += 1;
    var html_str = '<div class="row"><input list="categories" name="cat"> <label list="categories" name="lab"></label></div>'
    $('#new-cat').prepend(html_str);
}
$(document).ready(function(){
    console.log('af');
    window.counter_categories = 0;
});
function valid_form(){
    var has_errors = false
    if ($('#id_name').val().length < 1){
        has_errors =true;
        $('#name_err').text("Заполните поле!")
    }
    if ($('#id_price').val().length < 1){
        has_errors =true;
        $('#price_err').text("Заполните поле!")
    }
    if ($('#id_price').val() < 0){
        has_errors =true;
        $('#price_err').text("Цена должна быть положительной!")
    }
     if ($('#id_rating').val().length > 0){
         if ($('#id_rating').val() < 0 || $('#id_rating').val() > 5){
            has_errors =true;
            $('#rating_err').text("Рейтинг должен быть в пределах от 0 до 5!")
         }
    }
    var categories = document.getElementsByName('cat');
    for (var i = 0; i <= categories.length; ++i){
        for (var j = 0; i <= categories.length; ++i){
            if ($.text() != "") console.log("ORY");
        }
        if ($.text() != "") console.log("ORY");
    }
}