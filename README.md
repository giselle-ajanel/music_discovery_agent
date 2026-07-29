# Music Discovery Assistant 

An intelligent GraphRAG (Retrieval-Augmented Generation) agent that translates natural language questions into graph queries to explore multi-band musicians, supergroups, side projects, and band rosters—without technical jargon.



## Project Demo & Visuals

* **Live Agent Recording:** Check out the `music-discovery.mov` (or video link) to see the agent answering natural language queries about artist family trees and music recommendations in real time.

---

## System Architecture

```mermaid
graph LR
    A[music_connections.csv] -->|Data Importer| B[(Neo4j Knowledge Graph)]
    C[User Natural Language Query] --> D[Neo4j GraphRAG Agent]
    D -->|Cypher Tools & Text2Cypher| B
    B -->|Retrieved Graph Context| D
    D -->|Grounded Natural Language Answer| E[User UI / Chat]
