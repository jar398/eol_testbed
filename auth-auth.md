# EOL V3 authentication and authorization

The idea - correct me if I'm wrong - it that we might have a set of
web services, or perhaps only one web service, to which access would
be controlled.  The main purposes of the control are:

    * prevent denial of service attacks (intentional or accidental),
    * delay general user reviews until we're ready for them.

To this end, there would be user logins.  We grant access to all
controlled services to anyone who has a login.


## Plan A: use nginx.

Basic authentication for nginx is very simple.  It provides for three authorization levels: 

    * public (the default)
    * logged in
    * access denied to everyone

There are several perfectly good tutorials, for example [this one](https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-14-04).

The granularity of control is the `location`, which is usually a
directory.  One thing the tutorials don't explicitly say is that an
nginx `location` can be a single file.  For example:

        location /private {
            root   html;
            auth_basic "Restricted Content";
            auth_basic_user_file /usr/local/etc/nginx/htpasswd;
        }

would require login for access to the file `private.html` (as well as
to any other file or directory that begins with '`private`').

Logins would be manually administered by EOL staff.  That includes
adding accounts and resetting passwords.

## Plan B: use authentication and authorization built in rails.



## How to prevent writes to the databases

If there is any nontrivial code handling the web services, then it can
be responsible for making sure that the database commands it invokes
will only use `SELECT`, not `UPDATE`, `CREATE`, or `DELETE.

Should we decide to implement pass-through access to neo4j, i.e. a way
for logged-in users to compose a Cypher query and pass it directly to
neo4j for execution, then we would need some assurance that
graph-modifying commands don't get through.

It's not clear this is desirable, especially if a more full-fledged
web API is on the way, but I'll talk about it just in case.  (It might
be a good stopgap to use while the web API is udner development.)

Here are some ways to do this kind of attenuation:

  * Use neo4j authorization (roles).  This would do exactly what we
    need.  Unfortunately this feature is not part of neo4j community
    edition, so it is not an option at present.
  * Write the Cypher service as a rails service, with code to filter
    out troublesome verbs.  The rails service would in turn call out 
    to neo4j, and any results would be passed to the caller.
  * The previous idea doesn't work so well for very large result sets,
    since the result might have to be buffered in memory (depending on
    what rails lets us do, which I don't know).  To avoid this, and
    perhaps to get a simpler solution, the request could do a 307
    redirect, after checking the content, to a second URL that can
    forward directly to neo4j.  This does not protect against
    malicious attacks, but it does give some protection against
    mistakes.

