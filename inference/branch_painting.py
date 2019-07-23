
import sys, collections, csv, codecs, zipfile, argparse

def experiment(path):
  archive = zipfile.ZipFile(path, 'r')
  dh = load_dynamic_hierarchy(archive)
  children = get_children(dh)
  roots = find_roots(dh)
  print ("%7s roots" % len(roots))
  traits = load_traits(archive)    # Takes a long time
  page_traits = get_page_traits(traits)

  # TBD: load in the terms.csv file, in order to get term names

  # Count pages that have both traits and descendants
  count = 0
  for page_id in page_traits:
    if page_id in children:
      count += 1
      if count % 1000 == 0:
        page = dh[page_id]
        preds = [trait.predicate for trait in page_traits[page_id]]
        print ("%s %s %s" % (page.parent_id, page.canonical, preds[0]))
  print ("pages with both traits and children: %s" % count)

  # Count inferrable traits
  (asserted, inferred) = estimate_inferred_trait_count(dh, roots, children, page_traits)
  print ("asserted traits: %s" % asserted)
  print ("inferred traits: %s" % inferred)

  # Figure out which predicates are multivalued
  multivalued = {}
  for page in dh.values():
    pred_vals = {}
    for trait in page_traits.get(page.page_id, ()):
      pred = trait.predicate    # a string
      val = get_predicate_value(trait)
      if pred in pred_vals:
        if not val in pred_vals[pred]:
          pred_vals[pred].append(val)
      else:
        pred_vals[pred] = [val]
    for (pred, vals) in pred_vals.items():
      if len(vals) > 1:
        multivalued[pred] = page
  for (pred, page) in multivalued.items():
    print ("multivalued: %s %s" % (page.page_id, pred))

def get_predicate_value(trait):
  val = trait.normal_measurement
  if val == '':
    val = trait.literal
    if val == '':
      val = trait.value_uri
      if val == '':
        val = trait.object_page_id
        if val == '':
          val = trait.measurement
          if val == '':
            print ('** No value for trait %s with predicate %s' % (trait.eol_pk, trait.predicate))
  return val

def estimate_inferred_trait_count(dh, roots, children, page_traits):
  # incoming = number of traits on node's parent (both asserted and inferred)
  def descend(page, incoming):
    if page.page_id in page_traits:
      asserted = len(page_traits[page.page_id])
    else:
      asserted = 0
    inferred = incoming
    from_here = asserted + inferred
    for child in children.get(page.page_id, ()):
      (a, i) = descend(child, from_here)
      asserted += a
      inferred += i
    return (asserted, inferred)
  asserted = 0
  inferred = 0
  for root in roots:
    (a, i) = descend(root, 0)
    asserted += a
    inferred += i
  return (asserted, inferred)

# Output: list of Page
def find_roots(dh):
  roots = []
  for page in dh.values():
    if not page.parent_id in dh:
      roots.append(page)
  return roots

# Returns dict mapping from trait unique id to trait record
def load_traits(archive):
  csv_path = 'trait_bank/traits.csv'
  traits = {}
  with archive.open(csv_path, 'r') as raw_infile:
    infile = codecs.iterdecode(raw_infile, 'utf-8')
    r = csv.reader(infile)
    header = next(r)
    Trait = collections.namedtuple('Trait', header)

    # ['eol_pk', 'page_id', 'resource_pk', 'resource_id', 'source', 'scientific_name', 'predicate', 'object_page_id', 'value_uri', 'normal_measurement', 'normal_units_uri', 'normal_units', 'measurement', 'units_uri', 'units', 'literal']
    for row in r:
      nt = Trait._make(row)
      traits[nt.eol_pk] = nt
    print('%7s traits' % (len(traits)))
  return traits

# Input: dict mapping trait id to Trait
# Output: dict mapping page id to list of Trait
def get_page_traits(traits):
  page_traits = {}
  for trait in traits.values():
    page_id = trait.page_id
    if page_id in page_traits:
      page_traits[page_id].append(trait)
    else:
      page_traits[page_id] = [trait]
  print('%7s pages with traits' % (len(page_traits)))
  return page_traits

# Input: dict mapping page id to Page
# Output: dict mapping page id to list of Page (the page's children)
def get_children(dh):
  children = {}
  for page in dh.values():
    parent_id = page.parent_id
    if parent_id in children:
      children[parent_id].append(page)
    else:
      children[parent_id] = [page]
  print('%7s pages with children' % (len(children)))
  return children

def load_dynamic_hierarchy(archive):
  csv_path = 'trait_bank/pages.csv'
  dh = {}
  with archive.open(csv_path, 'r') as raw_infile:
    infile = codecs.iterdecode(raw_infile, 'utf-8')
    r = csv.reader(infile)
    header = next(r)
    Page = collections.namedtuple('Page', header)
    for row in r:
      nt = Page._make(row)
      dh[nt.page_id] = nt
    print('%7s pages' % (len(dh)))
  return dh

experiment(sys.argv[1])
