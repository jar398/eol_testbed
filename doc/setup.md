# Web application server and databases setup instructions

Here are notes on the setup procedure that I used on a MacBook Pro
running MacOS 10.12.5.  It is similar to what's in
[README.md](https://github.com/EOL/eol_website/blob/master/README.md),
except with an emphasis on traits rather than the repository server.

It's not exactly what I did, since I ran into many problems on the way
and had to fix them, often trying several approaches before finding
one that worked.  Some of the problems took many hours to track down.
I have not independently tested these instructions, so think of them
more as notes that might help you if you need to do a similar
installation.

I probably should have set up a VM (`rvm` ?) and/or an `rbenv`, as
Jeremy recommended, but I was undisciplined and didn't.

Sorry this is such a mess.

 * Clone the [`eol_website`](https://github.com/EOL/eol_website) repository.
 * Jeremy gave me the following instructions, which I didn't follow exactly:

```
    # I don't remember whether I did this command.  I already had xcode installed
    # and I don't think I had to do anything to make it work.
    sudo xcodebuild -license
    # Suppress documentation file creation - speeds things up
    vim ~/.gemrc
    gem: --no-document
    brew update
    brew install rbenv
    brew install libksba bash-completion qt gcc openssl libyaml libffi readline
    # I used the Ruby installed by homebrew, version 2.5.1p57, not 2.4.2
    rbenv install 2.4.2
    rbenv global 2.4.2
    gem install bundler --pre
    # Jeremy says: IT IS BEST IF YOU KILL YOUR SHELL NOW AND RESTART ONE.
    gem install rubocop
    # I don't know why there are two 'gem install's for bundler?
    gem install bundler
    # I don't think I did this command (or maybe it failed).  No matter.
    xcode-select --install
    cd to the eol_website project directory
    # This didn't work for me the first time - nokogiri failed.
    bundle
    rake db:reset
```

 * To get `bundle` to complete without errors for `libxml` or `nokogiri`, 
   I had to consult stackoverflow multiple times.  I'm sorry to say I'm
   not sure exactly what fixed the problem, but my notes end with a reference
   to [this stackoverflow question](https://stackoverflow.com/questions/39937394/gem-install-nokogiri-v-1-6-8-1-fails) and this command:
      * `bundle config build.nokogiri --use-system-libraries --with-xml2-include=/usr/local/opt/libxml2/include/libxml2`
 * Tweak `config/secrets.yml`:
      * Change `url: 'http://localhost:3001'` to `url: 'http://beta-repo.eol.org'` (repository)
 * Install and start `mysql` if not already there.
 * Install and start `neo4j` (I used `brew` - neo4j setup is very easy)
 * At shell: `export EOL_TRAITBANK_URL=http://neo4j:neo4j@localhost:7474` (the second 'neo4j' should be whatever you set the admin password to)
 * Install rails (see `rbenv install` above, or use `brew install` like I did)
 * Set up mysql `eol` user and database.  You'll need to know the `mysql`
   root user password (or else it has to be empty).
      1. `mysql -uroot`
      1. `create database eol_development;`
      1. `create user 'eol'@'localhost' identified by 'eol';`
      1. `grant all privileges on eol_development.* to 'eol'@'localhost';`
      1. `flush privileges;`
 * Update `config/secrets.yml` to set database user to `eol` (and password, if you set one)
 * Initialize database (not sure what this does, seems to create indexes?)
      * `rails r "TraitBank::Admin.setup"`
 * I don't know why this is needed, but it is: (from Jeremy)
      * `rails r "ImportRun.delete_all"`
 * Get resources and terms from beta repository:
      * `rake sync`  (this takes about 15 minutes)
 * Get production publishing site resources list.  I got this file from Jeremy, and I don't know how he made it.  Put the file at `pub-site-resources.json` in the main `testbed` directory (path is hardwired in upcoming `clobber_resource_ids.rb` script).
 * The following assumes the `testbed` and `eol_website` repository clones are siblings in the file system.
 * Change the resource ids that we got from the harvesting/repository site to avoid conflicts with publishing site resource ids (at mysql prompt):
      * `mysql -ueol eol_development`
      * `update resources set id = id + 1000;`
 * Clobber resource ids to match beta publishing site: <br/>
      * `(cd ../eol_website; rails r ../testbed/clobber_resource_ids.rb)`
 * Start the rails server (on default port, 3000):
      * `rails s &`
 * Just for fun, visit resources list http://localhost:3000/resources.  You'll get the error "Migrations are pending. To resolve this issue, run: bin/rake db:migrate RAILS_ENV=development".
      * Fix this as directed.  (just `rake` instead of `bin/rake`)
 * Grab parent/child relationships from opendata:
      * rake terms:fetch
 * [If you look at `/terms` you should see the terms list.]
 * Load the dynamic taxonomic hierarchy: <br/>
      * `rake publish ID=1`
 * Load traits resources as desired.  Resource ids are same as on publishing site.
   Warning: Some of the resources listed in other places are not be available via this route.
   E.g. the following gets resource `sal_et_al_2013`: <br />
      * `rake publish ID=455`

I have a nagging feeling that while trying to get nokogiri to install
I may have had to do something to configure xcode (or the gcc command)
to use clang instead of gcc, but don't remember for sure.  I certainly
didn't _want_ to do this, so perhaps I managed to avoid it.

Learned the hard way: When starting and stopping neo4j, do *not* mix
use of `brew services start neo4j` (or `brew services stop neo4j`, etc) with use of
the `neo4j` shell command e.g. `neo4j start`.  They do not play nicely
together.

Example of command line access to neo4j's Cypher endpoint:

    curl --user neo4j:neo4j \
         -H "Content-type: application/json" \
         -H "Accept: application/json; charset=UTF-8" \
         -d '{"statements" : [ {"statement" : "call dbms.showCurrentUser()"} ]}' \
         http://localhost:7474/db/data/transaction/commit

You can also play with neo4j using [the
web console](http://localhost:7474/) or the `cypher-shell` command.
