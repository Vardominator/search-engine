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

        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/query",
            data : {query: query_input},
            success: buildRelevantList
        });

        $('#query').val("");

    });

    function populateTable(response){
        var res = $.parseJSON(response);
        console.log(res);
        $("#document_count").text(res.doc_count);
        $("#term_count").text(res.term_count);
    }

    function buildRelevantList(response){
        var res = $.parseJSON(response);

        $("#relevant_list").empty()
        $.each(res.files, function(index, file){

            content = res.contents[file];
            if(content.length > 80){
                content = content.substring(0, 100);
                content = content + "...";
            }

            $("#relevant_list").append(
            '<div class="item">' + 
                '<i class="map marker icon"></i>' + 
                '<div class="content">' +
                    '<a class="header">' + file + '</a>' +
                    '<div class="description">' +
                        "blah" + content + 
                    '</div>'
                + '</div>'
            + '</div>');
        });1
        
    }

    function successCallBack(response){
        console.log(response);
    }


});