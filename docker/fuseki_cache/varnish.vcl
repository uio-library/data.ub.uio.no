vcl 4.0;

backend default {
    .host = "fuseki";
    .port = "3030";
}

acl banners {
    "172.17.0.0"/16;  # Docker
    "172.18.0.0"/16;  # Docker
}

sub vcl_recv {
    if (req.method == "BAN") {
        if (!client.ip ~ banners) {
            return(synth(405, "Not allowed from this IP."));
        }

        # Lurker-friendly ban
        # Assumes the ``X-Ban-Url`` header is a regex,
        # this might be a bit too simple.
        # <http://book.varnish-software.com/4.0/chapters/Cache_Invalidation.html>
        ban("obj.http.x-url ~ " + req.http.x-ban-url);

        # Throw a synthetic page so the request won't go to the backend.
        return(synth(200, "Ban added"));
    }
}

sub vcl_backend_response {

    # Unset cookies so we can cache more requests
    unset beresp.http.set-cookie;

    # Allow Varnish to serve objects that are up to five minutes out of date.
    # When it does it will also schedule a refresh of the object.
    set beresp.grace = 5m;

    # Store for a long time (1 week)
    set beresp.ttl = 1w;

    /* Set the clients TTL on this object */
    set beresp.http.Cache-Control = "public, max-age=86400";

    # Always gzip before storing, to save space in the cache
    set beresp.do_gzip = true;

    # Part of cache invalidation
    set beresp.http.x-url = bereq.url;
}

sub vcl_deliver {
    unset resp.http.Pragma;

    # Add a header indicating hit/miss
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    # The X-Url header is for internal use only
    unset resp.http.x-url;
}
