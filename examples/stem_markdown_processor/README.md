# STEM Markdown Document Processor (GraphIn Example)

# 1 - obvoius usage
We've build langgraph, than asked connected vi graphin CrewAI to pass the graph and optimize it. to build some uml diagrams for it and optimize the code directly.
as well as we later will take all this stuff to semantic kernel and discuss it in any potision, maybe some well-known alghoryth and can be optimized this or that way. and maybe mathematic graph theory will help us to optimize it better. TRIZ, graph algorithms, wolfram, etc.
result - working plan given to python dev/agent.

No graph skills, simple graph, single language, no real cooperating - good example #1.

This is an example GraphIn application that demonstrates manifest-driven graph execution for processing Markdown documents, performing semantic section chunking, classifying text into STEM taxonomy subfields, and handling Human-in-the-Loop (HITL) interrupts when classification confidence is below threshold.

## GraphInYAML Manifest

The workflow execution pipeline is defined in [stem_markdown_processor.graphin.yaml](file:///Users/ssemenov/Documents/antigravity/valiant-kepler/examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml).

## Running the Example

Run the GraphIn engine using the CLI:

```bash
graphin process --manifest examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml --source-dir examples/stem_markdown_processor/data/source --output-dir examples/stem_markdown_processor/data/results
```
