sudo grep -RniE 'char[a-z0-9]*' / --exclude-dir={/proc,/sys,/dev,/run,/snap,/var/lib/docker,/var/lib/containers} 2>/dev/null
