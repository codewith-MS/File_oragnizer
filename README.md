# File_oragnizer

#organizing the file

#logging : It loads a built-in Python tool that lets us record messages instead of using print()
So we can save useful information (time, file name, errors) into a log file and use it later when something breaks.
as python cannot remember where was the file location after it was moved to another destination.

#dry run : before moving the file it show what will happen after the file are move from one destination to another

Hash-based duplicate detection : Before moving each file, we compute a SHA-256 hash of its contents and check whether a file with the same hash already exists in the destination category folder. If so:
        By default we skip moving (to avoid duplicate content),and we log the skip + record it into a duplicates.txt file (so you know which files were duplicates).we can change                 behavior to instead rename the file or keep both — I’ll show where to change that.

### What I added (exact new pieces) and why

import hashlib, import json

  > Why: we need SHA-256 hashing (content checks) and a small JSON index to persist seen hashes across runs.

HASH_INDEX_FILE = "hash_index.json" and functions load_hash_index, save_hash_index

  > Why: so the script remembers already-seen content between runs. Without persistence you'll re-detect duplicates every run only during that run.

file_hash(path) function

  > Why: compute SHA-256 safely in chunks so even large files are hashed.

hash_index usage and checks:

  > if h in hash_index.get(category, {}): → skip duplicates

  >Why: real duplicate detection must check content, not filename.

duplicates_skipped counter and report entries

  > Why: you asked to know which files weren't moved; now duplicates are tracked separately.

Recording hash after successful move:

  > hash_index[category][h] = rel_ref

  > Why: future runs can find duplicates quickly.

Save the hash_index.json when DRY_RUN is False (i.e., on real moves).

  > Why: don't pollute persistent state in a dry run; only record when operations actually happened.

Minor logic: not_moved_files now subtracts duplicates_skipped too.

  > Why: accurate accounting.
> 

## To make it look neat in output format we use 
> Halo and spinner for animation

------------------------------------------------------
#### Output 

<img width="600" height="285" alt="image" src="https://github.com/user-attachments/assets/3e1fb3f4-a3ca-40b3-8612-a8aeb3401174" />



















