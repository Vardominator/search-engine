$(document).ready(function(){

    $('#dir_input').change(function(e){
        if($('#dir_input').val() != ''){
            $('#buildindex_button').removeClass('disabled');
        }else{
            $('#buildindex_button').addClass('disabled');
        }
    });
    
    $("#buildindex_button").click(function(e){
        var dir = $('#dir_input').val();
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/buildindex",
            data : {corpus_dir: dir},
            success: populateTable
        });
        $('#dir_input').val("");
        $('#buildindex_button').addClass('disabled');
    });

    $("#query").change(function(e){
        var query_input = $('#query').val();

        //if(query_input != ''){
        var query_input = $('#query').val();
        console.log(query_input);
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/query",
            data : {query: query_input},
            success: successCallBack
        });
        //}

        $('#query').val("");
    });

    function populateTable(response){
        console.log(response.doc_count);
        var res = $.parseJSON(response);
        $("#document_count").text(res.doc_count);
        $("#term_count").text(res.term_count);
    }

    function successCallBack(response){
        console.log(response);
    }


});