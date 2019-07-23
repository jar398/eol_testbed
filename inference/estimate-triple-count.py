

# Open zip file
# Open each .csv file
# for each row
#  for each cell after the first
#   if cell is nonempty, increment counter

import sys, csv, codecs, zipfile, argparse

def estimate_triple_count(path):
    archive = zipfile.ZipFile(path, 'r')
    zip_triples = 0
    for name in ['traits', 'metadata', 'pages', 'terms']:
        csv_path = 'trait_bank/%s.csv' % (name,)
        with archive.open(csv_path, 'r') as raw_infile:
            infile = codecs.iterdecode(raw_infile, 'utf-8')
            rows = 0
            triples = 0
            r = csv.reader(infile)
            for row in r:
                rows += 1
                for cell in row[1:]:
                    if len(cell) > 0:
                        triples += 1
            print('%25s: %7s rows, %8s triples' % (csv_path, rows, triples,))
        zip_triples += triples
    print('%s triples' % (zip_triples,))

estimate_triple_count(sys.argv[1])
