
## Grafin is:
 - the simplest coordinator for coordianators. 
    - langraph
    - crewai
    - semantic kernel
    - graph backend - YamlGraph. format should be tranlsatable to others.
 - workspace for developers
 - skill-sharing protocol (and soft)



## connection:
 - to implement open-ai skill with description. and access points for shared one, e.g. mysql db connection, file reference, tcp / unix sockets / pipes, chat channels, model / mcp / rest/ ... endpoints .e.g. for langgraph - graph editin connection is whole folder with python project. the same for crewai (team folder) and semantic kernel (plugins folder + config folder) - good workspace for developer.
 <!-- TODO: investigate -->
 ## mobile support - compilation
And if take all this stuff, will compile it with semantic kernel non-python variants - we will have a binary for user - semantic kernel that can e.g. control graph (abilities - by commands? plugins written by us previously - to python)
 TODO: take a look at graph skilllset - to define what we actually can export from langgraph (langgraph.json only?) and how we can actually modify the graph and it's state without code updating. And make python adapters, and extend CrewAI's tools and semantic kernel's commands/plugins with them. And than take a look - what language will be next?
 it should be ither compilable, or bring us to the whole new ecofamily, e.g. js/ts + openclaw + soul.md (if wide-usable) - than we can find something compilable for graph processing as well.

 the same for langraph - who can import langgraph's graphs? 


 - to implement single adapter foreach language. On the same language. (for now we have python. cython javascript, go, c++ - in plans) core (graphin) - python? or cython?
 - с подключением к vs-code-like ides - through Devcontainers
 - 

## Examples
### 1 - obvoius usage
We've build langgraph, than asked connected vi graphin CrewAI to pass the graph and optimize it. to build some uml diagrams for it and optimize the code directly.
as well as we later will take all this stuff to semantic kernel and discuss it in any potision, maybe some well-known alghoryth and can be optimized this or that way. and maybe mathematic graph theory will help us to optimize it better. TRIZ, graph algorithms, wolfram, etc.
result - working plan given to python dev/agent.

No graph skills, simple graph, single language, no real cooperating - good example #1.

### 2 the same, but a bit deeper
> Use NeMo Agent Toolkit if you are deploying to production and need unified OpenTelemetry tracing across multiple distinct frameworks (like LangChain or CrewAI) running on top of NVIDIA NIM infrastructure.



Adding skillset level for operating on common graph. Experiment's useful artifacts - add to codebase.
complex constant langraph (idea realiser - SCRUM-based + few incident-related tasks + side one-time tasks - doctor appointment, cv refine, learning plan, budjet, etc.) 

python langgraph graph skillset - code examples how to get / set graph / node structure / state for external user in / out of his codebase. maybe cli commands. put in graphin core graph skillsets.

crontab-based agent-scheduler with graph skillset - to test if can be used as a graph walker and fullfill graph skillset.
and make him adapters to operate with graph. And save this skillset as a  cheduler abilities adopted for graph walking. if crontab can - any sheduler will. describe crontab as a cheduler skillset.
The same for CrewAI and semantic kernel - fullfill their graph skillsets. 

## graphin space:
 graphin is a workspace on device:
 - models (local / cloud) - the sallest devices - wiout local, poor connect - without cloud
 - per-orchestrator per-project devcontainers (local / cloud) -  for developers mostly, 
 - other utils containers - logs, compiled in container utils, stable versions of projects - for users and for comparing by developers
 - per-device compiled binaries with UX - e.g. for ipad - c++-claw based app with small local model (or adopted for prediction system model) and our interface implemented on c++. it's a util app for graphin.
- and grafin (agent  + process + model + config + bridge), 
- config file with list of all contributors attached - dev / docker / bin - `graphin.yaml`
- and our p2p network connection for stable cloud / on-premises versions (in case of need - we will use tailscale / ipfs / others)
