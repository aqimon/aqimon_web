var resultPage=1;

$("#load-more").on("click", function(){
    $("#load-more").text("Loading");
    $("#load-more").prop("disabled", true);
    resultPage++;
    resultLoad(resultPage);
})

function resultLoad(resultPage){
    query = {
        "title": tagTitle,
        "page": resultPage
    }
    $.getJSON("/ajax/tags/list_clients", query, function(recv){
        if (resultPage == 1){
            $("#result-loading").hide();
            $("#load-more").show();
        }
        for (var i=0; i<recv.length; i++){
            $("#result").append(generateClientResultEntry(recv[i]));
        }
        $('[data-toggle="tooltip"]').tooltip()
        if (recv.length<10){
            $("#load-more").text("No more results to show :(");
            $("#load-more").prop("disabled", true);
        } else {
            $("#load-more").text("Load more results");
            $("#load-more").prop("disabled", false);
        }
    })
}