SOURCES=workload.py
GO_VERSION=1.17.10-r0


.PHONY: all
all: out

go-$(GO_VERSION).apk:
	wget https://dl-cdn.alpinelinux.org/alpine/v3.15/community/x86_64/go-$(GO_VERSION).apk

out/usr/lib/go/bin/go: go-$(GO_VERSION).apk
	mkdir -p out
	tar -C out -xzf go-$(GO_VERSION).apk usr/lib 2> /dev/null

out: ${SOURCES} out/usr/lib/go/bin/go
	mkdir -p out
	cp ${SOURCES} out
