from src.re.adapters.excel_output.n08_0038 import N08_0038_OUTPUT_PROFILE


def test_n08_write_contract_is_explicit_and_never_targets_formula_signatures():
    profile = N08_0038_OUTPUT_PROFILE
    formula_cells = {item.cell for item in profile.template_profile.formula_signatures}
    write_cells = {item.cell for item in profile.write_bindings}
    compatibility_cells = {item.cell for item in profile.compatibility_bindings}

    assert write_cells
    assert write_cells.isdisjoint(formula_cells)
    assert compatibility_cells == {"Phieu TTTT!E5"}
    assert compatibility_cells.isdisjoint(formula_cells)

    expected_rate_cells = {
        f"Bangtinh!{column}{row}"
        for column in "FGH"
        for row in (55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105)
    }
    assert expected_rate_cells.issubset(write_cells)


def test_gate_b10_output_consumers_explicitly_keep_g181_and_g182_distinct():
    consumers = {
        item.cell: (item.semantic_key, item.expected_formula)
        for item in N08_0038_OUTPUT_PROFILE.output_consumers
    }
    assert consumers["Bangtinh!G181"] == (
        "total_value_before_rounding_vnd",
        "=ROUND(G169+G178,0)",
    )
    assert consumers["Bangtinh!G182"] == (
        "final_appraised_value_vnd",
        "=ROUND(G181,-6)",
    )
    assert consumers["Offical!E32"] == (
        "total_value_before_rounding_vnd",
        "=Bangtinh!G181",
    )
