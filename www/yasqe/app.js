
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
    endpoint: "/sparql",
    requestMethod: "GET"
    /*defaultGraphs: ['http://data.ub.uio.no/rt']*/
  },
  viewportMargin: Infinity,
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

$('#examples').on('change', function () {
  console.log(this.value);
  if (this.value == '') return;
  $.get('examples/example' + parseInt(this.value, 10) + '.rq').success(function(data) {
    yasqe.setValue(data);
  });
});
