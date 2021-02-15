find . -name "*.ply" | parallel -I% --max-args 1 xz %
find . -name "*.png" | parallel -I% --max-args 1 xz %
find . -name "*.json" | parallel -I% --max-args 1 xz %
