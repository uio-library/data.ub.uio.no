{# This is the template for the about page. You can enter any html here and show different language versions by using the lang value in a twig conditional as demonstrated below. #}
{% if request.lang == 'en' %}

<h4>About</h4>
<p>
	<a href="http://data.ub.uio.no">data.ub.uio.no</a> is a platform
	for controlled subject vocabularies as linked open data.
</p>
<p>
	To support search and navigation, we have installed the Skosmos
	ontology browser from the National Library of Finland.
	<a href="http://github.com/NatLibFi/Skosmos">Skosmos on GitHub</a>.
</p>
<p>
	If you want to reuse data, here's <a href="http://data.ub.uio.no/dumps">data dumps</a>,
	a <a href="http://data.ub.uio.no/query">SPARQL endpoint</a>
	and a
	<a href="http://data.ub.uio.no/skosmos/rest/v1/vocabularies?lang=nb">REST-API</a>
	(<a href="https://github.com/NatLibFi/Skosmos/wiki/REST-API">documentation</a>).
</p>

{% elseif request.lang == 'nn' %}

<h4>Om</h4>
<p>
	<a href="http://data.ub.uio.no">data.ub.uio.no</a> er ei
	plattform for kontrollerte emnevokabular som opne lenka data.
</p>
<p>
	For å gjere det enkelt å søkje og navigere i vokabulara har
	vi installert Skosmos, ein applikasjon utvikla ved Finlands nasjonalbibliotek.
	<a href="http://github.com/NatLibFi/Skosmos">Skosmos på GitHub</a>.
</p>
<p>
	Om du ynskjer å gjenbruke dataa våre finst det <a href="http://data.ub.uio.no/dumps">datadumpar</a>,
	eit <a href="http://data.ub.uio.no/query">SPARQL-endepunkt</a>
	og eit
	<a href="http://data.ub.uio.no/skosmos/rest/v1/vocabularies?lang=nb">REST-API</a>
	(<a href="https://github.com/NatLibFi/Skosmos/wiki/REST-API">dokumentasjon</a>).
</p>

{% else %}

<h4>Om</h4>
<p>
	<a href="http://data.ub.uio.no">data.ub.uio.no</a> er en
	plattform for kontrollerte emnevokabularer som åpne lenkede data.
</p>
<p>
	For å gjøre det enkelt å søke og navigere i vokabularene har
	vi installert Skosmos, en applikasjon utvikla ved Finlands nasjonalbibliotek.
	<a href="http://github.com/NatLibFi/Skosmos">Skosmos på GitHub</a>.
</p>
<p>
	Om du ønsker å gjenbruke dataene våre finnes det <a href="http://data.ub.uio.no/dumps">datadumper</a>,
	et <a href="http://data.ub.uio.no/query">SPARQL-endepunkt</a>
	og et
	<a href="http://data.ub.uio.no/skosmos/rest/v1/vocabularies?lang=nb">REST-API</a>
	(<a href="https://github.com/NatLibFi/Skosmos/wiki/REST-API">dokumentasjon</a>).
</p>

{% endif %}
