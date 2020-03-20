# rails r ad_hoc_id_script.rb

# Run this once, after the resources list has been loaded from the
# repository (`rake sync`), to adjust the id of each resource
# so that it matches what's found in file pub-site-resources.json
# (which is somehow extracted from the publishing server).

# Get resources.json file with: wget http://content.eol.org/resources.json

file = File.read "resources.json"
data = JSON.parse(file)

count = 0
wins = 0
data.each { |resource|
  id = resource["id"]
  STDERR.puts("Touching #{resource["name"]}") if (count % 25).zero?
  begin 
    Resource.find_by_name(resource["name"]).update_attribute(:id, resource["id"])
    wins += 1
  rescue
    STDERR.puts("Skipping #{resource["name"]}")
  end
  count += 1
}
STDERR.puts("Updated #{wins} out of #{count} resource records")
