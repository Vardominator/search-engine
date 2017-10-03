$(document).ready(function(){
    // ENABLE ACCORDION FUNCTIONALITY
    $('.ui.accordion').accordion();

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
        $("#showterms_button").removeClass('disabled');
    });

    // SHOW TERMS
    $("#showterms_button").click(function(e){
        
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/showterms",
            success: buildVocabList
        });

    });

    // EXECUTE QUERY
    $("#query").change(function(e){
        var query_input = $('#query').val();

        if(query_input.includes(":stem")){
            var term = query_input.replace(":stem", "").trim()
            console.log(term);
            $.ajax({
                type: "POST",
                url: "http://127.0.0.1:5000/stem",
                data : {term: term},
                success: printTermStem
            });

        }else{
            $('#retrieve_documents_loader').show();
            $.ajax({
                type: "POST",
                url: "http://127.0.0.1:5000/query",
                data : {query: query_input},
                success: buildRelevantList
            });
        }

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
        $("#relevant_list").empty();
        console.log(res.files.length);

        if(res.files.length == 0){
            console.log(res.files.length);
            $("#selected_document_body").text("No documents found.");
            
        }else{

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
                    + '</div>'
                );
            });

            $("#documents_found").text(res.files.length);
        }
        $('#retrieve_documents_loader').hide();
    }

    // BUILD LIST OF VOCAB TERMS
    function buildVocabList(response){
        $("#relevant_list").empty();
        var vocab = ($.parseJSON(response)).vocab;

        $("#relevant_list").append(
            '<div class="ui accordion" id="term_accordion">' +
            '</div>'
        );

        $.each(vocab, function(key, terms){

            $("#term_accordion").append(
                '<div class="title">' +
                    '<i class="dropdown icon"></i>' +
                    key +
                '</div>' + 
                '<div class="content" id="'+ key +'">' +
                '</div>'
            );
            
            for(term of vocab[key]){
                $('#' + key).append(
                    '<p>' + 
                        term + 
                    '</p>'
                );
            };

        });
        $("#term_accordion").accordion("refresh");
    }

    $('.dropdown.icon').click(function(e){
        $("#term_accordion").accordion("refresh");
    });

    // PRINT STEM OF TERM IN DOCUMENT BODY BOXY
    function printTermStem(response){
        var res = $.parseJSON(response)
        $('#selected_document_body').text(
            'The stem of ' + '"' + res['term'] + '"' + ' is '
             + '"' + res['stemmed_term'] + '"'
        );
    }

    // USED FOR DEBUGGING
    function successCallBack(response){
        console.log(response);
    }

});