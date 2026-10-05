import os
import sys

# Ensure project modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from multi_tool_agent.rag import index_document_chunk

REFERENCE_SOURCES = [
    {
        "title": "PMC12484150: The Impacts of War on Health, Human Rights, and Environment",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12484150/",
        "content": "War causes severe environmental degradation, chemical contamination, long-term health vulnerabilities, and public health infrastructure collapse post-conflict.",
        "category": "Health & Environment",
    },
    {
        "title": "Oxford Exposome (2026): War Exposome Framework",
        "url": "https://academic.oup.com/exposome/article/6/1/osag003/8460765",
        "content": "Introduces the war exposome framework combining environmental mapping, heavy metal contamination, microplastics, and chronic psychosocial trauma.",
        "category": "Exposome & Toxicology",
    },
    {
        "title": "UNEP: Curbing Negative Environmental Impacts of War",
        "url": "https://www.unep.org/news-and-stories/statements/curbing-negative-environmental-impacts-war-and-armed-conflict",
        "content": "UNEP strategies detailing post-conflict environmental assessments, toxic hot-spots remediation, ecosystem restoration, and water pollution management.",
        "category": "Environmental Policy",
    },
    {
        "title": "UN Peacekeeping: How Conflict Impacts Our Environment",
        "url": "https://www.un.org/en/peace-and-security/how-conflict-impacts-our-environment",
        "content": "UN report detailing deforestation, habitat loss, soil destruction, and oil pipeline pollution resulting from armed conflict.",
        "category": "Ecosystem & Biodiversity",
    },
    {
        "title": "Northern Uganda WAYS Study: Postwar Environment & Mental Health",
        "url": "https://www.researchgate.net/publication/259588649_Postwar_environment_and_long-term_mental_health_problems_in_former_child_soldiers_in_Northern_Uganda_The_WAYS_study",
        "content": "Longitudinal evaluation of post-war social environments, trauma, and long-term mental health challenges faced by former child soldiers.",
        "category": "Mental Health & Trauma",
    },
    {
        "title": "ResearchGate: Salting the Earth - Post-Conflict Reconstruction",
        "url": "https://www.researchgate.net/publication/350850248_Salting_the_Earth_Environmental_health_challenges_in_post-conflict_reconstruction",
        "content": "Evaluates heavy metal accumulation, agricultural soil toxicity, and water source contamination during post-conflict reconstruction.",
        "category": "Reconstruction & Soil",
    },
]


def ingest_reference_links():
    print(f"Indexing {len(REFERENCE_SOURCES)} reference link sources into vector store...")
    success_count = 0

    for source in REFERENCE_SOURCES:
        try:
            index_document_chunk(
                title=source["title"],
                content=source["content"],
                metadata={
                    "url": source["url"],
                    "category": source["category"],
                    "source": "academic_reference_link",
                },
            )
            print(f"[OK] Indexed: {source['title']}")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] Error indexing {source['title']}: {e}")

    print(f"Finished vectorizing reference links ({success_count}/{len(REFERENCE_SOURCES)} successful).")


if __name__ == "__main__":
    ingest_reference_links()