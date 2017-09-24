$(document).ready(function(){
    $("#buildindex_button").click(function(e){
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/buildindex",
            success: successCallBack
        });
    });

    $("#search_button").click(function(e){
        console.log("button clicked asdasdf");
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/test",
            success: successCallBack
        });
    });

    function successCallBack(response){
        console.log(response);
    }

});