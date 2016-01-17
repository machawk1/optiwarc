Tools for deduplicating WARC files. Largely based on the tools
built by the [Bibliotheca Alexandrina](https://github.com/arcalex) for this
purpose, but modified for easier (or correct) use.

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
