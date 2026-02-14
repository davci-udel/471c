from collections.abc import Mapping
from functools import partial

from .syntax import (
    Abstract,
    Allocate,
    Apply,
    Begin,
    Branch,
    Identifier,
    Immediate,
    Let,
    LetRec,
    Load,
    Primitive,
    Reference,
    Store,
    Term,
    Program,
)

type Context = Mapping[Identifier, None]


def check_term(
    term: Term,
    context: Context,
) -> None:
    recur = partial(check_term, context=context)  # noqa: F841

    match term:
        case Let(bindings=bindings, body=body):
            identifiers = [identifier for identifier, _ in bindings]
            duplicates = len(set(identifiers)) < len(identifiers)
            if duplicates:
                raise ValueError("Duplicate identifiers")

            for _, term in bindings:
                recur(term)
            binding_identifiers = {identifier: None for (identifier, _) in bindings}
            recur(body, context={**context, **binding_identifiers})

        case LetRec(bindings=bindings, body=body):
            identifiers = [identifier for identifier, _ in bindings]
            duplicates = len(set(identifiers)) < len(identifiers)
            if duplicates:
                raise ValueError("Duplicate identifiers")
            binding_identifiers = {identifier: None for (identifier, _) in bindings}
            for _, term in bindings:
                recur(term, context={**context, **binding_identifiers})
            recur(body, context={**context, **binding_identifiers})

        case Reference(name=name):
            if name not in context:
                raise ValueError()

        case Abstract(parameters=parameters, body=body):
            duplicates = len(set(parameters)) < len(parameters)
            if duplicates:
                raise ValueError("Duplicate identifiers")
            local = {parameter: None for parameter in parameters}
            recur(body, context={**context, **local})

        case Apply(target=target, arguments=arguments):
            recur(target)
            for argument in arguments:
                recur(argument)

        case Immediate(value=value):
            pass

        case Primitive(operator=_operator, left=left, right=right):
            recur(left)
            recur(right)

        case Branch(operator=_operator, left=left, right=right, consequent=consequent, otherwise=otherwise):
            recur(left)
            recur(right)
            recur(consequent)
            recur(otherwise)

        case Allocate():
            pass

        case Load(base=base):
            recur(base)

        case Store(base=base, value=value):
            recur(base)
            recur(value)

        case Begin(effects=effects, value=value):  # pragma: no branch
            for effect in effects:
                recur(effect)
            recur(value)


def check_program(
    program: Program,
) -> None:
    match program:
        case Program(parameters=parameters, body=body):  # pragma: no branch
            duplicates = len(set(parameters)) < len(parameters)
            if duplicates:
                raise ValueError("Duplicate identifiers")
            local = dict.fromkeys(parameters, None)
            check_term(body, context=local)
