Provide local network services for LLM

docker run -d --name searxng -p 8888:8080 \
 -v $(pwd)/searxng-settings.yml:/etc/searxng/settings.yml \
 searxng/searxng
