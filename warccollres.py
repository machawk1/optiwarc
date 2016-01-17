import gzip, io, sqlite3, sys, warc
# Read a warcsums file (generated by `warcsums`, predictably) from stdin
# and write a postprocessed hash manifest (like `warcsumproc`) indicating
# where true duplicate responses can be found. This can be fed in to
# `warcrefs` to actually deduplicate the WARC.
#
# See:
# http://netpreserve.org/sites/default/files/attachments/2015_IIPC-GA_Slides_16b_Eldakar.pdf

# Output should be sorted by WARC name then WARC offset
# backrefs must only refer to earlier records, so process in order of offset
# copy_number starts from 1

def create_tables(connection):
    c = connection.cursor()
    c.execute('CREATE TABLE warcsums ' +
              '(id INTEGER PRIMARY KEY AUTOINCREMENT,' +
              ' warc_filename BLOB NOT NULL,' +
              ' warc_offset INTEGER NOT NULL,' +
              ' warc_len INTEGER NOT NULL,' +
              ' uri BLOB NOT NULL,' +
              ' datetime BLOB NOT NULL,' +
              ' digest BLOB NOT NULL,' +
              ' copy_number INTEGER DEFAULT NULL,' +
              ' ref_uri BLOB DEFAULT NULL,' +
              ' ref_date BLOB DEFAULT NULL)')
    connection.commit()

def import_warcsums(f, connection):
    cursor = connection.cursor()
    n_imports = 0
    for line in f:
        (warc_filename, warc_offset, warc_len, uri, datetime, digest) = line.split()
        cursor.execute('INSERT INTO warcsums ' +
                       '(warc_filename, warc_offset, warc_len,' +
                       ' uri, datetime, digest) ' +
                       'VALUES (?, ?, ?, ?, ?, ?)',
                       (warc_filename, warc_offset, warc_len,
                       uri, datetime, digest))
        n_imports += 1
    connection.commit()

    # Assert that all records are part of the same WARC file
    c = connection.cursor()
    c.execute('SELECT COUNT(DISTINCT warc_filename) FROM warcsums')
    count = c.fetchone()
    assert count is not None and count[0] == 1, "Must refer to only one file"
    return n_imports


def find_possible_collision(connection):
    c = connection.cursor()
    c.execute('SELECT id, warc_filename, digest, warc_offset, warc_len, uri, datetime ' +
              'FROM warcsums WHERE copy_number IS NULL ' +
              'ORDER BY warc_offset LIMIT 1')
    result = c.fetchone()
    if result is None:
        return None
    rowid = result[0]

    c.execute('UPDATE warcsums SET copy_number = 1 WHERE id = ?',
              (rowid,))
    connection.commit()
    print('Considering row', rowid)
    return result[1:]


def read_warc_contents(filename, offset, length):
    # TODO
    f = open(filename, 'rb')
    f.seek(offset)
    decompressed = gzip.open(io.BytesIO(f.read(length))).read()
    reader = warc.WARCReader(io.BytesIO(decompressed))
    record = reader.read_record()
    out = record.payload.read()
    # Strip HTTP headers (we're only interested in the body; headers are always
    # preserved since the WARCing process inserts Date headers).
    body_idx = out.find(b'\r\n\r\n') + 4
    return out[body_idx:]

def dedup_collisions(connection, warc_filename, digest, warc_offset, warc_len, uri, datetime):
    """
    Given a record from WARC file warc_filename with hash `digest` and actual
    contents `contents`, find all records in the database with the same digest
    and contents that are in the same WARC.

    Sets the copy number and ref fields on processed records.
    """
    # TODO check if there are dupes to handle before extracting
    # Extract the candidate file
    contents = read_warc_contents(warc_filename, warc_offset, warc_len)

    dup_count = 1

    cursor = connection.cursor()
    cursor.execute('SELECT id, warc_offset, warc_len ' +
                   'FROM warcsums WHERE digest = ? AND copy_number IS NULL ' +
                   'ORDER BY warc_offset', (digest,))

    for (rowid, warc_offset, warc_len) in cursor:
        test_contents = read_warc_contents(warc_filename, warc_offset, warc_len)

        if test_contents == contents:
            # True match
            dup_count += 1
            c2 = connection.cursor()
            c2.execute('UPDATE warcsums SET ' +
                       'copy_number = ?, ' +
                       'ref_uri = ?, ' +
                       'ref_date = ? ' +
                       'WHERE id = ?',
                       (dup_count, uri, datetime, rowid))
            print('Row', rowid, 'is copy', dup_count, 'of', uri)
    # Nothing else to do; just commit
    connection.commit()

if __name__ == '__main__':
    connection = sqlite3.connect('collres.db')

    create_tables(connection)
    print('Imported', import_warcsums(sys.stdin, connection), 'records')

    while True:
        params = find_possible_collision(connection)
        if params is None:
            break
        dedup_collisions(connection, *params)
