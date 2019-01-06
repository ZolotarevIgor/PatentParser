google.charts.load('current', {packages: ['corechart', 'line']});

//ТО КАКИЕ СТРАНЫ МЫ ВЫБРАЛИ, ИХ АЙДИШНИКИ
function FindCon(){
    values = $('#selectId').val();
    //alert(values,param);
    var inp = document.getElementsByName('pat');
    for (var i = 0; i < inp.length; i++) {
        if (inp[i].type == "radio" && inp[i].checked) {
            radioControl(inp[i]);
        }
    }

    var json = {"countries":values,"param":param};
    var myJsonString = JSON.stringify(json);
    
    var request = new XMLHttpRequest();
    request.open('POST', 'index.html', false);
    request.setRequestHeader('Content-Type', 'text/html');
    request.send(myJsonString );
    if (request.status != 200) {
        // обработать ошибку
        // alert( xhr.status + ': ' + xhr.statusText ); // пример вывода: 404: Not Found
        console.error(request.status + ': ' + xhr.statusText);
        console.log(request.responseText);
    } else {
        // вывести результат
        dataJSON = JSON.parse(request.responseText); // responseText -- текст ответа.
    }
    //ПО ПОЛУЧЕННЫМ ДАННЫМ СТРОИМ ГРАФИК
    drawLineColors();
}
function drawLineColors() {
    console.log(values);
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    for (var i=0; i<values.length; i++){
    data.addColumn('number', values[i]);
    }
    
    var mainmas = [];
    year = 2007;//начальный год
    for (var i=0; i<10; i++) //для каждого кода, у каждой страны берем данные из заданного года
    {
        var mas = [];
        mas.push(year); //mas = [2007]
        for (var j = 0; j<values.length;j++){//в цикле по странам берем значение соответствующее этому году
            mas.push(dataJSON["countries"][j]["y"+year]); //mas = [2007, 123, 156, 763]
        }
        mainmas.push(mas);//кидаем данные о годе
        year+=1; //переходим к следующему году
    }
    data.addRows(mainmas);
    
    var options = {
    hAxis: {
        title: 'Time'
    },
    vAxis: {
        title: 'Count'
    }
    
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}
//НАСТРОЙКИ ПОИСКА
$(document).ready( function(e){
    $(".chosen-select").chosen({
        width: "30%",
        disable_search: false,
        disable_search_threshold: 5,
        enable_split_word_search: false,
        max_selected_options: 10,
        no_results_text: "Страна не найдена",
        placeholder_text_multiple: "Выберите страны",
        placeholder_text_single: "Выберите одну страну",
        search_contains: true,
        display_disabled_options: false,
        display_selected_options: false,
        max_shown_results: 5
    });
});

var param;
//СЛУШАЕМ ЧТО НАЖМЕТ ПОЛЬЗОВАТЕЛЬ И ПРИСВАИМ ПАРАМЕТР, ЕГО НАДО ПЕРЕДАТЬ
function radioControl(obj) {
    switch (obj.value){
        case 'a':
            param = 'A';
            break;
        case 'n':
            param = 'N';
            break;
        case 'r':
            param = 'R';
            break;
        case 'rn':
            param = 'R+N';
            break;
        case 'arn':
            param = 'A/(R+N)';
            break;
    }
}