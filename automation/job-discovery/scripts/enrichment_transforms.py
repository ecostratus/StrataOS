"""
Enrichment transforms for canonical job entries.

Provides pure, deterministic inference of:
- skills: inferred technical/soft skills
- domain_tags: area tags (backend, data, devops, etc.)
- seniority: one of {intern,junior,mid,senior,staff,principal,lead,manager}
- stack: inferred technologies/frameworks/clouds

All functions are pure and operate on existing canonical fields.
Inputs may include optional fields like description; functions are resilient
to missing keys.
"""

from __future__ import annotations

from typing import Dict, List, Set, Any


_TECH_KEYWORDS = {
    "python": "Python",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "angular": "Angular",
    "vue": "Vue",
    "node": "Node.js",
    "nodejs": "Node.js",
    "java ": "Java",
    " kotlin": "Kotlin",
    "c#": "C#",
    "dotnet": ".NET",
    ".net": ".NET",
    "go ": "Go",
    "golang": "Go",
    "ruby": "Ruby",
    "rails": "Rails",
    "php": "PHP",
    "swift": "Swift",
    "objective-c": "Objective-C",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "sql": "SQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "graphql": "GraphQL",
    "rest": "REST",
    "restful": "REST",
    "microservices": "Microservices",
    # Expanded cloud/services
    "lambda": "AWS Lambda",
    "serverless": "Serverless",
    "cloud functions": "Cloud Functions",
    "azure functions": "Azure Functions",
    "s3": "S3",
    "ec2": "EC2",
    "ecs": "ECS",
    "eks": "EKS",
    "sqs": "SQS",
    "bigquery": "BigQuery",
    "pub/sub": "Pub/Sub",
    "cloud run": "Cloud Run",
    # CI/CD & IaC
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "circleci": "CircleCI",
    "ci/cd": "CI/CD",
    "terraform": "Terraform",
    "pulumi": "Pulumi",
    "cloudformation": "CloudFormation",
    "bicep": "Bicep",
    "helm": "Helm",
    # Messaging/observability
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    # Datastores / NoSQL
    "mongodb": "MongoDB",
    "dynamodb": "DynamoDB",
    "cassandra": "Cassandra",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    # Data/ML libraries
    "spark": "Apache Spark",
    "hadoop": "Hadoop",
    "databricks": "Databricks",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "scikit-learn",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    # Web frameworks
    "spring boot": "Spring Boot",
    " spring": "Spring",
    "asp.net": "ASP.NET",
    ".net core": ".NET Core",
}


_DOMAIN_TAGS = {
    "backend": ["backend", "server", "api", "microservices"],
    "frontend": ["frontend", "front-end", "ui", "react", "angular", "vue"],
    "mobile": ["mobile", "ios", "android", "swift", "kotlin"],
    "data": ["data", "analytics", "etl", "warehouse", "ml", "machine learning"],
    "devops": ["devops", "sre", "platform", "infrastructure", "kubernetes", "docker"],
    "security": ["security", "infosec", "appsec", "secops"],
    "ml": ["ml", "machine learning", "deep learning", "ai", "pytorch", "tensorflow"],
    "cloud": ["cloud", "serverless", "lambda", "functions", "aws", "azure", "gcp"],
    "data-platform": ["spark", "hadoop", "kafka", "warehouse", "databricks"],
}


_SENIORITY_MAP = [
    ("principal", "principal"),
    ("staff", "staff"),
    ("lead", "lead"),
    ("manager", "manager"),
    ("senior", "senior"),
    ("sr.", "senior"),
    ("jr.", "junior"),
    ("junior", "junior"),
    ("intern", "intern"),
]


def infer_seniority(text: str) -> str:
    t = text.lower()
    for key, val in _SENIORITY_MAP:
        if key in t:
            return val
    # Default heuristic: manager titles
    if "engineering manager" in t or "manager" in t:
        return "manager"
    # Assume mid-level when unspecified
    return "mid"


def infer_domain_tags(text: str) -> List[str]:
    t = text.lower()
    tags: List[str] = []
    for tag, keys in _DOMAIN_TAGS.items():
        if any(k in t for k in keys):
            tags.append(tag)
    # Stable order
    return sorted(set(tags))


def infer_stack(text: str) -> List[str]:
    t = text.lower()
    found: Set[str] = set()
    for key, norm in _TECH_KEYWORDS.items():
        if key in t:
            found.add(norm)
    return sorted(found)


def extract_skills(text: str) -> List[str]:
    # For now mirror stack keywords and add soft indicators if present
    t = text.lower()
    skills: Set[str] = set(infer_stack(text))
    if "lead" in t or "manager" in t or "mentorship" in t:
        skills.add("Leadership")
    if "agile" in t or "scrum" in t:
        skills.add("Agile")
    if "ci/cd" in t or "pipeline" in t or "jenkins" in t or "github actions" in t or "gitlab ci" in t or "circleci" in t:
        skills.add("CI/CD")
    return sorted(skills)


def enrich_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dict with enrichment fields added.

    Safe for missing fields; operates on `title` and optional `description`.
    """
    title = str(job.get("title", ""))
    desc = str(job.get("description", ""))
    basis = f"{title} {desc}".strip()

    enriched = dict(job)
    enriched["seniority"] = infer_seniority(basis) if basis else "mid"
    enriched["domain_tags"] = infer_domain_tags(basis) if basis else []
    enriched["stack"] = infer_stack(basis) if basis else []
    enriched["skills"] = extract_skills(basis) if basis else []
    return enriched
