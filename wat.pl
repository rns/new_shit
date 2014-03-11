
node(while).
node(note).
node(todo).
node(idea).
node(assignment).
node(module).
node(bool).
node(number).
node(text).

#works_as(number, expression).
works_as(bool, expression).
works_as(expression, statement).
works_as(while, statement).
works_as(note, statement).
works_as(todo, statement).
works_as(idea, statement).
works_as(assignment, statment).
works_as(statement, all).
works_as(module, all).


works_ass(X, Y):-works_as(X, Y).
works_ass(X, Y):-
	works_as(X, Z),
	works_ass(Z, Y).

node_works_as(X, Y):-
	works_ass(X, Y),
	node(X).

/*
statement --> [if].
statement --> expression.
expression --> [bool].
expression --> [number].
expression --> [comparison].


if_syntax --> "if", [bool], "then", statement_syntax
comparison_syntax --> expression "==" expression

statement("if", [X, _])?
*/

