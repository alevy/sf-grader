package example_grader

import (
	"testing"
	"example.com/example"
)

func TestNegate(t *testing.T) {
	if example.Negate(true) {
		t.Errorf("Expected false, was true")
	}
}
