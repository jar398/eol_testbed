# EOL V3 authentication and authorization

The idea - correct me if I'm wrong - is that we might have a set of
traits-related web services to which access would limited to read-only
use by a limited set of users.  The purposes of the access controls
are:

   * delay general user reviews until we're ready for them, by preventing 
     access by anyone who is not registered for access
   * prevent modifications to the traits DB (either intentional or accidental),
   * prevent denial of service attacks (either intentional or accidental).

To this end, there would be user logins.  We grant read access to all
controlled services to anyone who has a login.

The desired state is three levels of authorization:

   1. No access except through the web app (the default)
   2. Read access using a web API and/or Cypher
   3. Any kind of access (administrator) but maybe not via the web API

Architecturally, there are three choices for where we might institute
such controls:

   1. nginx (the web server)
   1. rails (the web application)
   1. neo4j (the traits database)

In any of these scenarios, logins would be manually administered by
EOL staff.  That includes adding accounts and resetting passwords.
This approach does not scale well, e.g. it does not allow web-based
registration.  Scalable approaches do exist but I won't talk about them.

## 1. Use neo4j security

We have determined that while neo4j community edition does have user
logins, all authenticated users have administrator access, and so can
do arbitrary writes to the graphdb.  We therefore won't be considering
neo4j security as an option at this time.  The other two options are
examined below.

## 2. Use nginx security

There are several perfectly good tutorials for authentication and
authorization in nginx, for example [this
one](https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-14-04).

The granularity of control is the `location`, which is usually some
part of the URL space served by the server.  For example:

        location /private {
            root   html;
            auth_basic "Restricted Content";
            auth_basic_user_file /usr/local/etc/nginx/htpasswd;
        }

The above would require login for access to the file `private.html`
(as well as to any other file or directory that begins with
'`private`').  One thing the tutorials (and the nginx documentation
itself) don't explicitly say is that an nginx `location` can be a
single file or API call.

## 3. Use rails security

Rails has its own security infrastructure, maybe not too different
(for present purposes) from nginx's.  I have not investigated how this
works but evidence of its activation in the web app is
[here](https://github.com/EOL/eol_website/blob/master/app/controllers/application_controller.rb).

## How to choose

I have not evaluated rails security yet.  I think the goals in
deciding between nginx and rails would be

  * Avoid redundant user lists - if any other part of the web application
    needs user registration, it would be stupid to have to register a
    user and password with nginx, and then have to turn around and
    register the same user name and password with rails.  Password 
    update and recovery would be awful, and so on.
  * Avoid interference - if security is needed for two widely
    divergent purposes, and user registrations are not or should not
    be shared, then it would make sense to put the two facilities in
    different layers of the stack.

Personally I'd prefer using nginx if possible, simply because the
rails setup is an unknown.  I think that for maintenance purposes this
could be better just because nginx is so simple and keeping the
security layer in nginx prevents rails errors that could cripple the
web app.

On the other hand, rails security is almost certain to have features
that nginx doesn't, such as fine-grained access control or user
groups, and if we may end up needing these features in the future, we
might be better off with rails security.

## How to prevent writes to the databases

In the web application, and in any web API services we write, database
writes are prevented simply by the way in which database commands are
composed.  That is, access policy adherence is an automatic
consequence of the code.

Should we decide to implement pass-through access to neo4j, i.e. a way
for logged-in users to compose a Cypher query and pass it directly to
neo4j for execution, then we would need some assurance that
graph-modifying commands (`UPDATE`, `CREATE`, or `DELETE`) don't get through.

It's not clear that pass-through access is desirable, especially if a
more full-fledged web API is on the way, but it might be a good
stopgap to use while the web API is under development.

If there is pass-through access, we would have to somehow prevent
Cypher commands containing modification verbs.

One idea I had would be to use a 307 redirect.  The command gets
checked, and if it seems OK then the service returns a 307 redirect to
a second service that does a direct pass-through to neo4j.  This
approach does not protect against malicious attacks by registered
users, but it does give protection against mistakes.  The advantage of
using a 307 instead of a non-redirecting service is that a direct
neo4j pass-through removes the need for result set buffering in
between neo4j and the user.
