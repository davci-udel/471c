from collections.abc import Callable
from functools import partial

from L0 import syntax as L0
from util.sequential_name_generator import SequentialNameGenerator

from L1 import syntax as L1


def get_free(statement: L1.Statement, in_use: set[L1.Identifier]) -> dict[L1.Identifier, None]:
    match statement:
        case L1.Abstract(destination=destination, parameters=parameters, body=body, then=then):
            return get_free(statement=body, in_use=in_use | set([*parameters, *[destination]])) | get_free(
                statement=then, in_use=in_use | set([destination])
            )
        case L1.Apply(target=target, arguments=arguments):
            return {a: None for a in [*arguments, *[target]] if a not in in_use}
        case L1.Copy(destination=destination, source=source, then=then):
            so: dict[L1.Identifier, None] = {} if source in in_use else {source: None}
            return so | get_free(statement=then, in_use=in_use | set([destination]))
        case L1.Immediate(destination=destination, value=value, then=then):
            return get_free(statement=then, in_use=in_use | set([destination]))
        case L1.Primitive(destination=destination, operator=_, left=left, right=right, then=then):
            le: dict[L1.Identifier, None] = {} if left in in_use else {left: None}
            ri: dict[L1.Identifier, None] = {} if right in in_use else {right: None}
            return le | ri | get_free(statement=then, in_use=in_use | set([destination]))
        case L1.Branch(operator=_, left=left, right=right, then=then, otherwise=otherwise):
            le: dict[L1.Identifier, None] = {} if left in in_use else {left: None}
            ri: dict[L1.Identifier, None] = {} if right in in_use else {right: None}
            return le | ri | get_free(statement=then, in_use=in_use) | get_free(statement=otherwise, in_use=in_use)
        case L1.Allocate(destination=destination, count=_, then=then):
            return get_free(statement=then, in_use=in_use | set([destination]))
        case L1.Load(destination=destination, base=base, index=_, then=then):
            ba: dict[L1.Identifier, None] = {} if base in in_use else {base: None}
            return ba | get_free(statement=then, in_use=in_use | set([destination]))
        case L1.Store(base=base, index=_, value=value, then=then):
            ba: dict[L1.Identifier, None] = {} if base in in_use else {base: None}
            va: dict[L1.Identifier, None] = {} if value in in_use else {value: None}
            return ba | va | get_free(statement=then, in_use=in_use)
        case L1.Halt(value=value):
            return {} if value in in_use else {value: None}
        case _:  # pragma: no cover
            return


def close_statement(
    statement: L1.Statement,
    procedures: list[L0.Procedure],
    fresh: Callable[[str], str],
) -> L0.Statement:
    _close_statement = partial(close_statement, procedures=procedures, fresh=fresh)
    match statement:
        case L1.Abstract(destination=destination, parameters=parameters, body=body, then=then):
            code = fresh("abstract_code")
            env = fresh("abstract_env")
            heap = fresh("abstract_heap")
            body_closed = _close_statement(body)
            body_free_dict = get_free(statement=body, in_use=set([*[destination], *parameters]))
            for i, free in enumerate(body_free_dict):
                body_closed = L0.Load(destination=free, base=env, index=i + 1, then=body_closed)

            body_closed = L0.Copy(destination=destination, source=env, then=body_closed)
            procedures.append(L0.Procedure(name=code, parameters=[*[env], *parameters], body=body_closed))

            then_ = _close_statement(then)
            for i, free in enumerate(body_free_dict):
                then_ = L0.Store(base=destination, index=i + 1, value=free, then=then_)
            return L0.Allocate(
                destination=destination,
                count=len(body_free_dict.keys()) + 1,
                then=L0.Address(
                    destination=heap, name=code, then=L0.Store(base=destination, index=0, value=heap, then=then_)
                ),
            )
        case L1.Apply(target=target, arguments=arguments):
            code = fresh("apply_code")
            return L0.Load(
                destination=code, base=target, index=0, then=L0.Call(target=code, arguments=[*[target], *arguments])
            )
        case L1.Copy(destination=destination, source=source, then=then):
            return L0.Copy(destination=destination, source=source, then=_close_statement(then))
        case L1.Immediate(destination=destination, value=value, then=then):
            return L0.Immediate(destination=destination, value=value, then=_close_statement(then))
        case L1.Primitive(destination=destination, operator=operator, left=left, right=right, then=then):
            return L0.Primitive(
                destination=destination, operator=operator, left=left, right=right, then=_close_statement(then)
            )
        case L1.Branch(operator=operator, left=left, right=right, then=then, otherwise=otherwise):
            return L0.Branch(
                operator=operator,
                left=left,
                right=right,
                then=_close_statement(then),
                otherwise=_close_statement(otherwise),
            )
        case L1.Allocate(destination=destination, count=count, then=then):
            return L0.Allocate(destination=destination, count=count, then=_close_statement(then))
        case L1.Load(destination=destination, base=base, index=index, then=then):
            return L0.Load(destination=destination, base=base, index=index, then=_close_statement(then))
        case L1.Store(base=base, index=index, value=value, then=then):
            return L0.Store(base=base, index=index, value=value, then=_close_statement(then))
        case L1.Halt(value=value):
            return L0.Halt(value=value)
        case _:  # pragma: no cover
            return


def close_program(
    program: L1.Program,
) -> L0.Program:
    match program:
        case L1.Program(parameters=parameters, body=body):
            procedures: list[L0.Procedure] = []
            procedures.append(
                L0.Procedure(
                    name="main",
                    parameters=parameters,
                    body=close_statement(statement=body, procedures=procedures, fresh=SequentialNameGenerator()),
                )
            )
            return L0.Program(procedures=procedures)
        case _:  # pragma: no cover
            return
