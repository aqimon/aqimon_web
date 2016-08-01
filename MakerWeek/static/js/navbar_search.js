var navbarSearchBloodhound = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace("name"),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: "/ajax/search?type=Client&q=%q",
        wildcard: "%q"
    }
})

$("#search-bar").typeahead({
    highlight: true,
}, {
    source: navbarSearchBloodhound,
    display: 'name',
    templates: {
        empty: "<div class=\"autocomplete-status\">Oops, I couldn't find any :(</div",
        pending: "<div class=\"autocomplete-status\">Loading</div>",
        suggestion: function(data){
            return $("<a>").prop("href", "/client/"+data.clientid).text(data.name);
        }
    }
})