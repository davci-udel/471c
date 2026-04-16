from L0 import syntax as L0
from L1.close import SequentialNameGenerator, close_program, close_statement
from L1.syntax import Abstract, Allocate, Apply, Branch, Copy, Halt, Immediate, Load, Primitive, Program, Store


def proc(n: L0.Identifier, ps: L0.Sequence[L0.Identifier], b: L0.Statement):
    return L0.Procedure(name=n, parameters=ps, body=b)


def h(v: L0.Identifier):
    return L0.Halt(value=v)


def test_close_program():
    program = Program(
        parameters=["par1", "par2"],
        body=Halt(value="h"),
    )
    l0_actual = close_program(program=program)
    l0_expected = L0.Program(procedures=[proc("main", ["par1", "par2"], h("h"))])
    assert l0_actual == l0_expected

    program = Program(
        parameters=["x"],
        body=Abstract(
            destination="d",
            parameters=["y"],
            body=Halt(value="y"),
            then=Apply(target="d", arguments=["x"]),
        ),
    )
    l0_actual = close_program(program=program)
    l0_expected = L0.Program(
        procedures=[
            proc(
                "abstract_code0", ["abstract_env0", "y"], L0.Copy(destination="d", source="abstract_env0", then=h("y"))
            ),
            proc(
                "main",
                ["x"],
                L0.Allocate(
                    destination="d",
                    count=1,
                    then=L0.Address(
                        destination="abstract_heap0",
                        name="abstract_code0",
                        then=L0.Store(
                            base="d",
                            index=0,
                            value="abstract_heap0",
                            then=L0.Load(
                                destination="apply_code0",
                                base="d",
                                index=0,
                                then=L0.Call(target="apply_code0", arguments=["d", "x"]),
                            ),
                        ),
                    ),
                ),
            ),
        ]
    )
    assert l0_actual == l0_expected

    program = Program(
        parameters=["par1", "par2"],
        body=Abstract(
            destination="d1",
            parameters=["x1"],
            body=Abstract(
                destination="d2",
                parameters=["x2"],
                body=Halt(value="x1"),
                then=Apply(target="d2", arguments=["x1"]),
            ),
            then=Halt(value="d1"),
        ),
    )
    l0_actual = close_program(program=program)
    l0_expected = L0.Program(
        procedures=[
            proc(
                "abstract_code1",
                ["abstract_env1", "x2"],
                L0.Copy(
                    destination="d2",
                    source="abstract_env1",
                    then=L0.Load(destination="x1", base="abstract_env1", index=1, then=h("x1")),
                ),
            ),
            proc(
                "abstract_code0",
                ["abstract_env0", "x1"],
                L0.Copy(
                    destination="d1",
                    source="abstract_env0",
                    then=L0.Allocate(
                        destination="d2",
                        count=2,
                        then=L0.Address(
                            destination="abstract_heap1",
                            name="abstract_code1",
                            then=L0.Store(
                                base="d2",
                                index=0,
                                value="abstract_heap1",
                                then=L0.Store(
                                    base="d2",
                                    index=1,
                                    value="x1",
                                    then=L0.Load(
                                        destination="apply_code0",
                                        base="d2",
                                        index=0,
                                        then=L0.Call(target="apply_code0", arguments=["d2", "x1"]),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            proc(
                "main",
                ["par1", "par2"],
                L0.Allocate(
                    destination="d1",
                    count=1,
                    then=L0.Address(
                        destination="abstract_heap0",
                        name="abstract_code0",
                        then=L0.Store(base="d1", index=0, value="abstract_heap0", then=h("d1")),
                    ),
                ),
            ),
        ]
    )
    assert l0_actual == l0_expected

    program = Program(
        parameters=[],
        body=Abstract(
            destination="d",
            parameters=["x"],
            body=Copy(
                destination="d2",
                source="s",
                then=Immediate(
                    destination="d3",
                    value=0,
                    then=Primitive(
                        destination="d4",
                        operator="+",
                        left="d2",
                        right="s2",
                        then=Allocate(
                            destination="d5",
                            count=2,
                            then=Load(destination="d6", base="s3", index=0, then=Halt(value="d5")),
                        ),
                    ),
                ),
            ),
            then=Halt(value="d"),
        ),
    )
    l0_actual = close_program(program=program)
    l0_expected = L0.Program(
        procedures=[
            proc(
                "abstract_code0",
                ["abstract_env0", "x"],
                L0.Copy(
                    destination="d",
                    source="abstract_env0",
                    then=L0.Load(
                        destination="s3",
                        base="abstract_env0",
                        index=3,
                        then=L0.Load(
                            destination="s2",
                            base="abstract_env0",
                            index=2,
                            then=L0.Load(
                                destination="s",
                                base="abstract_env0",
                                index=1,
                                then=L0.Copy(
                                    destination="d2",
                                    source="s",
                                    then=L0.Immediate(
                                        destination="d3",
                                        value=0,
                                        then=L0.Primitive(
                                            destination="d4",
                                            operator="+",
                                            left="d2",
                                            right="s2",
                                            then=L0.Allocate(
                                                destination="d5",
                                                count=2,
                                                then=L0.Load(
                                                    destination="d6",
                                                    base="s3",
                                                    index=0,
                                                    then=h("d5"),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            proc(
                "main",
                [],
                L0.Allocate(
                    destination="d",
                    count=4,
                    then=L0.Address(
                        destination="abstract_heap0",
                        name="abstract_code0",
                        then=L0.Store(
                            base="d",
                            index=0,
                            value="abstract_heap0",
                            then=L0.Store(
                                base="d",
                                index=3,
                                value="s3",
                                then=L0.Store(
                                    base="d",
                                    index=2,
                                    value="s2",
                                    then=L0.Store(base="d", index=1, value="s", then=h("d")),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ]
    )
    assert l0_actual == l0_expected


def test_close_statement():
    statement = Abstract(
        destination="d",
        parameters=["x"],
        body=Halt(value="x"),
        then=Halt(value="d"),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="d",
        count=1,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(base="d", index=0, value="abstract_heap0", then=h("d")),
        ),
    )
    expected_procedures = [
        proc("abstract_code0", ["abstract_env0", "x"], L0.Copy(destination="d", source="abstract_env0", then=h("x")))
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Abstract(
        destination="d",
        parameters=["x"],
        body=Halt(value="y"),
        then=Apply(target="d", arguments=["x"]),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="d",
        count=2,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(
                base="d",
                index=0,
                value="abstract_heap0",
                then=L0.Store(
                    base="d",
                    index=1,
                    value="y",
                    then=L0.Load(
                        destination="apply_code0",
                        base="d",
                        index=0,
                        then=L0.Call(target="apply_code0", arguments=["d", "x"]),
                    ),
                ),
            ),
        ),
    )
    expected_procedures = [
        proc(
            "abstract_code0",
            ["abstract_env0", "x"],
            L0.Copy(
                destination="d",
                source="abstract_env0",
                then=L0.Load(destination="y", base="abstract_env0", index=1, then=h("y")),
            ),
        )
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Load(destination="d", base="b", index=0, then=Halt(value="h"))
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Load(destination="d", base="b", index=0, then=h("h"))
    expected_procedures = []
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Abstract(
        destination="j0",
        parameters=["t0"],
        body=Halt(value="t0"),
        then=Branch(
            operator="==",
            left="x",
            right="y",
            then=Apply(
                target="j0",
                arguments=["a"],
            ),
            otherwise=Apply(
                target="j0",
                arguments=["b"],
            ),
        ),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="j0",
        count=1,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(
                base="j0",
                index=0,
                value="abstract_heap0",
                then=L0.Branch(
                    operator="==",
                    left="x",
                    right="y",
                    then=L0.Load(
                        destination="apply_code0",
                        base="j0",
                        index=0,
                        then=L0.Call(target="apply_code0", arguments=["j0", "a"]),
                    ),
                    otherwise=L0.Load(
                        destination="apply_code1",
                        base="j0",
                        index=0,
                        then=L0.Call(target="apply_code1", arguments=["j0", "b"]),
                    ),
                ),
            ),
        ),
    )
    expected_procedures = [
        proc(
            "abstract_code0",
            ["abstract_env0", "t0"],
            L0.Copy(
                destination="j0",
                source="abstract_env0",
                then=h("t0"),
            ),
        )
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Abstract(
        destination="t0",
        parameters=["x", "k0"],
        body=Apply(target="k0", arguments=["x"]),
        then=Halt(value="t0"),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="t0",
        count=1,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(base="t0", index=0, value="abstract_heap0", then=h("t0")),
        ),
    )
    expected_procedures = [
        proc(
            "abstract_code0",
            ["abstract_env0", "x", "k0"],
            L0.Copy(
                destination="t0",
                source="abstract_env0",
                then=L0.Load(
                    destination="apply_code0",
                    base="k0",
                    index=0,
                    then=L0.Call(target="apply_code0", arguments=["k0", "x"]),
                ),
            ),
        )
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Abstract(
        destination="d",
        parameters=["x"],
        body=Branch(
            operator="==",
            left="a",
            right="b",
            then=Halt(value="a"),
            otherwise=Halt(value="b"),
        ),
        then=Halt(value="d"),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="d",
        count=3,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(
                base="d",
                index=0,
                value="abstract_heap0",
                then=L0.Store(
                    base="d",
                    index=2,
                    value="b",
                    then=L0.Store(base="d", index=1, value="a", then=h("d")),
                ),
            ),
        ),
    )
    expected_procedures = [
        proc(
            "abstract_code0",
            ["abstract_env0", "x"],
            L0.Copy(
                destination="d",
                source="abstract_env0",
                then=L0.Load(
                    destination="b",
                    base="abstract_env0",
                    index=2,
                    then=L0.Load(
                        destination="a",
                        base="abstract_env0",
                        index=1,
                        then=L0.Branch(operator="==", left="a", right="b", then=h("a"), otherwise=h("b")),
                    ),
                ),
            ),
        )
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Abstract(
        destination="rec",
        parameters=["x"],
        body=Apply(target="rec", arguments=["x"]),
        then=Halt(value="rec"),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="rec",
        count=1,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(base="rec", index=0, value="abstract_heap0", then=h("rec")),
        ),
    )
    expected_procedures = [
        proc(
            "abstract_code0",
            ["abstract_env0", "x"],
            L0.Copy(
                destination="rec",
                source="abstract_env0",
                then=L0.Load(
                    destination="apply_code0",
                    base="rec",
                    index=0,
                    then=L0.Call(target="apply_code0", arguments=["rec", "x"]),
                ),
            ),
        )
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures

    statement = Abstract(
        destination="d",
        parameters=[],
        body=Store(base="b", index=0, value="v", then=Halt(value="v")),
        then=Halt(value="d"),
    )
    actual_procedures: list[L0.Procedure] = []
    l0_actual = close_statement(statement=statement, procedures=actual_procedures, fresh=SequentialNameGenerator())
    l0_expected = L0.Allocate(
        destination="d",
        count=3,
        then=L0.Address(
            destination="abstract_heap0",
            name="abstract_code0",
            then=L0.Store(
                base="d",
                index=0,
                value="abstract_heap0",
                then=L0.Store(
                    base="d",
                    index=2,
                    value="v",
                    then=L0.Store(base="d", index=1, value="b", then=h("d")),
                ),
            ),
        ),
    )
    expected_procedures = [
        proc(
            "abstract_code0",
            ["abstract_env0"],
            L0.Copy(
                destination="d",
                source="abstract_env0",
                then=L0.Load(
                    destination="v",
                    base="abstract_env0",
                    index=2,
                    then=L0.Load(
                        destination="b",
                        base="abstract_env0",
                        index=1,
                        then=L0.Store(base="b", index=0, value="v", then=h("v")),
                    ),
                ),
            ),
        )
    ]
    assert l0_actual == l0_expected
    assert actual_procedures == expected_procedures
