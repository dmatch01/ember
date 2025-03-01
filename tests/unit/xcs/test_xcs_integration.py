"""Integration tests for XCS components.

This module tests an end-to-end workflow that covers tracing, graph compilation,
and execution using a mock operator.
"""

from typing import Any, Dict

from ember.core.registry.operator.base.operator_base import Operator
from ember.xcs.tracer.xcs_tracing import TracerContext
from ember.xcs.tracer.tracer_decorator import jit


@jit()
class MockOperator(Operator[Dict[str, Any], Dict[str, Any]]):
    """Mock operator for integration tests that doubles the input value.

    Attributes:
        signature: A dummy signature providing input model definitions and basic
                   validation methods.
    """

    # For testing, we use a simplified signature.
    signature = type(
        "DummySignature",
        (),
        {
            "input_model": dict,
            "validate_inputs": lambda self, *, inputs: inputs,
            "validate_output": lambda self, *, output: output,
            "render_prompt": lambda self, *, inputs: "dummy prompt",
        },
    )()

    def forward(self, *, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the operator, doubling the input 'value'.

        Args:
            inputs (Dict[str, Any]): A dictionary containing the key 'value'
                with a numeric value.

        Returns:
            Dict[str, Any]: A dictionary with key 'result' containing the doubled value.
        """
        return {"result": inputs["value"] * 2}


def test_tracer_to_execution() -> None:
    """Tests a simplified end-to-end workflow with the new tracer context."""
    mock_operator: MockOperator = MockOperator()
    sample_input: Dict[str, Any] = {"value": 5}

    # Updated usage: no parameters to TracerContext
    with TracerContext() as tctx:
        _ = mock_operator(inputs=sample_input)

    # Verify that a trace record was captured
    assert (
        len(tctx.records) >= 1
    ), "No trace records captured during mock operator execution."

    # Check that the recorded output matches the expected doubled value
    found = False
    for record in tctx.records:
        if "result" in record.outputs:
            assert (
                record.outputs["result"] == 10
            ), f"Expected {{'result': 10}}, got {record.outputs}"
            found = True
            break
    assert found, "No trace record contained the expected doubled value."
