Tools for deduplicating WARC files. Largely based on the tools
built by the [Bibliotheca Alexandrina](https://github.com/arcalex) for this
purpose, but modified for easier (or correct) use. See
[Youssef
Eldakar's](http://netpreserve.org/sites/default/files/attachments/2015_IIPC-GA_Slides_16b_Eldakar.pdf)
description of the tools for a little more information.

## Fixes/Changes

`warcsum` mostly worked correctly, but used `int`s in a number of places where
they are inappropriate, mainly when dealing with file offsets. If you never use
a WARC larger than 2GB, there's no problem. My changes are just hacks to make it
work; it needs some cleanup.

`warccollres` has been reimplemented completely, since the arcalex
implementation seems to assume existing archive infrastructure so it can simply
make HTTP requests for WARC members, finding the URLs from a mysql database. I
don't have any of that, so my version (`warccollres.py`) uses a sqlite database
and reads WARC files directly.

`warcrefs` suffered from the same problem as `warcsum` where it used 32-bit file
offsets. I've probably fixed that, but haven't tested and it might be horrible.

The `warc` package for Python was designed with Python 2 in mind, so I had to
hack it to work on Python 3. Might be better to replace with `warcat`, but that
has its own issues (regarding extremely slow reading mostly).

## Use

First build everything:

```
$ cd gzmulti
$ ./configure && make
$ sudo make install
$ cd ../warcsum
$ ./configure && make
$ sudo make install
$ cd ../warcrefs
$ mvn package
```

You may need to add the library install directory to your load path so warcsum
and friends can find gzmulti:

    export LD_LIBRARY_PATH=/usr/local/lib

Now you can dedup. If you want to combine smaller WARCs into a big one, try
`megawarc`.

First generate hash digests of your input file's contents. We'll assume the
input is `mega.warc.gz`

    warcsum -i mega.warc.gz -o mega.warcsum

Then run `warccollres` to determine which hash collisions are identical records,
and which are not. This can take a while.

    python3 warccollres.py mega.warcsum

It will import the digest file into a database, then go to work finding
duplicates. If interrupted while finding duplicates, you can resume where it
left off by running `warccollres.py` without any arguments.

When finished, it will write the manifest back out with duplicate pointers to
`warccollres.txt`.  Then we run `warcrefs` to rewrite the WARC.

    java -jar warcrefs/target/warcrefs-1.0-SNAPSHOT-jar-with-dependencies.jar \
        8129 warccollres.txt `pwd`

..and hopefully that's it.

---

For performance reasons `warccollres` uses
[`mysqlclient`](https://github.com/PyMySQL/mysqlclient-python), which implies
you need a database server for it. Configure connection information in
`MYSQL_PARAMS`. You'll want to ensure the database server is configured for
reasonable performance. In particular, ensure `innodb_buffer_pool_size` is
large. Ideally, at least as large as your dataset so it can all live in RAM.

The code will automatically create indexes after importing data, but somebody
more skilled with SQL than I am might be able to improve that.

You can use sqlite too, but the queries in the code will need rewriting since
the dialects used are incompatible and it tends to be painfully slow when
writing.
