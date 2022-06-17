SOURCES=workload.py utils326.ml

OCAML_APK=ocaml-4.14.0-r0.apk
OCAMLBUILD_APK=ocamlbuild-0.14.1-r1.apk
OCAMLFIND_APK=ocaml-findlib-1.9.3-r0.apk
OCAMLRUNTIME_APK=ocaml-runtime-4.14.0-r0.apk

.PHONY: all
all: out

%.apk:
	wget https://dl-cdn.alpinelinux.org/alpine/v3.16/community/x86_64/$@

out/usr/bin/ocaml: ${OCAML_APK}
	mkdir -p out
	tar -C out -xzf $< 2> /dev/null

out/usr/lib/ocaml/stdlib.cma: ${OCAMLRUNTIME_APK}
	mkdir -p out
	tar -C out -xzf $< 2> /dev/null
	echo "/srv/usr/lib/ocaml" > out/usr/lib/ocaml/ld.conf
	echo "/srv/usr/lib/ocaml/stublibs" >> out/usr/lib/ocaml/ld.conf

out: ${SOURCES} out/usr/bin/ocaml out/usr/lib/ocaml/stdlib.cma
	mkdir -p out
	cp ${SOURCES} out
