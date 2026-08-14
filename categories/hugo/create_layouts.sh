#!/bin/bash
# Create layout folders
mkdir -p layouts/_default layouts/taxonomy

# Create homepage template
cat << 'EOF' > layouts/index.html
{{ define "main" }}
<h1>Welcome to my homepage</h1>
{{ end }}
EOF

# Create list template
cat << 'EOF' > layouts/_default/list.html
{{ define "main" }}
{{ range .Pages }}
  <h2><a href="{{ .Permalink }}">{{ .Title }}</a></h2>
{{ end }}
{{ end }}
EOF

# Create taxonomy tag layout
cat << 'EOF' > layouts/taxonomy/tag.html
{{ define "main" }}
<h1>Tags</h1>
<ul>
  {{ range .Data.Terms }}
    <li><a href="{{ .Page.Permalink }}">{{ .Page.Title }}</a></li>
  {{ end }}
</ul>
{{ end }}
EOF

# Create taxonomy terms layout
cat << 'EOF' > layouts/_default/terms.html
{{ define "main" }}
<h1>All Taxonomies</h1>
{{ range .Data.Terms }}
  <h2><a href="{{ .Page.Permalink }}">{{ .Page.Title }}</a></h2>
{{ end }}
{{ end }}
EOF

