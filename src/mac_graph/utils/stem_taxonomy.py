from typing import Dict, List

# Controlled taxonomy of STEM disciplines and subfields
STEM_TAXONOMY: Dict[str, List[str]] = {
    "Science": [
        "Physics",
        "Quantum Mechanics",
        "Chemistry",
        "Biology",
        "Genetics",
        "Biochemistry",
        "Neuroscience",
        "Astronomy",
        "Earth & Environmental Science",
        "Materials Science",
    ],
    "Technology": [
        "Computer Science",
        "Artificial Intelligence & Machine Learning",
        "Software Engineering",
        "Cybersecurity",
        "Data Science & Analytics",
        "Robotics & Automation",
        "Information Systems",
        "Cloud Computing & Networks",
    ],
    "Engineering": [
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil & Structural Engineering",
        "Chemical Engineering",
        "Aerospace Engineering",
        "Biomedical Engineering",
        "Systems Engineering",
    ],
    "Mathematics": [
        "Pure Mathematics",
        "Applied Mathematics",
        "Statistics & Probability",
        "Calculus & Analysis",
        "Linear Algebra",
        "Discrete Mathematics",
        "Differential Equations",
        "Optimization",
    ],
}


def get_all_disciplines() -> List[str]:
    """Return a flat list of all defined STEM subdisciplines."""
    disciplines = []
    for domain, subfields in STEM_TAXONOMY.items():
        disciplines.extend(subfields)
    return disciplines


def get_stem_domains() -> List[str]:
    """Return top-level STEM domain names (Science, Technology, Engineering, Mathematics)."""
    return list(STEM_TAXONOMY.keys())


def validate_discipline(discipline: str) -> bool:
    """Check if a discipline name belongs to the STEM taxonomy."""
    all_disciplines = set(get_all_disciplines()) | set(get_stem_domains())
    return discipline.strip().lower() in {d.lower() for d in all_disciplines}
