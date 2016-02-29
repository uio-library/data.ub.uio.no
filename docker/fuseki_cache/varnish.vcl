vcl 4.0;

backend default {
    .host = "fuseki";
    .port = "3030";
}

sub vcl_backend_response {
	# Allow Varnish to serve objects that are up to five minutes out of date.
	# When it does it will also schedule a refresh of the object.
	set beresp.grace = 5m;

    # Store for a long time (1 week)
    set beresp.ttl = 1w;

    # Always gzip before storing, to save space in the cache
    set beresp.do_gzip = true;
}