(* utility functions *)
open Utils326

(*Date for lateness deduction*)

(* "import" exceptions, in case they don't have them in their file*)
exception BadDivisors of int * int
let bad_divisors n m = raise (BadDivisors (n,m))
exception BadPi of int
let bad_pi (n:int) = raise (BadPi n)
exception BadArg of int
let bad_arg (n:int) = raise (BadArg n)

(* Keep track of tests passed and total number of tests. points is defined in Utils326 *)
let probs_right : points = (0, 0) (* (correct, total possible) *)
let total_points : points = (0, 0) (* (correct, total possible) *)

(* Give initial values for required functions and variables, so that if students 
    don't include them, they'll still be able to be referenced in the tests
   Also define a few of our implementations of required items *)
let prob1 : string = "Problem 1 unimplemented"

(* 
OCaml, by default, exports each file foo.ml as a module Foo
so this is just importing all the student's solutions
*)

open A1

(* every problem needs the first line of the following comment (T P #)
   above it, because when the grading script fails to compile a
   student's code, it greps for that comment so that the student can
   understand the context of what function/problem is not compiling,
   since the line number shown will be from this file, which the
   students don't have.  *)
              
(* Testing Problem 1 *)
let _ = print_header ( "Problem 1" )
let total = (0,0)

let total = tally total (assert326 ( prob1 = "Hello World!" ) 
                           "1 does not print correct message")
(* We've finished this problem, use the total kept by tally to determine overall result:
   problem passes iff all tests pass.
   probs_right is to the assignment what total is to the problem: a (right,total) points value *)
let _ = Printf.printf "%d / 4 points\n" (fst(total))
let probs_right = count_prob probs_right total
let total_points = total

(* the bottom of each assignment has a summary of how many problems 
   were correct among the number that had autograded tests *)
let _ = print_header ( "Summary" )

let _ = 
let (n,d) = probs_right in
Printf.printf "Problems Passed:\n";
Printf.printf "%d / %d\n" n d;
let (n,d) = total_points in
Printf.printf "Points Awarded:\n";
Printf.printf "Given: %d / %d\n" n d;
Printf.printf "Pending: _ / 9\n";
 let path = Sys.getcwd() in
 let uid = String.sub path ((String.rindex path '/')+1) ((String.length path) - (String.rindex path '/') - 1) in
print_late_days 1 d ["a1.ml"] uid
