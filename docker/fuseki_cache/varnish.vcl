vcl 4.0;

backend default {
    .host = "fuseki";
    .port = "3030";
}

sub vcl_backend_response {

    # Allow Varnish to serve objects that are up to five minutes out of date.
    # When it does it will also schedule a refresh of the object.
    set beresp.grace = 5m;

    # Store for a long time (1 day)
    set beresp.ttl = 1d;

    /* Set the clients TTL on this object */
    set beresp.http.Cache-Control = "public, max-age=86400";

    # Always gzip before storing, to save space in the cache
    set beresp.do_gzip = true;
}

sub vcl_deliver {
    unset resp.http.Pragma;

    # Add a header indicating hit/miss
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }
}
