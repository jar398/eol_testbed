# bin/rails r clobber_resource_ids.rb

# Run this once, after the resources list has been loaded from the
# content repository (`rake sync`), to adjust the id of each resource
# to match what's in some parallel publishing site, e.g. eol.org.

# For now you must get the resources.json file manually:
#   wget http://eol.org/resources.json?per_page=1000
# which creates a local files "resources.json?per_page=1000", whose
# name is wired into this script.

file = File.read "resources.json?per_page=1000"
data = JSON.parse(file)
seen = {}

count = 0
wins = 0
data["resources"].each { |resource|
  name = resource["name"]
  key = name
  STDERR.puts("Processing: #{key}") if (count % 50).zero?
  next unless resource["nodes_count"] == nil
  begin 
    record = Resource.find_by(name: name)
    if record
      id = resource["id"]
      if seen.key?(key)
        r2 = seen[key]
        a = [r2["id"], r2["name"], r2["nodes_count"]]
        b = [id, name, resource["nodes_count"]]
        STDERR.puts("Duplicate key: [#{a}] [#{b}]")
      else
        record.update_attribute(:id, id)
        wins += 1
        seen[key] = resource
      end
    else
      STDERR.puts("Not in db: #{key}")
    end
  rescue => e
    STDERR.puts("Exception: #{key} #{e}")
  end
  count += 1
}
STDERR.puts("Updated #{wins} out of #{count} resource records")
