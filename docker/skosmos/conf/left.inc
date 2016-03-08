{# This is the template for the front page welcome box. You can enter any html here and show different language versions by using the lang value in a twig conditional as demonstrated below. #}
<div class="welcome-box">
  {% if request.lang == 'nb' %}
  <h1>Velkommen til Skosmos</h1>
  <p>
    Med Skosmos kan du navigere og søke i vokabularene på <a href="//data.ub.uio.no/">data.ub.uio.no</a>.
  </p>
  {% elseif request.lang == 'nn' %}
  <h1>Velkommen til Skosmos</h1>
  <p>
    Med Skosmos kan du navigere og søke i vokabularene på <a href="//data.ub.uio.no/">data.ub.uio.no</a>.
  </p>
  {% else %}
  <h1>Welcome to the Skosmos browser!</h1>
  <p>
    Skosmos lets you search and navigate the vocabularies at <a href="//data.ub.uio.no/">data.ub.uio.no</a>.
  </p>
  {% endif %}
</div>
