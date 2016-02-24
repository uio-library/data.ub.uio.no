
var yasqe = YASQE(document.getElementById('yasqe'),
{
  value: "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n" +
    "PREFIX mads: <http://www.loc.gov/mads/rdf/v1#>\n" +
    "SELECT DISTINCT ?subject WHERE {\n" +
    "  ?subject a mads:Geographic .\n" +
    "}\n" +
    "LIMIT 10",
  sparql: {
    showQueryButton: true,
    endpoint: "/sparql"
    /*defaultGraphs: ['http://data.ub.uio.no/rt']*/
  }
});

var yasr = YASR(document.getElementById('yasr'),
{
  getUsedPrefixes: yasqe.getPrefixesFromQuery,
});

//link both together
yasqe.options.sparql.callbacks.complete = yasr.setResponse;

/*if (!yasr.somethingDrawn()) {
  yasqe.query();
}*/

$('.example').on('click', function (evt) {
  var id = $(this).attr('id');
  evt.preventDefault();
  $.get('examples/' + id + '.rq').success(function(data) {
    yasqe.setValue(data);
  });
});
