# Testbed
JAR's place to play around with EOL v3

Here is the setup procedure that I used, very similar to what's in
[README.md](https://github.com/EOL/eol_website/blob/master/README.md).

 * Clone the [`eol_website`](https://github.com/EOL/eol_website) repository
 * Tweak secrets.yml:
      * Change `3000` to `2999`
      * Change `url: 'http://localhost:3000'` to `url: 'http://beta-repo.eol.org'`
 * Install and start neo4j
 * At shell: `export EOL_TRAITBANK_URL=http://neo4j:YOURNEWPASSWORD@localhost:7474`
 * Install and start mysql
 * Set up mysql 'eol' user and database
      1. `create database eol_development;`
      2. `create user 'eol'@'localhost' identified by 'eol';`
      3. `grant all privileges on eol_development.* to 'eol'@'localhost';`
      4. `flush privileges;`
 * Initialize database (not sure what this does, seems to create indexes)
      * `rails r "TraitBank::Admin.setup"`
 * Install and start rails (I think)
      * `rails s`
 * I don't know why this is needed but it is: (from Jeremy)
      * `rails r "ImportRun.delete_all"`
 * Get sources and terms:
      * `rake sync`  (this takes about 15 minutes)
 * Change harvesting site resource ids to avoid conflicts with publishing site resource ids (at mysql prompt):
      * `update resources set id = id + 1000;`
 * Get publishing site resources list.  Not sure where this
    file comes from; I got it from Jeremy.  Put it at `pub-site-resources.json` in `eol_testbed` directory (path is hardwired in upcoming script)
 * The following assumes `eol_testbed` and `eol_website` clones are siblings in the file system.
 * Clobber resource ids to match beta publishing site:
    `(cd ../eol_website; rails r ../eol_testbed/clobber_resource_ids.rb)`
