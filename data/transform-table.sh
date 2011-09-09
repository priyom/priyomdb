#!/bin/bash
sed -r "/<tr>/{N;N;N;N;s/<tr>\n<td>([A-Z][a-z]{2})[a-z]+ ([0-9]+), ([0-9]{4})<\/td>\\n<td>([0-9]{1,2}:[0-9]{2})<\/td>\\n<td>([0-9? ]{6})(( [^ ]+( [0-9?]{2}){4})+)<\/td>\n<\/tr>/transmission time \3 \1 \2 \4 data \5\6/;t end;d;: end}" | sed -r "/transmission/b;d"
