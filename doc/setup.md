# 'Publishing' server setup instructions

Here are notes on the setup procedure that I used.  It is similar to
what's in
[README.md](https://github.com/EOL/eol_website/blob/master/README.md),
except with an emphasis on traits rather than the repository server.

Well, it's not exactly what I did, since I ran into many problems on
the way and had to fix them.  Some of the problems took many hours to
track down.

I probably should have set up a VM (`rvm` ?) and/or an `rbenv`, as
Jeremy recommended, but I was undisciplined and didn't.

 * Clone the [`eol_website`](https://github.com/EOL/eol_website) repository.
 * Jeremy gave me the following instructions, which I didn't follow exactly:

    \# I don't think this worked for me.  I already had xcode installed
    \# and didn't have to do anything to make it work.
    sudo xcodebuild -license
    \# Suppress documentation file creation - speeds things up
    vim ~/.gemrc
    gem: --no-document
    brew update
    brew install rbenv
    brew install libksba bash-completion qt gcc openssl libyaml libffi readline
    \# I used the Ruby installed by homebrew, version 2.5.1p57, not 2.4.2
    rbenv install 2.4.2
    rbenv global 2.4.2
    gem install bundler --pre
    \# Jeremy: IT IS BEST IF YOU KILL YOUR SHELL NOW AND RESTART ONE.
    gem install rubocop
    \# I don't know why bundler is installed twice?
    gem install bundler
    \# I don't think I did this command (or maybe it failed).  No matter.
    xcode-select --install
    cd to the eol_website project directory (which you get from github)
    \# This didn't work the first time - nokogiri failed.
    bundle
    rake db:reset

 * To get `bundle` to complete without errors for `libxml` or `nokogiri`, 
   I had to check stackoverflow multiple times.  I'm sorry to say I'm
   not sure exactly what fixed the problem, but my notes end with a reference
   to [this stackoverflow question](https://stackoverflow.com/questions/39937394/gem-install-nokogiri-v-1-6-8-1-fails) and <br />
    `bundle config build.nokogiri --use-system-libraries --with-xml2-include=/usr/local/opt/libxml2/include/libxml2`
 * Tweak secrets.yml:
      * Change `3000` to `2999` (because we are not running the publishing server)
      * Change `url: 'http://localhost:3000'` to `url: 'http://beta-repo.eol.org'`
 * Install mysql if not already there
 * Install and start neo4j (I used `brew` - the setup is very easy)
 * At shell: `export EOL_TRAITBANK_URL=http://neo4j:YOURNEWPASSWORD@localhost:7474`
 * Install rails (see `rbenv install` above, or use `brew install` like I did)
 * Install and start mysql
 * Set up mysql 'eol' user and database.  You'll need to know the `mysql`
   root user password (or else it has to be empty).
      1. `mysql -uroot`
      1. `create database eol_development;`
      1. `create user 'eol'@'localhost' identified by 'eol';`
      1. `grant all privileges on eol_development.* to 'eol'@'localhost';`
      1. `flush privileges;`
 * Initialize database (not sure what this does, seems to create indexes?)
      * `rails r "TraitBank::Admin.setup"`
 * Start rails server
      * `rails s`
 * I don't know why this is needed but it is: (from Jeremy)
      * `rails r "ImportRun.delete_all"`
 * Get resources and terms from repository:
      * `rake sync`  (this takes about 15 minutes)
 * Change harvesting site resource ids to avoid conflicts with publishing site resource ids (at mysql prompt):
      * `update resources set id = id + 1000;`
 * Get production publishing site resources list.  I got this file from Jeremy, and I don't know how he made it.  Put the file at `pub-site-resources.json` in `testbed` directory (path is hardwired in upcoming script)
 * The following assumes `testbed` and `eol_website` clones are siblings in the file system.
 * Clobber resource ids to match beta publishing site: <br/>
    `(cd ../eol_website; rails r ../testbed/clobber_resource_ids.rb)`

Example of command line access to neo4j:

    curl --user neo4j:neo4j \
         -H "Content-type: application/json" \
         -H "Accept: application/json; charset=UTF-8" \
         -d '{"statements" : [ {"statement" : "call dbms.showCurrentUser()"} ]}' \
         http://localhost:7474/db/data/transaction/commit

Learned the hard way: When starting and stopping neo4j, do *not* mix
use of `brew services start neo4j` (or `stop neo4j`, etc) with use of
the `neo4j` shell command e.g. `neo4j start`.  They do not play nicely
together.

