function generateClientResultEntry(data){
    data.since = moment(data.timestamp).fromNow();
    data.timeString = moment(data.timestamp).format();
    tags="";
    for (var i=0; i<data.tags.length; i++){
        tags+=sprintf("<a href=\"/tags/%s\" class=\"label label-info\">%s</a> ", data.tags[i], data.tags[i]);
    }
    data.tags = tags;
    if (data.owner_realname == "")
        data.owner_realname = data.owner_username;
    contentString=
        '<div class="result-entry"> \
            <div class="result-entry-left"> \
                <span class="h3"> \
                 <a href="/client/%(id)s"> \
                    Client <i>%(name)s</i> \
                 </a> \
                </span> \
                <div class="result-entry-left-secondary"> \
                    <span class="glyphicon glyphicon-tag"></span> %(tags)s \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Client ID: %(id)s<br /> \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Address: %(address)s<br /> \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Owner: <a href="/user/%(owner_username)s">%(owner_realname)s</a><br /> \
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
                <div class="result-entry-right-data" data-toggle="tooltip" data-placement="top" title="%(timeString)s"> \
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

function generateTagResultEntry(data){
    contentString=
        '<div class="result-entry result-entry-tag"> \
            <div class="result-entry-left"> \
                <span class="h3"> \
                 <a href="/tags/%(title)s"> \
                    Tag <span class="label label-info">%(title)s</span> \
                 </a> \
                </span> \
                <div class="result-entry-left-secondary"> \
                   Description: %(description)s \
                </div> \
                <div class="result-entry-left-secondary"> \
                    Tagged in %(count)d clients \
                </div> \
            </div> \
        </div>';
    return sprintf(contentString, data);
}