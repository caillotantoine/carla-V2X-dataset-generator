find . -name "*.xz" | parallel -I% --max-args 1 xz -d %
