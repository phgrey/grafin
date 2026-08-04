import os
import pytest
from examples.scrum_life_assistant.phase1_scrum_sprint_langgraph import run_phase_1
from examples.scrum_life_assistant.phase2_crewai_specialists import run_phase_2
from examples.scrum_life_assistant.phase3_semantic_kernel_triz import run_phase_3
from examples.scrum_life_assistant.phase4_agy_crontab_life_scheduler import run_phase_4


def test_scrum_experiment_phases():
    manifest1 = run_phase_1()
    assert manifest1 is not None
    assert len(manifest1.nodes) >= 5

    manifest2 = run_phase_2()
    assert manifest2 is not None
    assert "crewai" in manifest2.framework_configs

    manifest3 = run_phase_3()
    assert manifest3 is not None
    assert "semantic_kernel" in manifest3.framework_configs

    manifest4 = run_phase_4()
    assert manifest4 is not None
