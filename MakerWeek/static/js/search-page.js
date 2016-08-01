var searchType, searchQuery, resultPage;

$("#search-dropdown-options li").on("click", function(){
    $("#search-dropdown-text").text($(this).text());
});
$("#search-dropdown-text").text("Client");

function initiateSearch(){
    searchType = $("#search-dropdown-text").text();
    searchQuery = $("#searchbar").val();
    resultPage=1;
    resultLoading();
    resultLoad(searchType, searchQuery, resultPage);
}

function resultLoading(){
    $("#result").html("Loading");
}

function generateResultEntry(data){
    contentString=
        '<div class="result-entry"> \
            <div class="result-entry-left"> \
                <h3> \
                 <a href="/client/%(id)s"> \
                    Client <i>%(name)s</i> \
                 </a> \
                </h3> \
                <div class="result-entry-left-secondary"> \
                    Client ID: %(id)s<br /> \
                </div> \
            </div> \
            <div class="result-entry-right"> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(temperature).3f°C \
                        </div> \
                        <div class="divider"></div> \
                        <div class="result-entry-right-data-text"> \
                            Temperature \
                        </div> \
                </div> \
                <div class="result-entry-right-data"> \
                        <div class="result-entry-right-data-number"> \
                            %(humidity).3f%% \
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
            </div> \
        </div>';
    return sprintf(contentString, data);
}

function resultLoad(searchType, searchQuery, resultPage){
    query = {
        "type": searchType,
        "q": searchQuery,
        "page": resultPage
    }
    $.getJSON("/ajax/search", query, function(data){
        console.log(data);
        for (i=0; i<data.length; i++){
            $("#result").append(generateResultEntry(data[i]));
        }
        $("#entry").append("here comes the load more");
    })
}