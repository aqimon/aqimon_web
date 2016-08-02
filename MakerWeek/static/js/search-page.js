var searchType, searchQuery, resultPage;

$("#search-dropdown-options li").on("click", function(){
    $("#search-dropdown-text").text($(this).text());
});
$("#search-dropdown-text").text("Client");

function initiateSearch(){
    searchType = $("#search-dropdown-text").text();
    searchQuery = $("#searchbar").val();
    resultPage=1;
    $("#result-loading").show();
    resultLoad(searchType, searchQuery, resultPage);
}

function generateResultEntry(data){
    data.since = moment(data.timestamp).fromNow();
    tags="";
    for (var i=0; i<data.tags.length; i++){
        tags+=sprintf("<span class=\"label label-info\">%s</span> ", data.tags[i]);
    }
    data.tags = tags;
    contentString=
        '<div class="result-entry"> \
            <div class="result-entry-left"> \
                <span class="h3"> \
                 <a href="/client/%(id)s"> \
                    Client <i>%(name)s</i> \
                 </a> \
                </span> \
                <div class="result-entry-left-secondary"> \
                    Tags: %(tags)s \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Client ID: %(id)s<br /> \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Address: %(address)s<br /> \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Owner: <a href="/user/%(owner)s">%(owner)s</a><br /> \
                </div> \
            </div> \
            <div class="result-entry-right"> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(temperature).1f°C \
                        </div> \
                        <div class="divider"></div> \
                        <div class="result-entry-right-data-text"> \
                            Temperature \
                        </div> \
                </div> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(humidity).1f%% \
                        </div> \
                        <div class="divider"></div> \
                        <div class="result-entry-right-data-text"> \
                            Humidity \
                        </div> \
                </div> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(coLevel).3fppm \
                        </div> \
                        <div class="divider"></div> \
                        <div class="result-entry-right-data-text"> \
                            CO level \
                        </div> \
                </div> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(dustLevel).3fppm \
                        </div> \
                        <div class="divider"></div> \
                        <div class="result-entry-right-data-text"> \
                            Dust level \
                        </div> \
                </div> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(since)s \
                        </div> \
                        <div class="divider"></div> \
                        <div class="result-entry-right-data-text"> \
                            Last update \
                        </div> \
                </div> \
            </div> \
        </div>';
    return sprintf(contentString, data);
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
        for (var i=0; i<recv.length; i++){
            $("#load-more").before(generateResultEntry(recv[i]));
        }
        if (recv.length<10){
            $("#load-more").text("No more results to show :(");
            $("#load-more").prop("disabled", true);
        } else {
            $("#load-more").text("Load more results");
            $("#load-more").prop("disabled", false);
        }
    })
}