UTILS = str.cma unix.cma utils326.ml

.PHONY: all grader
all: grader

grader:
	ocamlc -noassert -I $(SUBMISSION_DIR) $(SUBMISSION_DIR)/a1.ml $(UTILS) $(SUBMISSION_DIR)/grade.ml
