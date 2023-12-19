import os

import pytest

from day_19.compute import (
    Workflow,
    q1,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestWorkflow:
    def test_loading(self, small_ex_txt):
        workflow = Workflow.from_file(small_ex_txt)
        assert 'in' in workflow.workflows
        assert len(workflow.workflows) == 11
        assert len(workflow.parts) == 5


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Workflow.from_file(small_ex_txt)) == 19114

    def test_input(self, input_txt):
        assert q1(Workflow.from_file(input_txt)) == 487623
