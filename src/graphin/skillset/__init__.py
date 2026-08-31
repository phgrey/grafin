"""Graph Skillsets Protocol package for GraphIn."""

from graphin.skillset.base import GraphSkillset
from graphin.skillset.manager import SkillsetManager, StandardGraphSkillset

try:
    from graphin.skillset.manager import CordisSkillsetService
    __all__ = [
        "GraphSkillset",
        "SkillsetManager",
        "StandardGraphSkillset",
        "CordisSkillsetService",
    ]
except ImportError:
    __all__ = [
        "GraphSkillset",
        "SkillsetManager",
        "StandardGraphSkillset",
    ]

