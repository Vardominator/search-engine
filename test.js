$(document).ready(function(){

    // ENABLES 'Build Index' BUTTON IF CORPUS DIRECTORY IS INSERTED
    $('#dir_input').change(function(e){
        if($('#dir_input').val() != ''){
            $('#buildindex_button').removeClass('disabled');
        }else{
            $('#buildindex_button').addClass('disabled');
        }
    });
    
    // BUILD INDEX
    $("#buildindex_button").click(function(e){
        $('#building_index_loader').show();
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

    // EXECUTE QUERY
    $("#query").change(function(e){
        $('#retrieve_documents_loader').show();
        var query_input = $('#query').val();

        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/query",
            data : {query: query_input},
            success: buildRelevantList
        });

        $("#last_query").text($("#query").val());
        $('#query').val("");
        $('#selected_document_title').text("");
        $('#selected_document_body').text("");
    });

    var documentBodies = {};

    // SHOW SELECTED RELEVANT DOCUMENT
    $(document).on("click", "#title_icon", function () {
        var selectedTitle = $(this).text();
        var selectedBody = documentBodies[selectedTitle];
        $('#selected_document_title').text(selectedTitle);
        $('#selected_document_body').text(selectedBody);
    });

    // PRINT DOCUMENT AND TERM COUNT FROM INDEX
    function populateTable(response){
        var res = $.parseJSON(response);
        console.log(res);
        $("#document_count").text(res.doc_count);
        $("#term_count").text(res.term_count);
        $('#building_index_loader').hide()
    }

    // BUILD THE LIST OF RELEVANT FILES
    function buildRelevantList(response){
        var res = $.parseJSON(response);
        $("#relevant_list").empty()

        $.each(res.files, function(index, file){
            title = res.contents[file]['title'];
            body = res.contents[file]['body'];
            documentBodies[title] = body;

            if(body.length > 75){
                body = body.substring(0, 75);
                body = body + "...";
            }

            $("#relevant_list").append(
            '<div class="item">' + 
                '<i class="map marker icon"></i>' + 
                '<div class="content">' +
                    '<a class="header" id="title_icon">' + title + '</a>' +
                    '<div class="description">' +
                        body + 
                    '</div>'
                + '</div>'
            + '</div>');
        });

        $('#retrieve_documents_loader').hide();
        $("#documents_found").text(res.files.length);
    }

    // USED FOR DEBUGGING
    function successCallBack(response){
        console.log(response);
    }

});