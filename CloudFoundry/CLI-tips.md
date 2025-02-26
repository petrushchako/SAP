# CLI TIPS
List of useful CLI commands


- CF apps instance count retrieval:
    `cf apps | tail +4 | awk '$3 !~ /^web:.*\/1.*/ {printf "%-80s %s\n", $1,$3}'`

- 
