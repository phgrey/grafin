# STEM Markdown Document Processor (GraphIn Example)

This is an example GraphIn application that demonstrates manifest-driven graph execution for processing Markdown documents, performing semantic section chunking, classifying text into STEM taxonomy subfields, and handling Human-in-the-Loop (HITL) interrupts when classification confidence is below threshold.

## GraphInYAML Manifest

The workflow execution pipeline is defined in [stem_markdown_processor.graphin.yaml](file:///Users/ssemenov/Documents/antigravity/valiant-kepler/examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml).

## Running the Example

Run the GraphIn engine using the CLI:

```bash
graphin process --manifest examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml --source-dir examples/stem_markdown_processor/data/source --output-dir examples/stem_markdown_processor/data/results
```
