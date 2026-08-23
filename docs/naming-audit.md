# Naming and competitive audit

Audit date: 2026-08-23. Code and repository creation began only after this audit.

Checks included PyPI JSON endpoints, GitHub owner/repository and indexed searches,
general web search, scientific-software search, companies/products, chemistry usage,
and possible Python/macOS/Qt framework confusion.

| Candidate | Assessment | Finding |
|---|---|---|
| CatPrep | HIGH RISK | Existing PyPI categorical-preprocessing package; eROSITA/XMM CATPREP task; Chemspeed CatPrep equipment; catalyst-preparation school; catprep.com test-prep software |
| CatalystRecipe | MINOR RISK | PyPI unregistered, but generic phrase and noisy “recipe” search results |
| CatalystPrepCalc | CLEAR | No exact PyPI/repository collision found; descriptive but long |
| **ImpregCalc** | **CLEAR — selected** | PyPI unregistered; owner repository absent; no indexed scientific/package/product collision found |
| ImpregPlan | CLEAR | No material collision found; “plan” says less about arithmetic |
| CatStoich | MINOR RISK | No package collision found; “cat” is ambiguous outside catalysis |
| PrepStoich | CLEAR | No material collision found; less specific to supported impregnation |
| PrecursorPlan | MINOR RISK | Generic and could describe unrelated synthesis planning |
| CatalystDose | MINOR RISK | “Dose” can imply dosing hardware or medicine |
| SupportDose | MINOR RISK | Ambiguous support/medical search meaning |
| ImpregRecipe | CLEAR | No material collision found; less natural pronunciation |
| CatRecipe | MINOR RISK | “Cat” strongly collides with animal-content searches |
| CatalystBatch | MINOR RISK | Could mean batch reactor or CI batching rather than preparation |

Selected project name: **ImpregCalc**  
GitHub repository: `ImpregCalc`  
PyPI candidate: `impregcalc`  
Python import: `impregcalc`

The name is short, pronounceable, package-natural, and directly evokes the initial
IWI/wet-impregnation calculation scope. It does not resemble Tk, Qt, PyQt, PySide,
or a known macOS framework. Known risk: the name would feel narrow if a future
release moved substantially beyond impregnation; such scope expansion is not part of
0.1.x.

Relevant competing/adjacent tools found during the audit include Chemspeed's
commercial ISYNTH CATIMPREG automation platform and CatCost, an NREL/CCB catalyst
cost-estimation tool. They address automation/equipment or economics rather than a
small vendor-neutral, open Python stoichiometric recipe engine.

