FUNCTIONS=start_assignment gh_repo go_grader grades generate_report
OUTPUTS=$(patsubst %, output/%.img, $(FUNCTIONS))
RUNS=$(patsubst %, run/%, $(FUNCTIONS))

.PHONY: all
all: $(OUTPUTS) #$(RUNS)

output/%.img: functions/%/*
	@truncate -s 500M $@
	@mkfs.ext4 -F $@
	@ \
		if [ -f functions/$*/Makefile ]; then \
			make -C functions/$*; \
			cptofs -t ext4 -i $@ functions/$*/out/* /; \
		else \
			cptofs -t ext4 -i $@ functions/$*/* /; \
		fi
	@e2fsck -f $@
	@resize2fs -M $@

output/example_grader.tgz: example_grader/*
	tar -C example_grader -czf $@ .

output/example_submission.tgz: example_submission/*
	tar -czf $@ example_submission/

.PHONY: prepdb
prepdb: output/example_grader.tgz output/example_submission.tgz
	sfdb -b cos316/example/grading_script - < output/example_grader.tgz
	sfdb -b submission.tgz - < output/example_submission.tgz

.PHONY: prepfs
prepfs: output/example_grader.tgz output/example_submission.tgz example_grader/grader_config.json
	sffs mkdir /gh_repo	--endorse false --secrecy true --integrity gh_repo
	sffs mkdir /go_grader --endorse false --secrecy true --integrity go_grader
	sffs mkdir /grades --endorse false --secrecy true --integrity grades
	sffs mkdir /gh_repo/user --endorse false --secrecy user --integrity gh_repo
	sffs mkdir /go_grader/user --endorse false --secrecy user --integrity go_grader
	sffs mkdir /grades/user --endorse false --secrecy user --integrity grades
	# write /gh_repo/user/submission.tgz
	sffs mkfile /gh_repo/user/submission.tgz --endorse gh_repo --secrecy user --integrity gh_repo
	sffs write /gh_repo/user/submission.tgz --endorse gh_repo --file output/example_submission.tgz
	# write /cos316/example/grading_script & /cos316/example/grader_config.json
	sffs mkdir /cos316 --endorse false --secrecy true --integrity cos316
	sffs mkdir /cos316/example --endorse cos316 --secrecy true --integrity cos316
	sffs mkfile /cos316/example/grading_script --endorse cos316 --secrecy cos316,go_grader --integrity cos316
	sffs write /cos316/example/grading_script --endorse cos316 --file output/example_grader.tgz
	sffs mkfile /cos316/example/grader_config.json --endorse cos316 --secrecy true --integrity cos316
	sffs write /cos316/example/grader_config.json --endorse cos316 --file example_grader/grader_config.json


run/%: output/%.img payloads/%.jsonl python3.ext4
	@singlevm --mem_size 1024 --kernel vmlinux-4.20.0 --rootfs python3.ext4 --appfs output/$*.img --function $* < payloads/$*.jsonl
	@touch $@

.PHONY: debug/%
debug/%: export RUST_LOG=debug
debug/%: output/%.img payloads/%.jsonl python3.ext4
	@singlevm --mem_size 1024 --kernel vmlinux-4.20.0 --rootfs python3.ext4 --appfs output/$*.img --function $* --kernel_args "console=ttyS0" < payloads/$*.jsonl

.PHONY: clean
clean:
	rm -f $(OUTPUTS) $(RUNS) storage/*.mdb
