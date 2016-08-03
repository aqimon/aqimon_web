var searchType, searchQuery, resultPage;

$("#search-dropdown-options li").on("click", function(){
    $("#search-dropdown-text").text($(this).text());
});

function initiateSearch(){
    searchType = $("#search-dropdown-text").text();
    searchQuery = $("#searchbar").val();
    resultPage=1;
    $("#result").html("");
    $("#result-loading").show();
    resultLoad(searchType, searchQuery, resultPage);
}

$("#load-more").on("click", function(){
    $("#load-more").text("Loading");
    $("#load-more").prop("disabled", true);
    resultPage++;
    resultLoad(searchType, searchQuery, resultPage);
})

function resultLoad(searchType, searchQuery, resultPage){
    query = {
        "type": searchType,
        "q": searchQuery,
        "page": resultPage
    }
    $.getJSON("/ajax/search", query, function(recv){
        if (resultPage == 1){
            $("#result-loading").hide();
            $("#load-more").show();
        }
        console.log(recv);
        for (var i=0; i<recv.length; i++){
            if (searchType == "Clients")
                $("#result").append(generateClientResultEntry(recv[i]));
            else if (searchType == "Tags")
                $("#result").append(generateTagResultEntry(recv[i]));
            else if (searchType == "Users")
                $("#result").append(generateUserResultEntry(recv[i]));
            else
                return;
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