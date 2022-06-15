SOURCES=workload.py

OCAML_APK=ocaml-4.14.0-r0.apk

.PHONY: all
all: out

${OCAML_APK}:
	wget https://dl-cdn.alpinelinux.org/alpine/v3.16/community/x86_64/$@

out/usr: ${OCAML_APK}
	mkdir -p out
	tar -C out -xzf $< 2> /dev/null

out: ${SOURCES} out/usr
	mkdir -p out
	cp ${SOURCES} out
