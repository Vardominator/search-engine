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

        var buildIndex = false
        if($("#build_checkbox").hasClass("checked")){
            buildIndex = true
        }

        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/buildindex",
            data : {corpus_dir: dir, build: buildIndex},
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
    $("#query").keypress(function(e){
        if(e.which == 13){
            $("#spell_correction").hide()
            var queryInput = $('#query').val();
            var ranked = $("#ranked").hasClass('active')
            $("#documents_found").text("")
            
            if(queryInput.includes(":stem")){
                var term = queryInput.replace(":stem", "").trim()
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
                    data : {query: queryInput, rankedRetrieval:ranked},
                    success: buildRelevantList
                });
            }

            $("#last_query").text($("#query").val());
            $('#query').val("");
            $('#selected_document_title').text("");
            $('#selected_document_body').text("");
        }
    });

    // HANDLE CORRECTED QUERY CLICK
    $("#correct_query_anchor").click(function(e){
        $("#spell_correction").hide()
        $('#retrieve_documents_loader').show();
        var ranked = $("#ranked").hasClass('active')
        var queryInput = $('#corrected_query').text();
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/query",
            data : {query: queryInput, rankedRetrieval:ranked},
            success: buildRelevantList
        });
        $("#last_query").text(queryInput);
    })

    // HANDLE MODE SWITCH
    $("#boolean").click(function(e){
        $("#boolean").addClass("active");
        $("#ranked").removeClass("active");
    });
    $("#ranked").click(function(e){
        $("#ranked").addClass("active");
        $("#boolean").removeClass("active");
    });

    // BUILD CHECKBOX
    $("#build_checkbox").click(function(e){
        if($("#build_checkbox").hasClass("checked")){
            $("#build_checkbox").removeClass("checked");
            $('#buildindex_button').text("Use Index")
        }else{
            $("#build_checkbox").addClass("checked");
            $('#buildindex_button').text("Build Index")
        }
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
        $("#document_count").text(res.doc_count);
        $("#term_count").text(res.term_count);
        $('#building_index_loader').hide()
    }

    // BUILD THE LIST OF RELEVANT FILES
    function buildRelevantList(response){
        var res = $.parseJSON(response);
        $("#relevant_list").empty();
        $("#selected_document_body").empty();
        if(res.files.length == 0){
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
            })
            $("#documents_found").text(res.files.length);
        }

        if(res.ranked){
            $('#selected_document_title').text("Document Scores");
            var scores = ""
            $.each(res.scores, function(index, score){
                scores += score
                scores += '<br>'
            })
            $('#selected_document_body').append(scores);
        }
        if(res.spell_corrected != null){
            console.log(res.spell_corrected)
            $('#corrected_query').text("")
            $('#corrected_query').append(res.spell_corrected)
            $('#spell_correction').show()
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