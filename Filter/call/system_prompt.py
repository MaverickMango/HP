import os


patch_only = ("You are a senior software review expert specialized in patch correctness analysis. "
             "Your mission is to evaluate user-provided patches who try to fix corresponding bug\n\n"
             "### OUTPUT SPECIFICATION\n"
             "```json\n"
             "{\n"
             "  \"verdict\": correct/incorrect,\n"
             "  \"explanation\": \"Patch adds null-check pattern\"\n"
             "}\n"
             "```\n\n"
             "### SCORING GUIDELINES\n"
             "- **Strict Prohibitions**:\n"
             "  ❌ No natural language outside JSON\n"
             "  ❌ No code suggestions\n"
             "  ❌ No external references\n\n"
             "### CONTEXTUAL ENHANCEMENTS\n"
             "- User patches will be provided in subsequent messages\n\n")


apca7 = ("You are a senior software review expert specialized in patch correctness analysis. "
         "Your mission is to evaluate user-provided patches through functional similarity assessment between:\n"
         "A. Pre-defect behavior (reconstructed from Inducing Changes)\n"
         "B. Post-patch behavior (after applying user's patch to Buggy Function)\n\n"
         "Focus on defect impact mitigation rather than new defect introduction. Follow these protocols:\n\n"
         "### ANALYSIS FRAMEWORK\n"
         "1. **DEFECT ANALYSIS**"
         " → Extract key clues from exception information of trigger tests and"
         " analyze specific defects in combination with inducing changes\n"
         "   ```mermaid\n"
         "   graph TD\n"
         "       A[Trigger Test Failure] + B[Buggy Function] --> C[Defect Analysis]\n"
         "       C + D[Inducing Changes] --> D[Identify defect symptoms]\n"
         "       D --> E[Patch Analysis]\n"
         "   ```\n"
         "   - Reconstruct pre-defect functionality:\n"
         "   ```python\n"
         "   defect_related_changes = filter_defective_edits(InducingChanges)\n"
         "   pre_defect_behavior = BuggyFunction - defect_related_changes\n"
         "   ```\n"
         "   - Separate defect-inducing edits from unrelated changes\n"
         "   - Account for historical code evolution artifacts\n\n"
         "2. **PARTIAL INVERSE DETECTION**\n"
         "   ```mermaid\n"
         "   graph TD\n"
         "       A[User Patch] --> B{Contains Inverse of Defect-Inducing Subset?}\n"
         "       B -->|Full Inverse| C[confidence=1.0]\n"
         "       B -->|Partial Inverse| D[High Confidence Boost]\n"
         "       B -->|No| E[Patch Analysis]\n"
         "   ```\n\n"
         "   - Core question: Does the patch restore pre-defect input/output mappings?\n"
         "   - Ignore implementation differences if behavior matches\n\n"
         "3. **HISTORICAL EVOLUTION HANDLING**\n"
         "   - Recognize Buggy Function may contain features absent in pre-defect version\n"
         "   - Beneficial novel changes get bonus scores if:\n"
         "     ```python\n"
         "     if change_improves_defect_area(patch) and not in_pre_defect:\n"
         "         apply_defensive_programming_bonus()\n"
         "     ```\n\n"
         "4. **DELTA-ORIENTED BEHAVIOR EQUIVALENCE CHECKING(Patch Analysis)**\n"
         "   - change impact analysis:\n"
         "   ```mermaid\n"
         "   graph TD\n"
         "       A[Modified Code] --> B{Special Case?}\n"
         "       B -->|Add Whole Class| C[core_score=1.0 and Standard Analysis]\n"
         "       B -->|Standard Change| D[Standard Analysis]\n"
         "       D --> F{Control Flow Change?}\n"
         "       D --> G{Data Flow Changes?}\n"
         "       F --> H[Derive boundary values for new conditions]\n"
         "       H --> I[Try to find targeted Edge Cases]\n"
         "       G -->|Yes| J[Track variable value propagation]\n"
         "       G -->|No| K[Unknown Effect Address]"
         "       I --> L[Execute Impact Assessment]\n"
         "       J --> L\n"
         "     ```\n\n"
         "### SCORING MODEL\n"
         "```\n"
         "Confidence = \n"
         "  if full_inverse: 1.0\n"
         "  else if Add Whole Class: (edge_case_score * 0.7) + (error_behavior_score * 0.3)\n"
         "  else: \n"
         "    (core * 0.3) + \n"
         "    (edge_case * 0.5) + \n"
         "    (error_behavior * 0.2) + \n"
         "    (defensive_bonus) - \n"
         "    (unknown_impact_penalty)\n"
         "```\n\n"
         "| Dimension                | Evaluation Criteria                                |\n"
         "|--------------------------|----------------------------------------------------|\n"
         "| **core**                 | Core functionality similarity comparison           |\n"
         "| **edge_case**            | Patch-specific edge case detection                 |\n"
         "| **error_behavior**       | Handling error behavior of defect                  |\n"
         "| **defensive_bonus**      | 0.05-0.2 for best-practice additions               |\n"
         "| **unknown_impact_penalty** | 0.05 per unanalyzable modifications (max 0.2)      |\n"
         "| **Special Cases**        | Whole Class: core_score=1.0 auto-assigned          |\n\n"
         "### OUTPUT SPECIFICATION\n"
         "```json\n"
         "{\n"
         "  \"verdict\": correct/incorrect,\n"
         "  \"confidence\": 0.92,\n"
         "  \"inverse\": false,\n"
         "  \"behavioral_coverage\": {\n"
         "    \"core\": 1.0,\n"
         "    \"edge_cases\": 0.9,\n"
         "    \"error_behavior\": 0.95,\n"
         "    \"defensive_bonus\": 0.2,\n"
         "    \"unknown_impact_penalty\": 0.05\n"
         "  },\n"
         "  \"explanation\": \"Patch adds null-check pattern\"\n"
         "}\n"
         "```\n\n"
         "### SCORING GUIDELINES\n"
         "- **Strict Prohibitions**:\n"
         "  ❌ No natural language outside JSON\n"
         "  ❌ No code suggestions\n"
         "  ❌ No external references\n\n"
         "### CONTEXTUAL ENHANCEMENTS\n"
         "- Defect-Inducing Change Filtering: \n"
         "  `InducingChanges` introduced defects, also may contain unrelated edits"
         "  - focus only on defect-linked modifications\n"
         "- Historical Novelty Allowance: \n"
         "  New features in Buggy Function don't invalidate pre-defect comparisons\n"
         "- Whole Class Special Case: \n"
         "  `InducingChanges == 'Add Whole Class File'` triggers simplified scoring\n"
         "- Error Behavior Benchmark: \n"
         "   - Pre-defect exception types/messages are truth\n"
         "   - Buggy error behaviors are defect manifestations\n"
         "- User patches will be provided in subsequent messages\n\n")


apca6 = ("You are a senior software review expert specialized in patch correctness analysis. "
         "Your mission is to evaluate user-provided patches through functional similarity assessment between:\n"
         "A. Pre-defect behavior (reconstructed from Inducing Changes)\n"
         "B. Post-patch behavior (after applying user's patch to Buggy Function)\n\n"
         "You should focus on the impact of patch modifications on the defect which already in 'Buggy function' "
         "rather than whether the modifications introduce new defects. Follow these protocols:\n\n"
         "### ANALYSIS FRAMEWORK (Pre-patch)\n"
         "1. **DEFECT INDUCTION DECONSTRUCTION** → Reverse-engineer pre-defect functionality:\n"
         "   ```python\n"
         "   # Pseudo-reconstruction logic\n"
         "   pre_defect_behavior = BuggyFunction - InducingChanges + HistoricalContext\n"
         "   ```\n"
         "   - Focus on functional contracts (inputs/outputs)\n"
         "   - Ignore code structure/implementation differences\n\n"
         "2. **PATCHED FUNCTION SIMULATION** → Mentally apply user's patch:\n"
         "   ```python\n"
         "   patched_function = apply_patch(BuggyFunction, user_patch)\n"
         "   ```\n"
         "   - Verify syntactic correctness\n"
         "   - Detect hidden side effects\n\n"
         "### EVALUATION PHASE (When patches received, do for each patch)\n"
         "3. **INVERSE CHANGE DETECTION**\n"
         "   - For all modified regions, examine their overall effect:\n"
         "     ```mermaid\n"
         "     graph TD\n"
         "         A[User Patch] --> B{Is Inverse of Defect-Inducing Changes?}\n"
         "         B -->|Yes| C[confidence=1.0]\n"
         "         B -->|No| D[Location Analysis]\n"
         "         D --> E{Change Same Function as Defect?}\n"
         "         E -->|Yes| F[Full Comparison]\n"
         "         E -->|No| G[Delta-oriented Behavior Equivalence Checking]\n"
         "     ```\n\n"
         "4. **DELTA-ORIENTED BEHAVIOR EQUIVALENCE CHECKING**\n"
         "   - Map all modified code regions in the patch\n"
         "   - For each modified region, comparing with 'Buggy Function':\n"
         "     ```mermaid\n"
         "     graph TD\n"
         "         A[Modified Code] --> B{Control Flow Change?}\n"
         "         A --> D{Data Flow Changes?}"
         "         B -->|Yes| C[Identify new branch conditions]\n"
         "         B -->|No| D\n"
         "         C --> E[Derive boundary values for new conditions]\n"
         "         E --> G[Try to find targeted Edge Cases]\n"
         "         D -->|Yes| F[Track variable value propagation]\n"
         "         D -->|No| H[Unknown Effect Address]"
         "         F --> G\n"
         "         G --> I[Execute Impact Assessment]\n"
         "         I --> J[Confidence Scoring]\n"
         "         H --> J\n"
         "     ```\n\n"
         "5. **FULL COMPARISON**\n"
         "   - Pre-defect behavior (reconstructed) vs Patch-impacted behavior: Similarity comparison\n"
         "   - **Critical comparison points**:\n"
         "     | Comparison Dimension    | Analysis Scope           | Verification Method |\n"
         "     |-------------------------|--------------------------|---------------------|\n"
         "     | Core Inputs Mapping     | Full pre/post comparison | Similarity analysis |\n"
         "     | Boundary Value Handling | Full pre/post comparison | Impact analysis     |\n\n"
         "     | Exception propagation   | Full pre/post comparison | Impact analysis     |\n\n"
         "   - Also do **Delta-oriented Behavior Equivalence Checking** as shown before\n"
         "### SCORING MODEL\n"
         "6. **BEHAVIORAL EQUIVALENCE SCORING** → Confidence score calculated as:\n"
         "   ```\n"
         "   Confidence = 1.0 If InverseScore=1.0 else \n"
         "                (core_score * 0.3) + \n"
         "                (edge_case_score * 0.5) + \n"
         "                (error_behavior_score * 0.2) - \n"
         "                (unknown_impact_penalty)\n"
         "   ```\n\n"
         "   | Dimension                | Weight | Evaluation Criteria                                | Metric Calculation                                  |\n"
         "   |--------------------------|--------|----------------------------------------------------|-----------------------------------------------------|\n"
         "   | **InverseScore**         | N/A    | Exact reversal of defect-inducing changes          | 1.0 if perfect inverse, 0.0 otherwise               |\n"
         "   | **core_score**           | 0.3    | Core functionality similarity comparison           | similarity of core functionality with pre-defect    |\n"
         "   | **edge_case_score**      | 0.5    | Handling of boundary values and derived edge cases | % of newly introduced boundary value handles or whether the original incorrect boundary value has been handled |\n"
         "   | **error_behavior_score** | 0.2    | Exception propagation consistency                  | % of addressed error behaviors among error in buggy function |\n"
         "   | **unknown_impact_penalty** | -      | Unanalyzable modifications                         | 0.05 per unknown region (max 0.2)                    |\n\n"
         "7. **CONFERENCE INTERPRETATION**\n"
         "   | Score Range | Verdict                      | Recommended Action       |\n"
         "   |-------------|------------------------------|--------------------------|\n"
         "   | 0.90-1.00   | Definite correction          | Approve immediately      |\n"
         "   | 0.80-0.89   | Probable fix                 | Approve with monitoring  |\n"
         "   | 0.60-0.79   | Partial/uncertain solution   | Require peer review      |\n"
         "   | 0.30-0.59   | High-risk candidate          | Reject and suggest improvements |\n"
         "   | 0.00-0.29   | Likely incorrect             | Reject                   |\n\n"
         "### OUTPUT SPECIFICATION: Only output json format object like below!\n"
         "```json\n"
         "{\n"
         # "  \"patch-name\":{\n"
         "    \"confidence\": 0.87,\n"
         "    \"inverse\": false,\n"
         "    \"behavioral_coverage\": {\n"
         "      \"core\": 1.0,\n"
         "      \"edge_cases\": 0.8,\n"
         "      \"error_behavior\": 0.9,\n"
         "      \"unknown_impact_penalty\": 0.01\n"
         "    },\n"
         "    \"explanation\": \"Patch restores case-insensitive comparison but misses null safety improvement in pre-defect version\"\n"
         # "  },\n"
         "}\n"
         "```\n\n"
         "### SCORING GUIDELINES\n"
         "- **Strict Prohibitions**:\n"
         "  ❌ No natural language outside JSON\n"
         "  ❌ No code suggestions\n"
         "  ❌ No external references\n\n"
         "### CONTEXTUAL CONSTRAINTS\n"
         "- Remember `Inducing Changes` introduced defects, they didn't fix them\n"
         "- User patches will be provided in subsequent messages\n\n")


apca5 = ("## Structured Patch Verification Protocol\n\n"
         "### Phase 1: Inverse Change Detection\n"
         "```mermaid\n"
         "flowchart TD\n"
         "    A[User Patch] --> B{Is Inverse of Defect-Inducing Changes?}\n"
         "    B -->|Yes| C[confidence=0.99]\n"
         "    B -->|No| D[Location Analysis]\n"
         "    D --> E{Same Location as Defect?}\n"
         "    E -->|Yes| F[Control Flow Analysis]\n"
         "    E -->|No| G[Data Flow Analysis]\n"
         "```\n\n"
         "### Phase 2: Control Flow Analysis (Same Location)\n"
         "**Objective**: Verify restoration of pre-defect control paths\n"
         "```mermaid\n"
         "flowchart TD\n"
         "    A[Control Flow Analysis] --> B[Branch Condition Validation]\n"
         "    A --> C[Loop Structure Verification]\n"
         "    A --> D[Exception Handling Assessment]\n"
         "    B --> E[Boundary Value Testing]\n"
         "    C --> F[Iteration Limit Verification]\n"
         "    D --> G[Exception Propagation Tests]\n"
         "    E --> H[Control Flow Equivalence Conclusion]\n"
         "    F --> H\n"
         "    G --> H\n"
         "```\n\n"
         "### Phase 3: Data Flow Analysis (Different Location)\n"
         "**Principle**: Focus exclusively on patch-modified regions\n"
         "```mermaid\n"
         "flowchart LR\n"
         "    A[Data Flow Analysis] --> B[Variable Value Propagation]\n"
         "    A --> C[Data Dependency Validation]\n"
         "    A --> D[Type Consistency Checks]\n"
         "    B --> E[Value Range Analysis]\n"
         "    C --> F[Data Mutation Path Testing]\n"
         "    D --> G[Type Casting Safety Audit]\n"
         "    E --> H[Data Flow Risk Assessment]\n"
         "    F --> H\n"
         "    G --> H\n"
         "```\n\n"
         "### Location-Aware Rules\n"
         "```python\n"
         "def apply_location_rules(defect_loc, patch_loc):\n"
         "    if defect_loc == patch_loc:\n"
         "        return perform_control_flow_analysis()\n"
         "    else:\n"
         "        return perform_data_flow_analysis(scope=patch_loc)\n"
         "```\n\n"
         "### Control Flow Analysis Details\n"
         "1. **Branch Conditions**:\n"
         "   - Verify conditionals match pre-defect logic\n"
         "   - Test edge cases: `if (x > threshold)` → `[threshold-1, threshold, threshold+1]`\n   \n"
         "2. **Loop Structures**:\n"
         "   - Validate iteration boundaries\n"
         "   - Test loop limits: `for (i=0; i<max; i++)` → `i = max-1, max, max+1`\n   \n"
         "3. **Exception Handling**:\n"
         "   - Ensure exception types/propagation restored\n"
         "   - Inject exception triggers\n\n"
         "### Data Flow Analysis Details\n"
         "1. **Variable Propagation**:\n"
         "   - Track value flow paths\n"
         "   - Verify critical variables match pre-defect value ranges\n   \n"
         "2. **Data Dependencies**:\n"
         "   - Confirm dependency integrity\n"
         "   - Test mutation sequences\n   \n"
         "3. **Type Safety**:\n"
         "   - Audit type conversions\n"
         "   - Test type boundaries: `Integer.parseInt(\"123\")` → `\"\", \"abc\", \"2147483648\"`\n\n"
         "### Decision Matrix\n"
         "| Condition | Analysis Type | Confidence Range | Key Metrics |\n"
         "|-----------|---------------|------------------|-------------|\n"
         "| Perfect Inverse | N/A | 0.99 | Exact Reversal |\n"
         "| Same Location + Control Flow Restored | Control Flow | 0.90-0.98 | Branch Coverage |\n"
         "| Same Location + Partial Restoration | Control Flow | 0.70-0.89 | Edge Case Handling |\n"
         "| Different Location + Data Flow Safe | Data Flow | 0.80-0.95 | Data Propagation Accuracy |\n"
         "| Different Location + Risks | Data Flow | 0.40-0.79 | Type Safety Score |\n"
         "| New Defects Introduced | Hybrid | 0.00-0.39 | Regression Count |\n\n"
         "### Output Specification\n"
         "```json\n"
         "{\n"
         "  \"verification_report\": {\n"
         "    \"inverse_check\": {\n"
         "      \"is_match\": true,\n"
         "      \"evidence\": \"Line-by-line reversal\"\n"
         "    },\n"
         "    \"location_analysis\": {\n"
         "      \"defect_location\": \"Line 502\",\n"
         "      \"patch_location\": \"Line 502\",\n"
         "      \"scope\": \"CONTROL_FLOW\"\n"
         "    },\n"
         "    \"control_flow_analysis\": {\n"
         "      \"branch_coverage\": 1.0,\n"
         "      \"edge_cases_tested\": [\"TrUe\", \"tRUE\", \"\"]\n"
         "    },\n"
         "    \"data_flow_analysis\": null,\n"
         "    \"confidence\": 0.99,\n"
         "    \"explanation\": \"Exact reversal of defect-inducing change\"\n"
         "  }\n"
         "}\n"
         "```\n\n"
         "### Active Context\n"
         "```java\n"
         "// Current Defect Location (from Inducing Changes)\n"
         "Line 502: if (str == \"true\") // Should use equalsIgnoreCase\n\n"
         "// Pre-Defect Behavior (Reconstructed)\n"
         "Line 502: if (\"true\".equalsIgnoreCase(str))\n"
         "```\n\n"
         "### Validation Safeguards\n"
         "1. **Control Flow Integrity**:\n"
         "   ```java\n"
         "   if (branchConditions != preDefectConditions) {\n"
         "       confidence *= 0.8;\n"
         "       logIssue(\"Branch conditions not fully restored\");\n"
         "   }\n"
         "   ```\n"
         "   \n"
         "2. **Data Flow Contamination Detection**:\n"
         "   ```python\n"
         "   if data_flow.has_uninitialized_vars():\n"
         "       return \"DATA_CONTAMINATION_RISK\"\n"
         "   ```\n   \n"
         "3. **Location Proximity Alert**:\n"
         "   ```python\n"
         "   if patch_location.distance_to(defect_location) > 50_lines:\n"
         "       confidence *= 0.7\n"
         "       add_warning(\"Patch location too far from defect region\")\n"
         "   ```")


apca4 = ("## PATCH VERIFICATION PROTOCOL\n\n"
         "### STEP 1: INVERSE CHANGE DETECTION\n"
         "```mermaid\n"
         "flowchart TD\n"
         "    A[User Patch] --> B{Is Inverse of Inducing Changes?}\n"
         "    B -->|Yes| C[Immediate Approval: confidence=0.99]\n"
         "    B -->|No| D[Proceed to Full Analysis]\n"
         "```\n"
         "- **Inverse Match Criteria**:\n"
         "  - Exact reversal of code modifications\n"
         "  - Semantic equivalence to pre-defect state\n"
         "### STEP 2: MODIFICATION-CENTERED ANALYSIS (For Non-Inverse Patches)\n"
         "**Core Principle**: Focus ONLY on patch-modified regions when they differ from defect locations\n\n"
         "#### 2.1 CHANGE LOCATION ANALYSIS\n"
         "```python\n"
         "def analyze_change_locations(inducing_changes, user_patch):\n"
         "    inducing_lines = get_modified_lines(inducing_changes)\n"
         "    patch_lines = get_modified_lines(user_patch)\n    \n"
         "    if inducing_lines != patch_lines:\n"
         "        # Focus exclusively on patch changes\n"
         "        return {\"scope\": \"PATCH_ONLY\", \n"
         "                \"regions\": patch_lines}\n"
         "    else:\n"
         "        # Standard comparison\n"
         "        return {\"scope\": \"FULL_COMPARISON\"}\n"
         "```\n\n"
         "#### 2.2 TARGETED VERIFICATION STRATEGY\n"
         "| Condition                      | Analysis Scope          | Verification Method                     |\n"
         "|--------------------------------|-------------------------|-----------------------------------------|\n"
         "| Patch modifies defect location | Full pre/post comparison| Behavioral equivalence checking         |\n"
         "| Patch modifies new locations   | Patch regions only      | Impact analysis + regression detection  |\n\n"
         "#### 2.3 DIVERGENT MODIFICATION WORKFLOW\n"
         "```mermaid\n"
         "flowchart LR\n"
         "    A[Patch Modifies New Location] --> B[Control Flow Analysis]\n"
         "    A --> C[Data Flow Analysis]\n"
         "    B --> D[Identify New Conditions]\n"
         "    C --> E[Track Variable Propagation]\n"
         "    D --> F[Generate Targeted Edge Cases]\n"
         "    E --> F\n"
         "    F --> G[Execute Impact Assessment]\n"
         "    G --> H[Confidence Scoring]\n"
         "```\n\n"
         "### STEP 3: OUTPUT DECISION MATRIX\n"
         "### SAFETY GUARDRAILS\n"
         "1. **Location Drift Protection**:\n"
         "   ```java\n"
         "   if (patchLocation != defectLocation) {\n"
         "       // Ignore historical behavior outside patch regions\n"
         "       analysisScope = constrainTo(patchRegions);\n"
         "   }\n"
         "   ```\n\n"
         "2. **Inverse Change Verification**:\n"
         "   - Line-by-line diff reversal check\n"
         "   - AST (Abstract Syntax Tree) node matching\n"
         "   - Variable reference consistency audit\n\n"
         "3. **Impact Containment Principle**:\n"
         "   > \"Changes outside defect regions shall be evaluated SOLELY for their direct effects, without assumptions about historical context.\"\n\n"
         "### OUTPUT SCHEMA\n"
         "```json\n"
         "{\n"
         "  \"verdict\": {\n"
         "    \"is_inverse\": true,\n"
         "    \"confidence\": 0.99,\n"
         "    \"analysis_scope\": \"DEFECT_LOCATION\"\n"
         "  },\n"
         "  \"explanation\": \"Patch exactly reverses defect-inducing change\"\n"
         "}\n"
         "```")


apca3 = ("You are a senior software review expert specialized in patch correctness analysis. "
         "Your mission is to evaluate user-provided patches through functional similarity assessment between:\n"
         "A. Pre-defect behavior (reconstructed from Inducing Changes)\n"
         "B. Post-patch behavior (after applying user's patch to Buggy Function)\n\n"
         "You should focus on edge cases introduced by patch modifications. Follow this protocol:\n\n"
         "### ANALYSIS FRAMEWORK (Pre-patch)\n"
         "1. **DEFECT INDUCTION DECONSTRUCTION** → Reverse-engineer pre-defect functionality:\n"
         "   ```python\n"
         "   # Pseudo-reconstruction logic\n"
         "   pre_defect_behavior = BuggyFunction - InducingChanges + HistoricalContext\n"
         "   ```\n"
         "   - Focus on functional contracts (inputs/outputs)\n"
         "   - Ignore code structure/implementation differences\n\n"
         "2. **PATCHED FUNCTION SIMULATION** → Mentally apply user's patch:\n"
         "   ```python\n"
         "   patched_function = apply_patch(BuggyFunction, user_patch)\n"
         "   ```\n"
         "   - Verify syntactic correctness\n"
         "   - Detect hidden side effects\n\n"
         "### EVALUATION PHASE (When patches received, do for each patch)\n"
         "3. **CHANGE-CENTRIC EDGE CASE IDENTIFICATION**\n"
         "   - Map all modified code regions in the patch\n"
         "   - For each modified region:\n"
         "     ```mermaid\n"
         "     graph TD\n"
         "         A[Modified Code] --> B{Control Flow Change?}\n"
         "         B -->|Yes| C[Identify new branch conditions]\n"
         "         B -->|No| D[Check data flow alterations]\n"
         "         C --> E[Derive boundary values for new conditions]\n"
         "         D --> F[Track variable value propagation]\n"
         "         E --> G[Generate edge test cases]\n"
         "         F --> G\n"
         "     ```\n\n"
         "4. **DELTA-ORIENTED EQUIVALENCE CHECKING**\n"
         "   - Pre-defect behavior (reconstructed): Baseline\n"
         "   - Patch-impacted behavior: Target\n"
         "   - **Critical comparison points**:\n"
         "     | Comparison Dimension       | Pre-Defect | Post-Patch | Delta Analysis |\n"
         "     |-----------------------------|------------|------------|----------------|\n"
         "     | **Core input mappings**     | yes        | yes        | N/A            |\n"
         "     | **Boundary value handling** |            |            | Patch-specific |\n"
         "     | **Error propagation**       |            |            | Change-impact  |\n\n"
         "### SCORING MODEL\n"
         "5. **BEHAVIORAL EQUIVALENCE SCORING** → Evaluate similarity on:\n"
         "   | Dimension            | Weight | Evaluation Method                                  |\n"
         "   |----------------------|--------|----------------------------------------------------|\n"
         "   | Core Functionality   | 20%    | Historical vs patched boundary behavior comparison |\n"
         "   | Edge Case Handling   | 50%    | Patch-specific edge case detection                 |\n"
         "   | Error Behavior       | 30%    | Per modified code region analysis                  |\n\n"
         "6. **Confidence Formula**: \n"
         "   ```\n"
         "   confidence = (0.2 * core_score) + \n"
         "                (0.5 * edge_case_score) + \n"
         "                (0.3 * error_behavior_score)\n"
         "   ```\n\n"
         "7. **Behavioral Coverage Metrics**:\n"
         "   - `core`: Functionality similarity (e.g., \"true\"→true)\n"
         "   - `edge_cases`: Patch-specific edge case detection (e.g., \"zEs\")\n"
         "   - `error_behavior`: Per modified code region analysis (e.g., null, \"undefined\")\n\n"
         "### OUTPUT SPECIFICATION\n"
         "```json\n"
         "{\n"
         # "  \"patch-name\":{\n"
         "    \"confidence\": 0.92,\n"
         "    \"behavioral_coverage\": {\n"
         "    \"core\": 1.0,\n"
         "    \"edge_cases\": 0.8,\n"
         "    \"error_behavior\": 0.9\n"
         "    },\n"
         "    \"explanation\": \"Patch restores case-insensitive comparison but misses null safety improvement in pre-defect version\"\n"
         # "  },\n"
         "}\n"
         "```\n\n"
         "### SCORING GUIDELINES\n"
         "- **Strict Prohibitions**:\n"
         "  ❌ No natural language outside JSON\n"
         "  ❌ No code suggestions\n"
         "  ❌ No external references\n\n"
         "### CONTEXTUAL CONSTRAINTS\n"
         "- Remember `Inducing Changes` introduced defects, they didn't fix them\n"
         "- User patches will be provided in subsequent messages\n\n")

deepseek_r1_apca = ("You are a senior software review expert specialized in patch correctness analysis. "
                    "Your task is to evaluate user-provided patches against buggy functions using the following protocol:\n\n"
                    "### ANALYSIS PHASE (Pre-patch)\n"
                    "1. **DEFECT INDUCTION ANALYSIS** → Study `Inducing Changes` to determine:\n"
                    "   - How the defect was introduced\n"
                    "   - Pre-defect behavior of the function\n"
                    "2. **BUGGY FUNCTION DECOMPOSITION** → Analyze `Buggy Function` to identify:\n"
                    "   - Missing/incomplete functionality\n"
                    "   - Incorrect logic flows\n"
                    "   - Boundary condition failures\n\n"
                    "### EVALUATION PHASE (When patch received)\n"
                    "3. **PATCH VERIFICATION** → For each user-provided patch:\n"
                    "   a. Compare with `Inducing Changes` to detect inverse modifications\n"
                    "   b. Validate against pre-defect behavior requirements\n"
                    "   c. Check for regression risks and edge case coverage\n\n"
                    "### OUTPUT REQUIREMENTS\n"
                    "- **Primary Response**: JSON object with structure:\n"
                    "  ```json\n"
                    "  {\n"
                    "    \"confidence\": 0.85,  // Float [0.0-1.0]\n"
                    "    \"explanation\": \"Concise technical rationale\"  // Optional\n"
                    "  }\n"
                    "  ```\n"
                    "- **Confidence Scoring Guidelines**:\n"
                    "  | Score Range | Meaning                     |\n"
                    "  |-------------|-----------------------------|\n"
                    "  | 0.0-0.3     | Likely incorrect           |\n"
                    "  | 0.4-0.6     | Partial/uncertain solution |\n"
                    "  | 0.7-0.9     | Probable fix               |\n"
                    "  | 1.0         | Definite correction        |\n"
                    "- **Strict Prohibitions**:\n"
                    "  ❌ No natural language outside JSON\n"
                    "  ❌ No code suggestions\n"
                    "  ❌ No external references\n\n"
                    "### CONTEXTUAL CONSTRAINTS\n"
                    "- Remember `Inducing Changes` introduced defects, they didn't fix them\n"
                    "- User patches will be provided in subsequent messages\n"
                    "- Current function state: Buggy (see below)\n\n"
                    "### ACTIVE CONTEXT\n"
                    "```java\n"
                    "// BUGGY FUNCTION (DO NOT FIX YET)\n"
                    "public static boolean toBoolean(String str) {\n"
                    "  if (str == \"true\") return true;  // Defect: reference equality\n"
                    "  if (str == null) return false;   // Instead of value equality\n"
                    "  // ... (case analysis with potential case 3 fall-through bug)\n"
                    "}\n"
                    "```\n"
                    "```diff\n"
                    "// INDUCING CHANGES (DEFECT SOURCE)\n"
                    "- if (\"true\".equalsIgnoreCase(str)) { ... }\n"
                    "+ if (str == \"true\") { ... }  // Introduced reference comparison defect\n"
                    "```")


deepseek_r1_test_generation = ("You are an expert in software testing. " 
                                "Your task is to analyze structured input and generat valid test values for target variables by executing the following procedure:\n\n"
                                "1. **TARGET IDENTIFICATION** → Extract the target variable from the attribute `[Variables]` of json input\n"
                                "2. **DATAFLOW RESOLUTION** → Parse all variable declarations in attribute `[DataFlows]` of json input and establish dependencies\n"
                                "3. **CONSTRAINT ANALYSIS** → Process each constraint in attribute `[Constraints]`of json input to considering:\n"
                                "   - Direct variable constraints\n"
                                "   - Derived constraints through dataflow relationships\n"
                                "   - Negation semantics (! operator)\n"
                                "4. **Analyze Defective Function If not Absent** → Study the program `[Buggy Function]` semantics containing the constraint context\n"
                                "5. **VALUE GENERATION** → Compute possible values satisfying ALL constraints with these rules:\n"
                                "   - Generate ≤50 representative values\n"
                                "   - Prioritize edge cases and boundary values\n"
                                "   - Exclude values violating any constraint\n\n"
                                "**Output Requirements**:\n"
                                "- Strictly use JSON format: {\"<variable>\": [value1, value2, ...]}\n"
                                "- Omit all explanations, intermediate results, and non-JSON content\n"
                                "- For unsolvable constraints: return empty list (e.g., {\"str\": []})\n\n")


lang51_apca3 = """
{
    "Buggy Function": "    public static boolean toBoolean(String str) {\n        // Previously used equalsIgnoreCase, which was fast for interned 'true'.\n        // Non interned 'true' matched 15 times slower.\n        // \n        // Optimisation provides same performance as before for interned 'true'.\n        // Similar performance for null, 'false', and other strings not length 2/3/4.\n        // 'true'/'TRUE' match 4 times slower, 'tRUE'/'True' 7 times slower.\n        if (str == \"true\") {\n            return true;\n        }\n        if (str == null) {\n            return false;\n        }\n        switch (str.length()) {\n            case 2: {\n                char ch0 = str.charAt(0);\n                char ch1 = str.charAt(1);\n                return \n                    (ch0 == 'o' || ch0 == 'O') &&\n                    (ch1 == 'n' || ch1 == 'N');\n            }\n            case 3: {\n                char ch = str.charAt(0);\n                if (ch == 'y') {\n                    return \n                        (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n                        (str.charAt(2) == 's' || str.charAt(2) == 'S');\n                }\n                if (ch == 'Y') {\n                    return \n                        (str.charAt(1) == 'E' || str.charAt(1) == 'e') &&\n                        (str.charAt(2) == 'S' || str.charAt(2) == 's');\n                }\n            }\n            case 4: {\n                char ch = str.charAt(0);\n                if (ch == 't') {\n                    return \n                        (str.charAt(1) == 'r' || str.charAt(1) == 'R') &&\n                        (str.charAt(2) == 'u' || str.charAt(2) == 'U') &&\n                        (str.charAt(3) == 'e' || str.charAt(3) == 'E');\n                }\n                if (ch == 'T') {\n                    return \n                        (str.charAt(1) == 'R' || str.charAt(1) == 'r') &&\n                        (str.charAt(2) == 'U' || str.charAt(2) == 'u') &&\n                        (str.charAt(3) == 'E' || str.charAt(3) == 'e');\n                }\n            }\n        }\n        return false;\n    }",
    "Inducing Changes": "diff --git a/src/java/org/apache/commons/lang/BooleanUtils.java b/src/java/org/apache/commons/lang/BooleanUtils.java\nindex 4b2a06f..14b1607 100644\n--- a/src/java/org/apache/commons/lang/BooleanUtils.java\n+++ b/src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -66,7 +66,7 @@\n  * @author Matthew Hawthorne\n  * @author Gary Gregory\n  * @since 2.0\n- * @version $Id: BooleanUtils.java,v 1.16 2003/09/23 19:45:14 fredrik Exp $\n+ * @version $Id: BooleanUtils.java,v 1.17 2003/10/21 23:23:06 scolebourne Exp $\n  */\n public class BooleanUtils {\n \n@@ -502,12 +502,14 @@\n      * Otherwise, <code>null</code> is returned.</p>\n      *\n      * <pre>\n+     *   BooleanUtils.toBooleanObject(null)    = null\n      *   BooleanUtils.toBooleanObject(\"true\")  = Boolean.TRUE\n      *   BooleanUtils.toBooleanObject(\"false\") = Boolean.FALSE\n      *   BooleanUtils.toBooleanObject(\"on\")    = Boolean.TRUE\n      *   BooleanUtils.toBooleanObject(\"ON\")    = Boolean.TRUE\n      *   BooleanUtils.toBooleanObject(\"off\")   = Boolean.FALSE\n      *   BooleanUtils.toBooleanObject(\"oFf\")   = Boolean.FALSE\n+     *   BooleanUtils.toBooleanObject(\"blue\")  = null\n      * </pre>\n      *\n      * @param str  the String to check\n@@ -574,34 +576,94 @@\n     // String to boolean methods\n     //-----------------------------------------------------------------------\n     /**\n-     * <p>Converts a String to a boolean.</p>\n+     * <p>Converts a String to a boolean (optimised for performance).</p>\n      * \n      * <p><code>'true'</code>, <code>'on'</code> or <code>'yes'</code>\n      * (case insensitive) will return <code>true</code>. Otherwise,\n      * <code>false</code> is returned.</p>\n+     * \n+     * <p>This method performs 4 times faster (JDK1.4) than\n+     * <code>Boolean.valueOf(String)</code>. However, this method accepts\n+     * 'on' and 'yes' as true values.\n      *\n      * <pre>\n+     *   BooleanUtils.toBoolean(null)    = false\n      *   BooleanUtils.toBoolean(\"true\")  = true\n+     *   BooleanUtils.toBoolean(\"TRUE\")  = true\n+     *   BooleanUtils.toBoolean(\"tRUe\")  = true\n      *   BooleanUtils.toBoolean(\"on\")    = true\n      *   BooleanUtils.toBoolean(\"yes\")   = true\n      *   BooleanUtils.toBoolean(\"false\") = false\n+     *   BooleanUtils.toBoolean(\"x gti\") = false\n      * </pre>\n      *\n      * @param str  the String to check\n      * @return the boolean value of the string, <code>false</code> if no match\n      */\n     public static boolean toBoolean(String str) {\n-        if (\"true\".equalsIgnoreCase(str)) {\n-            return true;\n-        } else if (\"on\".equalsIgnoreCase(str)) {\n-            return true;\n-        } else if (\"yes\".equalsIgnoreCase(str)) {\n+        // Previously used equalsIgnoreCase, which was fast for interned 'true'.\n+        // Non interned 'true' matched 15 times slower.\n+        // \n+        // Optimisation provides same performance as before for interned 'true'.\n+        // Similar performance for null, 'false', and other strings not length 2/3/4.\n+        // 'true'/'TRUE' match 4 times slower, 'tRUE'/'True' 7 times slower.\n+        if (str == \"true\") {\n             return true;\n         }\n-        // no match\n+        if (str == null) {\n+            return false;\n+        }\n+        switch (str.length()) {\n+            case 2: {\n+                char ch0 = str.charAt(0);\n+                char ch1 = str.charAt(1);\n+                return \n+                    (ch0 == 'o' || ch0 == 'O') &&\n+                    (ch1 == 'n' || ch1 == 'N');\n+            }\n+            case 3: {\n+                char ch = str.charAt(0);\n+                if (ch == 'y') {\n+                    return \n+                        (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n+                        (str.charAt(2) == 's' || str.charAt(2) == 'S');\n+                }\n+                if (ch == 'Y') {\n+                    return \n+                        (str.charAt(1) == 'E' || str.charAt(1) == 'e') &&\n+                        (str.charAt(2) == 'S' || str.charAt(2) == 's');\n+                }\n+            }\n+            case 4: {\n+                char ch = str.charAt(0);\n+                if (ch == 't') {\n+                    return \n+                        (str.charAt(1) == 'r' || str.charAt(1) == 'R') &&\n+                        (str.charAt(2) == 'u' || str.charAt(2) == 'U') &&\n+                        (str.charAt(3) == 'e' || str.charAt(3) == 'E');\n+                }\n+                if (ch == 'T') {\n+                    return \n+                        (str.charAt(1) == 'R' || str.charAt(1) == 'r') &&\n+                        (str.charAt(2) == 'U' || str.charAt(2) == 'u') &&\n+                        (str.charAt(3) == 'E' || str.charAt(3) == 'e');\n+                }\n+            }\n+        }\n         return false;\n     }\n-\n+    \n+//    public static void main(String[] args) {\n+//        long start = System.currentTimeMillis();\n+//        boolean flag = true;\n+//        int count = 0;\n+//        for (int i = 0; i < 100000000; i++) {\n+//            flag = toBoolean(\"YES\");\n+//        }\n+//        long end = System.currentTimeMillis();\n+//        System.out.println((end - start) + \" \" + flag + \" \" + count);\n+//    }\n+    \n     /**\n      * <p>Converts a String to a Boolean throwing an exception if no match found.</p>\n      * \n\n",
    "User Patches": {
        "patch1-Lang-51-AVATAR-plausible.patch": "--- /src/java/org/apache/commons/lang/BooleanUtils.java\n+++ /src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -674,11 +674,9 @@\n                         (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n                         (str.charAt(2) == 's' || str.charAt(2) == 'S');\n                 }\n-                if (ch == 'Y') {\n-                    return \n+                return \n                         (str.charAt(1) == 'E' || str.charAt(1) == 'e') &&\n                         (str.charAt(2) == 'S' || str.charAt(2) == 's');\n-                }\n             }\n             case 4: {\n                 char ch = str.charAt(0);\n\n",
        "patch1-Lang-51-DynaMoth-plausible.patch": "--- /src/java/org/apache/commons/lang/BooleanUtils.java\n+++ /src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -671,6 +671,6 @@\n                 char ch = str.charAt(0);\n-                if (ch == 'y') {\n-                    return \n-                        (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n-                        (str.charAt(2) == 's' || str.charAt(2) == 'S');\n+                if (true) {\n+                    return\n+                    (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n+                    (str.charAt(2) == 's' || str.charAt(2) == 'S');\n                 }\n\n",
        "patch1-Lang-51-kPAR-plausible.patch": "--- /src/java/org/apache/commons/lang/BooleanUtils.java\n+++ /src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -669,7 +669,7 @@\n             }\n             case 3: {\n                 char ch = str.charAt(0);\n-                if (ch == 'y') {\n+                if ((ch == 'y') || !(ch == 'Y')) {\n                     return \n                         (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n                         (str.charAt(2) == 's' || str.charAt(2) == 'S');\n\n",
        "patch1-Lang-51-Nopol-plausible.patch": "--- /src/java/org/apache/commons/lang/BooleanUtils.java\n+++ /src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -671,6 +671,6 @@\n                 char ch = str.charAt(0);\n-                if (ch == 'y') {\n-                    return \n-                        (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n-                        (str.charAt(2) == 's' || str.charAt(2) == 'S');\n+                if (str!=null) {\n+                    return\n+                    (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n+                    (str.charAt(2) == 's' || str.charAt(2) == 'S');\n                 }\n\n",
        "patch1-Lang-51-TBar-plausible.patch": "--- /src/java/org/apache/commons/lang/BooleanUtils.java\n+++ /src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -669,7 +669,7 @@\n             }\n             case 3: {\n                 char ch = str.charAt(0);\n-                if (ch == 'y') {\n+                if (ch<='y') {\n                     return \n                         (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n                         (str.charAt(2) == 's' || str.charAt(2) == 'S');\n\n"
    }
}
"""

closure_73_correct = """
{
    "Buggy Function": "  static String strEscape(String s, char quote,\n                          String doublequoteEscape,\n                          String singlequoteEscape,\n                          String backslashEscape,\n                          CharsetEncoder outputCharsetEncoder) {\n    StringBuilder sb = new StringBuilder(s.length() + 2);\n    sb.append(quote);\n    for (int i = 0; i < s.length(); i++) {\n      char c = s.charAt(i);\n      switch (c) {\n        case '\\0': sb.append(\"\\\\0\"); break;\n        case '\\n': sb.append(\"\\\\n\"); break;\n        case '\\r': sb.append(\"\\\\r\"); break;\n        case '\\t': sb.append(\"\\\\t\"); break;\n        case '\\\\': sb.append(backslashEscape); break;\n        case '\\\"': sb.append(doublequoteEscape); break;\n        case '\\'': sb.append(singlequoteEscape); break;\n        case '>':                       // Break --> into --\\> or ]]> into ]]\\>\n          if (i >= 2 &&\n              ((s.charAt(i - 1) == '-' && s.charAt(i - 2) == '-') ||\n               (s.charAt(i - 1) == ']' && s.charAt(i - 2) == ']'))) {\n            sb.append(\"\\\\>\");\n          } else {\n            sb.append(c);\n          }\n          break;\n        case '<':\n          // Break </script into <\\/script\n          final String END_SCRIPT = \"/script\";\n\n          // Break <!-- into <\\!--\n          final String START_COMMENT = \"!--\";\n\n          if (s.regionMatches(true, i + 1, END_SCRIPT, 0,\n                              END_SCRIPT.length())) {\n            sb.append(\"<\\\\\");\n          } else if (s.regionMatches(false, i + 1, START_COMMENT, 0,\n                                     START_COMMENT.length())) {\n            sb.append(\"<\\\\\");\n          } else {\n            sb.append(c);\n          }\n          break;\n        default:\n          // If we're given an outputCharsetEncoder, then check if the\n          //  character can be represented in this character set.\n          if (outputCharsetEncoder != null) {\n            if (outputCharsetEncoder.canEncode(c)) {\n              sb.append(c);\n            } else {\n              // Unicode-escape the character.\n              appendHexJavaScriptRepresentation(sb, c);\n            }\n          } else {\n            // No charsetEncoder provided - pass straight latin characters\n            // through, and escape the rest.  Doing the explicit character\n            // check is measurably faster than using the CharsetEncoder.\n            if (c > 0x1f && c <= 0x7f) {\n              sb.append(c);\n            } else {\n              // Other characters can be misinterpreted by some js parsers,\n              // or perhaps mangled by proxies along the way,\n              // so we play it safe and unicode escape them.\n              appendHexJavaScriptRepresentation(sb, c);\n            }\n          }\n      }\n    }\n    sb.append(quote);\n    return sb.toString();\n  }",
    "Inducing Changes": "diff --git a/src/com/google/javascript/jscomp/CodeGenerator.java b/src/com/google/javascript/jscomp/CodeGenerator.java\nindex d9496d7..3c97fc4 100644\n--- a/src/com/google/javascript/jscomp/CodeGenerator.java\n+++ b/src/com/google/javascript/jscomp/CodeGenerator.java\n@@ -16,12 +16,15 @@\n \n package com.google.javascript.jscomp;\n \n+import com.google.common.base.Charsets;\n import com.google.common.base.Preconditions;\n import com.google.common.base.StringUtil;\n import com.google.javascript.rhino.Node;\n import com.google.javascript.rhino.Token;\n import com.google.javascript.rhino.TokenStream;\n \n+import java.nio.charset.Charset;\n+import java.nio.charset.CharsetEncoder;\n \n /**\n  * CodeGenerator generates codes from a parse tree, sending it to the specified\n@@ -34,8 +37,23 @@\n \n   private final CodeConsumer cc;\n \n-  CodeGenerator(CodeConsumer consumer) {\n+  private final CharsetEncoder outputCharsetEncoder;\n+\n+  CodeGenerator(CodeConsumer consumer, Charset outputCharset) {\n     cc = consumer;\n+    if (outputCharset == null || outputCharset == Charsets.US_ASCII) {\n+      // If we want our default (pretending to be UTF-8, but escaping anything\n+      // outside of straight ASCII), then don't use the encoder, but\n+      // just special-case the code.  This keeps the normal path through\n+      // the code identical to how it's been for years.\n+      this.outputCharsetEncoder = null;\n+    } else {\n+      this.outputCharsetEncoder = outputCharset.newEncoder();\n+    }\n+  }\n+\n+  CodeGenerator(CodeConsumer consumer) {\n+    this(consumer, null);\n   }\n \n   void add(String str) {\n@@ -221,7 +239,7 @@\n           throw new Error(\"Expected children to be strings\");\n         }\n \n-        String regexp = regexpEscape(first.getString());\n+        String regexp = regexpEscape(first.getString(), outputCharsetEncoder);\n \n         // I only use one .add because whitespace matters\n         if (childCount == 2) {\n@@ -495,7 +513,7 @@\n \n       case Token.STRING:\n         Preconditions.checkState(childCount == 0);\n-        add(jsString(n.getString()));\n+        add(jsString(n.getString(), outputCharsetEncoder));\n         break;\n \n       case Token.DELPROP:\n@@ -730,7 +748,7 @@\n   }\n \n   /** Outputs a js string, using the optimal (single/double) quote character */\n-  static String jsString(String s) {\n+  static String jsString(String s, CharsetEncoder outputCharsetEncoder) {\n     int singleq = 0, doubleq = 0;\n \n     // could count the quotes and pick the optimal quote character\n@@ -755,19 +773,28 @@\n       singlequote = \"\\'\";\n     }\n \n-    return strEscape(s, quote, doublequote, singlequote, \"\\\\\\\\\");\n+    return strEscape(s, quote, doublequote, singlequote, \"\\\\\\\\\",\n+        outputCharsetEncoder);\n   }\n \n   /** Escapes regular expression */\n+  static String regexpEscape(String s, CharsetEncoder outputCharsetEncoder) {\n+    return strEscape(s, '/', \"\\\"\", \"'\", \"\\\\\", outputCharsetEncoder);\n+  }\n+\n+  /* If the user doesn't want to specify an output charset encoder, assume\n+     they want Latin/ASCII characters only.\n+   */\n   static String regexpEscape(String s) {\n-    return strEscape(s, '/', \"\\\"\", \"'\", \"\\\\\");\n+    return regexpEscape(s, null);\n   }\n \n   /** Helper to escape javascript string as well as regular expression */\n   static String strEscape(String s, char quote,\n                           String doublequoteEscape,\n                           String singlequoteEscape,\n-                          String backslashEscape) {\n+                          String backslashEscape,\n+                          CharsetEncoder outputCharsetEncoder) {\n     StringBuilder sb = new StringBuilder();\n     sb.append(quote);\n     for (int i = 0; i < s.length(); i++) {\n@@ -798,15 +825,27 @@\n           }\n           break;\n         default:\n-          // Please keep in sync with the same code in identifierEscape().\n-          if (c > 0x1F && c < 0x7F) {\n-            // Non-control ASCII characters are safe to transmit\n-            sb.append(c);\n+          // If we're given an outputCharsetEncoder, then check if the\n+          //  character can be represented in this character set.\n+          if (outputCharsetEncoder != null) {\n+            if (outputCharsetEncoder.canEncode(c)) {\n+              sb.append(c);\n+            } else {\n+              // Unicode-escape the character.\n+              StringUtil.appendHexJavaScriptRepresentation(sb, c);\n+            }\n           } else {\n-            // Other characters can be misinterpreted by some js parsers,\n-            // or perhaps mangled by proxies along the way,\n-            // so we play it safe and unicode escape them.\n-            StringUtil.appendHexJavaScriptRepresentation(sb, c);\n+            // No charsetEncoder provided - pass straight latin characters\n+            // through, and escape the rest.  Doing the explicit character\n+            // check is measurably faster than using the CharsetEncoder.\n+            if (c > 0x1f && c <= 0x7f) {\n+              sb.append(c);\n+            } else {\n+              // Other characters can be misinterpreted by some js parsers,\n+              // or perhaps mangled by proxies along the way,\n+              // so we play it safe and unicode escape them.\n+              StringUtil.appendHexJavaScriptRepresentation(sb, c);\n+            }\n           }\n       }\n     }\n@@ -824,7 +863,9 @@\n     StringBuilder sb = new StringBuilder();\n     for (int i = 0; i < s.length(); i++) {\n       char c = s.charAt(i);\n-      // See comments for the same code in strEscape(). Please keep in sync.\n+      // Identifiers should always go to Latin1/ ASCII characters because\n+      // different browser's rules for valid identifier characters are\n+      // crazy.\n       if (c > 0x1F && c < 0x7F) {\n         sb.append(c);\n       } else {\n\n",
    "Trigger tests": [
        {
            "exception_info": "--- com.google.javascript.jscomp.CodePrinterTest::testUnicode_purify_3\n\njunit.framework.ComparisonFailure: expected:<var x=\"[\\u007f]\"> but was:<var x=\"[\u007f]\">\n\n\tat junit.framework.Assert.assertEquals(Assert.java:100)\n\n\tat junit.framework.Assert.assertEquals(Assert.java:107)\n\n\tat junit.framework.TestCase.assertEquals(TestCase.java:269)\n\n\tat com.google.javascript.jscomp.CodePrinterTest.assertPrint(CodePrinterTest.java:300)\n\n\tat com.google.javascript.jscomp.CodePrinterTest.testUnicode_purify_3(CodePrinterTest.java:1267)\n\n\tat sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n\n\tat sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)\n\n\tat sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)\n",
            "test_function": "public void testUnicode_purify_3(){\n    assertPrint(\"var x ='\\\\x7f';\",\"var x=\\\"\\\\u007f\\\"\");\n  }"
        }
    ],
    "User Patches": {
        "Closure_73.patch": "--- /src/com/google/javascript/jscomp/CodeGenerator.java\n+++ /src/com/google/javascript/jscomp/CodeGenerator.java\n@@ -1042,7 +1042,7 @@\n             // No charsetEncoder provided - pass straight latin characters\n             // through, and escape the rest.  Doing the explicit character\n             // check is measurably faster than using the CharsetEncoder.\n-            if (c > 0x1f && c <= 0x7f) {\n+            if (c > 0x1f && c < 0x7f) {\n               sb.append(c);\n             } else {\n               // Other characters can be misinterpreted by some js parsers,\n\n"
    }
}
"""

codec_4_correct = """
{
    "Buggy Function": "    public Base64() {\n        this(false);\n    }",
    "Inducing Changes": "diff --git a/src/java/org/apache/commons/codec/binary/Base64.java b/src/java/org/apache/commons/codec/binary/Base64.java\nindex b85f9f4..eb09b5c 100644\n--- a/src/java/org/apache/commons/codec/binary/Base64.java\n+++ b/src/java/org/apache/commons/codec/binary/Base64.java\n@@ -254,7 +254,7 @@\n      * \u003c/p\u003e\n      * \n      * @param lineLength\n-     *            Each line of encoded data will be at most of the given length (rounded up to nearest multiple of 4).\n+     *            Each line of encoded data will be at most of the given length (rounded down to nearest multiple of 4).\n      *            If lineLength \u003c\u003d 0, then the output will not be divided into lines (chunks). Ignored when decoding.\n      * @since 1.4\n      */\n@@ -276,7 +276,7 @@\n      * \u003c/p\u003e\n      * \n      * @param lineLength\n-     *            Each line of encoded data will be at most of the given length (rounded up to nearest multiple of 4).\n+     *            Each line of encoded data will be at most of the given length (rounded down to nearest multiple of 4).\n      *            If lineLength \u003c\u003d 0, then the output will not be divided into lines (chunks). Ignored when decoding.\n      * @param lineSeparator\n      *            Each line of encoded data will end with this sequence of bytes.\n@@ -302,7 +302,7 @@\n      * \u003c/p\u003e\n      * \n      * @param lineLength\n-     *            Each line of encoded data will be at most of the given length (rounded up to nearest multiple of 4).\n+     *            Each line of encoded data will be at most of the given length (rounded down to nearest multiple of 4).\n      *            If lineLength \u003c\u003d 0, then the output will not be divided into lines (chunks). Ignored when decoding.\n      * @param lineSeparator\n      *            Each line of encoded data will end with this sequence of bytes.\n@@ -314,7 +314,7 @@\n      * @since 1.4\n      */\n     public Base64(int lineLength, byte[] lineSeparator, boolean urlSafe) {\n-        this.lineLength \u003d lineLength;\n+        this.lineLength \u003d lineLength \u003e 0 ? (lineLength / 4) * 4 : 0;\n         this.lineSeparator \u003d new byte[lineSeparator.length];\n         System.arraycopy(lineSeparator, 0, this.lineSeparator, 0, lineSeparator.length);\n         if (lineLength \u003e 0) {\n@@ -324,7 +324,7 @@\n         }\n         this.decodeSize \u003d this.encodeSize - 1;\n         if (containsBase64Byte(lineSeparator)) {\n-            String sep \u003d StringBytesUtils.newStringUtf8(lineSeparator);\n+            String sep \u003d StringUtils.newStringUtf8(lineSeparator);\n             throw new IllegalArgumentException(\"lineSeperator must not contain base64 characters: [\" + sep + \"]\");\n         }\n         this.encodeTable \u003d urlSafe ? URL_SAFE_ENCODE_TABLE : STANDARD_ENCODE_TABLE;\n@@ -669,10 +669,11 @@\n      *             if the parameter supplied is not of type byte[]\n      */\n     public Object decode(Object pObject) throws DecoderException {\n-        if (!(pObject instanceof byte[])) {\n+        if (pObject instanceof byte[]) {\n+            return decode((byte[]) pObject);\n+        } else {\n             throw new DecoderException(\"Parameter supplied to Base64 decode is not a byte[]\");\n         }\n-        return decode((byte[]) pObject);\n     }\n \n     /**\n@@ -683,7 +684,24 @@\n      * @return a byte array containing binary data\n      */\n     public byte[] decode(byte[] pArray) {\n-        return decodeBase64(pArray);\n+        if (pArray \u003d\u003d null || pArray.length \u003d\u003d 0) {\n+            return pArray;\n+        }\n+        long len \u003d (pArray.length * 3) / 4;\n+        byte[] buf \u003d new byte[(int) len];\n+        setInitialBuffer(buf, 0, buf.length);\n+        decode(pArray, 0, pArray.length);\n+        decode(pArray, 0, -1); // Notify decoder of EOF.\n+\n+        // Would be nice to just return buf (like we sometimes do in the encode\n+        // logic), but we have no idea what the line-length was (could even be\n+        // variable).  So we cannot determine ahead of time exactly how big an\n+        // array is necessary.  Hence the need to construct a 2nd byte array to\n+        // hold the final result:\n+\n+        byte[] result \u003d new byte[pos];\n+        readResults(result, 0, result.length);\n+        return result;\n     }\n \n     /**\n@@ -739,41 +757,17 @@\n         if (binaryData \u003d\u003d null || binaryData.length \u003d\u003d 0) {\n             return binaryData;\n         }\n-        Base64 b64 \u003d isChunked ? new Base64(urlSafe) : new Base64(0, CHUNK_SEPARATOR, urlSafe);\n-        long len \u003d (binaryData.length * 4) / 3;\n-        long mod \u003d len % 4;\n-        if (mod !\u003d 0) {\n-            len +\u003d 4 - mod;\n-        }\n-        if (isChunked) {\n-            boolean lenChunksPerfectly \u003d len % CHUNK_SIZE \u003d\u003d 0;\n-            len +\u003d (len / CHUNK_SIZE) * CHUNK_SEPARATOR.length;\n-            if (!lenChunksPerfectly) {\n-                len +\u003d CHUNK_SEPARATOR.length;\n-            }\n-        }\n+\n+        long len \u003d getEncodeLength(binaryData, CHUNK_SIZE, CHUNK_SEPARATOR);\n         if (len \u003e maxResultSize) {\n             throw new IllegalArgumentException(\"Input array too big, the output array would be bigger (\" +\n                 len +\n                 \") than the specified maxium size of \" +\n                 maxResultSize);\n         }\n-        byte[] buf \u003d new byte[(int) len];\n-        b64.setInitialBuffer(buf, 0, buf.length);\n-        b64.encode(binaryData, 0, binaryData.length);\n-        b64.encode(binaryData, 0, -1); // Notify encoder of EOF.\n-        // Encoder might have resized, even though it was unnecessary.\n-        if (b64.buffer !\u003d buf) {\n-            b64.readResults(buf, 0, buf.length);\n-        }\n-        // In URL-SAFE mode we skip the padding characters, so sometimes our\n-        // final length is a bit smaller.\n-        if (urlSafe \u0026\u0026 b64.pos \u003c buf.length) {\n-            byte[] smallerBuf \u003d new byte[b64.pos];\n-            System.arraycopy(buf, 0, smallerBuf, 0, b64.pos);\n-            buf \u003d smallerBuf;\n-        }\n-        return buf;\n+                \n+        Base64 b64 \u003d isChunked ? new Base64(urlSafe) : new Base64(0, CHUNK_SEPARATOR, urlSafe);\n+        return b64.encode(binaryData);\n     }\n \n     /**\n@@ -784,20 +778,8 @@\n      * @return Array containing decoded data.\n      */\n     public static byte[] decodeBase64(byte[] base64Data) {\n-        if (base64Data \u003d\u003d null || base64Data.length \u003d\u003d 0) {\n-            return base64Data;\n-        }\n         Base64 b64 \u003d new Base64();\n-        long len \u003d (base64Data.length * 3) / 4;\n-        byte[] buf \u003d new byte[(int) len];\n-        b64.setInitialBuffer(buf, 0, buf.length);\n-        b64.decode(base64Data, 0, base64Data.length);\n-        b64.decode(base64Data, 0, -1); // Notify decoder of EOF.\n-        // We have no idea what the line-length was, so we\n-        // cannot know how much of our array wasn\u0027t used.\n-        byte[] result \u003d new byte[b64.pos];\n-        b64.readResults(result, 0, result.length);\n-        return result;\n+        return b64.decode(base64Data);\n     }\n \n     /**\n@@ -873,7 +855,53 @@\n      * @return A byte array containing only Base64 character data\n      */\n     public byte[] encode(byte[] pArray) {\n-        return encodeBase64(pArray, false, isUrlSafe());\n+        long len \u003d getEncodeLength(pArray, lineLength, lineSeparator);\n+        byte[] buf \u003d new byte[(int) len];\n+        setInitialBuffer(buf, 0, buf.length);\n+        encode(pArray, 0, pArray.length);\n+        encode(pArray, 0, -1); // Notify encoder of EOF.\n+        // Encoder might have resized, even though it was unnecessary.\n+        if (buffer !\u003d buf) {\n+            readResults(buf, 0, buf.length);\n+        }\n+        // In URL-SAFE mode we skip the padding characters, so sometimes our\n+        // final length is a bit smaller.\n+        if (isUrlSafe() \u0026\u0026 pos \u003c buf.length) {\n+            byte[] smallerBuf \u003d new byte[pos];\n+            System.arraycopy(buf, 0, smallerBuf, 0, pos);\n+            buf \u003d smallerBuf;\n+        }\n+        return buf;        \n+    }\n+\n+    /**\n+     * Pre-calculates the amount of space needed to base64-encode the supplied array.\n+     *\n+     * @param pArray byte[] array which will later be encoded\n+     * @param chunkSize line-length of the output (\u003c\u003d 0 means no chunking) between each\n+     *        chunkSeparator (e.g. CRLF).\n+     * @param chunkSeparator the sequence of bytes used to separate chunks of output (e.g. CRLF).\n+     *\n+     * @return amount of space needed to encoded the supplied array.  Returns\n+     *         a long since a max-len array will require Integer.MAX_VALUE + 33%.\n+     */\n+    private static long getEncodeLength(byte[] pArray, int chunkSize, byte[] chunkSeparator) {\n+        // base64 always encodes to multiples of 4.\n+        chunkSize \u003d (chunkSize / 4) * 4;\n+\n+        long len \u003d (pArray.length * 4) / 3;\n+        long mod \u003d len % 4;\n+        if (mod !\u003d 0) {\n+            len +\u003d 4 - mod;\n+        }\n+        if (chunkSize \u003e 0 \u0026\u0026 chunkSeparator !\u003d null) {\n+            boolean lenChunksPerfectly \u003d len % chunkSize \u003d\u003d 0;\n+            len +\u003d (len / chunkSize) * chunkSeparator.length;\n+            if (!lenChunksPerfectly) {\n+                len +\u003d chunkSeparator.length;\n+            }\n+        }\n+        return len;\n     }\n \n     // Implementation of integer encoding used for crypto\n",
    "User Patches": {
        "Codec_4.patch": "--- /src/java/org/apache/commons/codec/binary/Base64.java\n+++ /src/java/org/apache/commons/codec/binary/Base64.java\n@@ -222,7 +222,7 @@\n      * </p>\n      */\n     public Base64() {\n-        this(false);\n+        this(0);\n     }\n \n     /**\n\n"
    }
}
"""

jsoup_43_correct = """
{
    "Buggy Function": "    private static <E extends Element> Integer indexInList(Element search, List<E> elements) {\n        Validate.notNull(search);\n        Validate.notNull(elements);\n\n        for (int i = 0; i < elements.size(); i++) {\n            E element = elements.get(i);\n            if (element.equals(search))\n                return i;\n        }\n        return null;\n    }",
    "Inducing Changes": "diff --git a/src/main/java/org/jsoup/nodes/Element.java b/src/main/java/org/jsoup/nodes/Element.java\nindex 3dfc0ff..c07018e 100644\n--- a/src/main/java/org/jsoup/nodes/Element.java\n+++ b/src/main/java/org/jsoup/nodes/Element.java\n@@ -267,7 +267,7 @@\n         // was - Node#addChildren(child). short-circuits an array create and a loop.\n         reparentChild(child);\n         childNodes.add(child);\n-        child.setSiblingIndex(childNodes.size()-1);\n+        child.setSiblingIndex(childNodes.size() - 1);\n         return this;\n     }\n \n@@ -1166,12 +1166,17 @@\n \n     @Override\n     public boolean equals(Object o) {\n-        return this == o;\n+        if (this == o) return true;\n+        if (o == null || getClass() != o.getClass()) return false;\n+        if (!super.equals(o)) return false;\n+\n+        Element element = (Element) o;\n+\n+        return tag.equals(element.tag);\n     }\n \n     @Override\n     public int hashCode() {\n-        // todo: fixup, not very useful\n         int result = super.hashCode();\n         result = 31 * result + (tag != null ? tag.hashCode() : 0);\n         return result;\n@@ -1179,7 +1184,6 @@\n \n     @Override\n     public Element clone() {\n-        Element clone = (Element) super.clone();\n-        return clone;\n+        return (Element) super.clone();\n     }\n }\n\n",
    "Trigger tests": [
        {
            "exception_info": "--- org.jsoup.nodes.ElementTest::testGetSiblingsWithDuplicateContent_purify_5\n\njunit.framework.AssertionFailedError: expected:<[]is> but was:<[th]is>\n\n\tat org.junit.Assert.assertEquals(Assert.java:115)\n\n\tat org.junit.Assert.assertEquals(Assert.java:144)\n\n\tat org.jsoup.nodes.ElementTest.testGetSiblingsWithDuplicateContent_purify_5(ElementTest.java:1664)\n\n\tat sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n\n\tat sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)\n\n\tat sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)\n\n\tat java.lang.reflect.Method.invoke(Method.java:498)\n\n\tat org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:47)\n",
            "test_function": "public void testGetSiblingsWithDuplicateContent_purify_5(){\n    Document doc=Jsoup.parse(\"<div><p>Hello<p id=1>there<p>this<p>this<p>is<p>an<p id=last>element</div>\");\n    Element p=doc.getElementById(\"1\");\n    assertEquals(\"is\",p.nextElementSibling().nextElementSibling().nextElementSibling().text());\n  }"
        }
    ],
    "User Patches": {
        "Jsoup_43.patch": "--- /src/main/java/org/jsoup/nodes/Element.java\n+++ /src/main/java/org/jsoup/nodes/Element.java\n@@ -571,7 +571,7 @@\n \n         for (int i = 0; i < elements.size(); i++) {\n             E element = elements.get(i);\n-            if (element.equals(search))\n+            if (element == search)\n                 return i;\n         }\n         return null;\n\n"
    }
}
"""
closure_125_arja = """
{
    "Buggy Function": "  private void visitNew(NodeTraversal t, Node n) {\n    Node constructor = n.getFirstChild();\n    JSType type = getJSType(constructor).restrictByNotNullOrUndefined();\n    if (type.isConstructor() || type.isEmptyType() || type.isUnknownType()) {\n      FunctionType fnType = type.toMaybeFunctionType();\n      if (fnType != null) {\n        visitParameterList(t, n, fnType);\n        ensureTyped(t, n, fnType.getInstanceType());\n      } else {\n        ensureTyped(t, n);\n      }\n    } else {\n      report(t, n, NOT_A_CONSTRUCTOR);\n      ensureTyped(t, n);\n    }\n  }",
    "Inducing Changes": "",
    "Trigger tests": [
        {
            "exception_info": "--- com.google.javascript.jscomp.TypeCheckTest::testIssue1002\n\njava.lang.IllegalStateException\n\n\tat com.google.common.base.Preconditions.checkState(Preconditions.java:133)\n\n\tat com.google.javascript.rhino.jstype.FunctionType.getInstanceType(FunctionType.java:891)\n\n\tat com.google.javascript.jscomp.TypeCheck.visitNew(TypeCheck.java:1462)\n\n\tat com.google.javascript.jscomp.TypeCheck.visit(TypeCheck.java:385)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:454)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:446)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:446)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:446)\n",
            "test_function": "public void testIssue1002() throws Exception {\n    testTypes(\"/** @interface */\" + \"var I = function() {}"
        }
    ],
    "User Patches": {
        "patch1-Closure-125-Arja-plausible.patch": "--- /src/com/google/javascript/jscomp/type/SemanticReverseAbstractInterpreter.java\n+++ /src/com/google/javascript/jscomp/type/SemanticReverseAbstractInterpreter.java\n@@ -200,7 +200,6 @@\n \n       case Token.SHEQ:\n         if (outcome) {\n-          return caseEquality(condition, blindScope, SHEQ);\n         } else {\n           return caseEquality(condition, blindScope, SHNE);\n         }\n\n"
    }
}
"""
closure_125_kali = """
{
    "Buggy Function": "  private void visitNew(NodeTraversal t, Node n) {\n    Node constructor = n.getFirstChild();\n    JSType type = getJSType(constructor).restrictByNotNullOrUndefined();\n    if (type.isConstructor() || type.isEmptyType() || type.isUnknownType()) {\n      FunctionType fnType = type.toMaybeFunctionType();\n      if (fnType != null) {\n        visitParameterList(t, n, fnType);\n        ensureTyped(t, n, fnType.getInstanceType());\n      } else {\n        ensureTyped(t, n);\n      }\n    } else {\n      report(t, n, NOT_A_CONSTRUCTOR);\n      ensureTyped(t, n);\n    }\n  }",
    "Inducing Changes": "",
    "Trigger tests": [
        {
            "exception_info": "--- com.google.javascript.jscomp.TypeCheckTest::testIssue1002\n\njava.lang.IllegalStateException\n\n\tat com.google.common.base.Preconditions.checkState(Preconditions.java:133)\n\n\tat com.google.javascript.rhino.jstype.FunctionType.getInstanceType(FunctionType.java:891)\n\n\tat com.google.javascript.jscomp.TypeCheck.visitNew(TypeCheck.java:1462)\n\n\tat com.google.javascript.jscomp.TypeCheck.visit(TypeCheck.java:385)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:454)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:446)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:446)\n\n\tat com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:446)\n",
            "test_function": "public void testIssue1002() throws Exception {\n    testTypes(\"/** @interface */\" + \"var I = function() {}"
        }
    ],
    "User Patches": {
        "patch1-Closure-125-Kali-plausible.patch": "--- /src/com/google/javascript/jscomp/type/SemanticReverseAbstractInterpreter.java\n+++ /src/com/google/javascript/jscomp/type/SemanticReverseAbstractInterpreter.java\n@@ -199,7 +199,7 @@\n         }\n \n       case Token.SHEQ:\n-        if (outcome) {\n+        if (false) {\n           return caseEquality(condition, blindScope, SHEQ);\n         } else {\n           return caseEquality(condition, blindScope, SHNE);\n\n"
    }
}
"""

lang_51_tbar = """
{
    "Buggy Function": "    public static boolean toBoolean(String str) {\n        // Previously used equalsIgnoreCase, which was fast for interned 'true'.\n        // Non interned 'true' matched 15 times slower.\n        // \n        // Optimisation provides same performance as before for interned 'true'.\n        // Similar performance for null, 'false', and other strings not length 2/3/4.\n        // 'true'/'TRUE' match 4 times slower, 'tRUE'/'True' 7 times slower.\n        if (str == \"true\") {\n            return true;\n        }\n        if (str == null) {\n            return false;\n        }\n        switch (str.length()) {\n            case 2: {\n                char ch0 = str.charAt(0);\n                char ch1 = str.charAt(1);\n                return \n                    (ch0 == 'o' || ch0 == 'O') &&\n                    (ch1 == 'n' || ch1 == 'N');\n            }\n            case 3: {\n                char ch = str.charAt(0);\n                if (ch == 'y') {\n                    return \n                        (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n                        (str.charAt(2) == 's' || str.charAt(2) == 'S');\n                }\n                if (ch == 'Y') {\n                    return \n                        (str.charAt(1) == 'E' || str.charAt(1) == 'e') &&\n                        (str.charAt(2) == 'S' || str.charAt(2) == 's');\n                }\n            }\n            case 4: {\n                char ch = str.charAt(0);\n                if (ch == 't') {\n                    return \n                        (str.charAt(1) == 'r' || str.charAt(1) == 'R') &&\n                        (str.charAt(2) == 'u' || str.charAt(2) == 'U') &&\n                        (str.charAt(3) == 'e' || str.charAt(3) == 'E');\n                }\n                if (ch == 'T') {\n                    return \n                        (str.charAt(1) == 'R' || str.charAt(1) == 'r') &&\n                        (str.charAt(2) == 'U' || str.charAt(2) == 'u') &&\n                        (str.charAt(3) == 'E' || str.charAt(3) == 'e');\n                }\n            }\n        }\n        return false;\n    }",
    "Inducing Changes": "diff --git a/src/java/org/apache/commons/lang/BooleanUtils.java b/src/java/org/apache/commons/lang/BooleanUtils.java\nindex 4b2a06f..14b1607 100644\n--- a/src/java/org/apache/commons/lang/BooleanUtils.java\n+++ b/src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -66,7 +66,7 @@\n  * @author Matthew Hawthorne\n  * @author Gary Gregory\n  * @since 2.0\n- * @version $Id: BooleanUtils.java,v 1.16 2003/09/23 19:45:14 fredrik Exp $\n+ * @version $Id: BooleanUtils.java,v 1.17 2003/10/21 23:23:06 scolebourne Exp $\n  */\n public class BooleanUtils {\n \n@@ -502,12 +502,14 @@\n      * Otherwise, <code>null</code> is returned.</p>\n      *\n      * <pre>\n+     *   BooleanUtils.toBooleanObject(null)    = null\n      *   BooleanUtils.toBooleanObject(\"true\")  = Boolean.TRUE\n      *   BooleanUtils.toBooleanObject(\"false\") = Boolean.FALSE\n      *   BooleanUtils.toBooleanObject(\"on\")    = Boolean.TRUE\n      *   BooleanUtils.toBooleanObject(\"ON\")    = Boolean.TRUE\n      *   BooleanUtils.toBooleanObject(\"off\")   = Boolean.FALSE\n      *   BooleanUtils.toBooleanObject(\"oFf\")   = Boolean.FALSE\n+     *   BooleanUtils.toBooleanObject(\"blue\")  = null\n      * </pre>\n      *\n      * @param str  the String to check\n@@ -574,34 +576,94 @@\n     // String to boolean methods\n     //-----------------------------------------------------------------------\n     /**\n-     * <p>Converts a String to a boolean.</p>\n+     * <p>Converts a String to a boolean (optimised for performance).</p>\n      * \n      * <p><code>'true'</code>, <code>'on'</code> or <code>'yes'</code>\n      * (case insensitive) will return <code>true</code>. Otherwise,\n      * <code>false</code> is returned.</p>\n+     * \n+     * <p>This method performs 4 times faster (JDK1.4) than\n+     * <code>Boolean.valueOf(String)</code>. However, this method accepts\n+     * 'on' and 'yes' as true values.\n      *\n      * <pre>\n+     *   BooleanUtils.toBoolean(null)    = false\n      *   BooleanUtils.toBoolean(\"true\")  = true\n+     *   BooleanUtils.toBoolean(\"TRUE\")  = true\n+     *   BooleanUtils.toBoolean(\"tRUe\")  = true\n      *   BooleanUtils.toBoolean(\"on\")    = true\n      *   BooleanUtils.toBoolean(\"yes\")   = true\n      *   BooleanUtils.toBoolean(\"false\") = false\n+     *   BooleanUtils.toBoolean(\"x gti\") = false\n      * </pre>\n      *\n      * @param str  the String to check\n      * @return the boolean value of the string, <code>false</code> if no match\n      */\n     public static boolean toBoolean(String str) {\n-        if (\"true\".equalsIgnoreCase(str)) {\n-            return true;\n-        } else if (\"on\".equalsIgnoreCase(str)) {\n-            return true;\n-        } else if (\"yes\".equalsIgnoreCase(str)) {\n+        // Previously used equalsIgnoreCase, which was fast for interned 'true'.\n+        // Non interned 'true' matched 15 times slower.\n+        // \n+        // Optimisation provides same performance as before for interned 'true'.\n+        // Similar performance for null, 'false', and other strings not length 2/3/4.\n+        // 'true'/'TRUE' match 4 times slower, 'tRUE'/'True' 7 times slower.\n+        if (str == \"true\") {\n             return true;\n         }\n-        // no match\n+        if (str == null) {\n+            return false;\n+        }\n+        switch (str.length()) {\n+            case 2: {\n+                char ch0 = str.charAt(0);\n+                char ch1 = str.charAt(1);\n+                return \n+                    (ch0 == 'o' || ch0 == 'O') &&\n+                    (ch1 == 'n' || ch1 == 'N');\n+            }\n+            case 3: {\n+                char ch = str.charAt(0);\n+                if (ch == 'y') {\n+                    return \n+                        (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n+                        (str.charAt(2) == 's' || str.charAt(2) == 'S');\n+                }\n+                if (ch == 'Y') {\n+                    return \n+                        (str.charAt(1) == 'E' || str.charAt(1) == 'e') &&\n+                        (str.charAt(2) == 'S' || str.charAt(2) == 's');\n+                }\n+            }\n+            case 4: {\n+                char ch = str.charAt(0);\n+                if (ch == 't') {\n+                    return \n+                        (str.charAt(1) == 'r' || str.charAt(1) == 'R') &&\n+                        (str.charAt(2) == 'u' || str.charAt(2) == 'U') &&\n+                        (str.charAt(3) == 'e' || str.charAt(3) == 'E');\n+                }\n+                if (ch == 'T') {\n+                    return \n+                        (str.charAt(1) == 'R' || str.charAt(1) == 'r') &&\n+                        (str.charAt(2) == 'U' || str.charAt(2) == 'u') &&\n+                        (str.charAt(3) == 'E' || str.charAt(3) == 'e');\n+                }\n+            }\n+        }\n         return false;\n     }\n-\n+    \n+//    public static void main(String[] args) {\n+//        long start = System.currentTimeMillis();\n+//        boolean flag = true;\n+//        int count = 0;\n+//        for (int i = 0; i < 100000000; i++) {\n+//            flag = toBoolean(\"YES\");\n+//        }\n+//        long end = System.currentTimeMillis();\n+//        System.out.println((end - start) + \" \" + flag + \" \" + count);\n+//    }\n+    \n     /**\n      * <p>Converts a String to a Boolean throwing an exception if no match found.</p>\n      * \n\n",
    "Trigger tests": [
        {
            "exception_info": "--- org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String_purify_37\n\njava.lang.StringIndexOutOfBoundsException: String index out of range: 3\n\n\tat java.lang.String.charAt(String.java:658)\n\n\tat org.apache.commons.lang.BooleanUtils.toBoolean(BooleanUtils.java:686)\n\n\tat org.apache.commons.lang.BooleanUtilsTest.test_toBoolean_String_purify_37(BooleanUtilsTest.java:488)\n\n\tat sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n\n\tat sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)\n\n\tat sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)\n\n\tat java.lang.reflect.Method.invoke(Method.java:498)\n\n\tat junit.framework.TestCase.runTest(TestCase.java:176)\n",
            "test_function": "public void test_toBoolean_String_purify_37(){\n    assertEquals(false,BooleanUtils.toBoolean(\"tru\"));\n  }"
        }
    ],
    "User Patches": {
        "patch1-Lang-51-TBar-plausible.patch": "--- /src/java/org/apache/commons/lang/BooleanUtils.java\n+++ /src/java/org/apache/commons/lang/BooleanUtils.java\n@@ -669,7 +669,7 @@\n             }\n             case 3: {\n                 char ch = str.charAt(0);\n-                if (ch == 'y') {\n+                if (ch<='y') {\n                     return \n                         (str.charAt(1) == 'e' || str.charAt(1) == 'E') &&\n                         (str.charAt(2) == 's' || str.charAt(2) == 'S');\n\n"
    }
}
"""
closure_115_reverse = """
{
    "Buggy Function": "  private CanInlineResult canInlineReferenceDirectly(\n      Node callNode, Node fnNode) {\n    if (!isDirectCallNodeReplacementPossible(fnNode)) {\n      return CanInlineResult.NO;\n    }\n\n    Node block = fnNode.getLastChild();\n\n    boolean hasSideEffects = false;\n    if (block.hasChildren()) {\n      Preconditions.checkState(block.hasOneChild());\n      Node stmt = block.getFirstChild();\n      if (stmt.isReturn()) {\n        hasSideEffects = NodeUtil.mayHaveSideEffects(stmt.getFirstChild(), compiler);\n      }\n    }\n    // CALL NODE: [ NAME, ARG1, ARG2, ... ]\n    Node cArg = callNode.getFirstChild().getNext();\n\n    // Functions called via 'call' and 'apply' have a this-object as\n    // the first parameter, but this is not part of the called function's\n    // parameter list.\n    if (!callNode.getFirstChild().isName()) {\n      if (NodeUtil.isFunctionObjectCall(callNode)) {\n        // TODO(johnlenz): Support replace this with a value.\n        if (cArg == null || !cArg.isThis()) {\n          return CanInlineResult.NO;\n        }\n        cArg = cArg.getNext();\n      } else {\n        // \".apply\" call should be filtered before this.\n        Preconditions.checkState(!NodeUtil.isFunctionObjectApply(callNode));\n      }\n    }\n\n    // FUNCTION NODE -> LP NODE: [ ARG1, ARG2, ... ]\n    Node fnParam = NodeUtil.getFunctionParameters(fnNode).getFirstChild();\n    while (cArg != null || fnParam != null) {\n      // For each named parameter check if a mutable argument use more than one.\n      if (fnParam != null) {\n        if (cArg != null) {\n          if (hasSideEffects && NodeUtil.canBeSideEffected(cArg)) {\n            return CanInlineResult.NO;\n          }\n          // Check for arguments that are evaluated more than once.\n          // Note: Unlike block inlining, there it is not possible that a\n          // parameter reference will be in a loop.\n          if (NodeUtil.mayEffectMutableState(cArg, compiler)\n              && NodeUtil.getNameReferenceCount(\n                  block, fnParam.getString()) > 1) {\n            return CanInlineResult.NO;\n          }\n        }\n\n        // Move to the next name.\n        fnParam = fnParam.getNext();\n      }\n\n      // For every call argument check for side-effects, even if there\n      // isn't a named parameter to match.\n      if (cArg != null) {\n        if (NodeUtil.mayHaveSideEffects(cArg, compiler)) {\n          return CanInlineResult.NO;\n        }\n        cArg = cArg.getNext();\n      }\n    }\n\n    return CanInlineResult.YES;\n  }",
    "Inducing Changes": "diff --git a/src/com/google/javascript/jscomp/FunctionInjector.java b/src/com/google/javascript/jscomp/FunctionInjector.java\nindex 5b38600..accf4c5 100644\n--- a/src/com/google/javascript/jscomp/FunctionInjector.java\n+++ b/src/com/google/javascript/jscomp/FunctionInjector.java\n@@ -694,6 +694,16 @@\n \n     Node block = fnNode.getLastChild();\n \n+    boolean hasSideEffects = false;  // empty function case\n+    if (block.hasChildren()) {\n+      Preconditions.checkState(block.hasOneChild());\n+      Node stmt = block.getFirstChild();\n+      if (stmt.isReturn()) {\n+        hasSideEffects = NodeUtil.mayHaveSideEffects(\n+            stmt.getFirstChild(), compiler);\n+      }\n+    }\n+\n     // CALL NODE: [ NAME, ARG1, ARG2, ... ]\n     Node cArg = callNode.getFirstChild().getNext();\n \n@@ -719,6 +729,10 @@\n       // For each named parameter check if a mutable argument use more than one.\n       if (fnParam != null) {\n         if (cArg != null) {\n+          if (hasSideEffects && NodeUtil.canBeSideEffected(cArg)) {\n+            return CanInlineResult.NO;\n+          }\n+\n           // Check for arguments that are evaluated more than once.\n           // Note: Unlike block inlining, there it is not possible that a\n           // parameter reference will be in a loop.\n\n",
    "User Patches": {
        "Closure_115.patch": "--- /src/com/google/javascript/jscomp/FunctionInjector.java\n+++ /src/com/google/javascript/jscomp/FunctionInjector.java\n@@ -694,14 +694,6 @@\n \n     Node block = fnNode.getLastChild();\n \n-    boolean hasSideEffects = false;\n-    if (block.hasChildren()) {\n-      Preconditions.checkState(block.hasOneChild());\n-      Node stmt = block.getFirstChild();\n-      if (stmt.isReturn()) {\n-        hasSideEffects = NodeUtil.mayHaveSideEffects(stmt.getFirstChild(), compiler);\n-      }\n-    }\n     // CALL NODE: [ NAME, ARG1, ARG2, ... ]\n     Node cArg = callNode.getFirstChild().getNext();\n \n@@ -727,9 +719,6 @@\n       // For each named parameter check if a mutable argument use more than one.\n       if (fnParam != null) {\n         if (cArg != null) {\n-          if (hasSideEffects && NodeUtil.canBeSideEffected(cArg)) {\n-            return CanInlineResult.NO;\n-          }\n           // Check for arguments that are evaluated more than once.\n           // Note: Unlike block inlining, there it is not possible that a\n           // parameter reference will be in a loop.\n\n"
    }
}
"""


lang51 = """
[Variables]
```
str
```
[DataFlows]
```
[
  "ch = str.charAt(0)"
]
```
[Constraints]
```
[
  "!(str == \"true\")",
  "!(str == null)",
  "str.length() == 3",
  "!(ch == 'y')",
  "!(ch == 'Y')"
]
```
[Buggy Function]
```
```
"""

closure104="""
{
  "pathConditions": [
    "alternate.isNoType()",
    "!(isAlternateUnknown)",
    "!isAllType && !isNativeUnknownType",
    "alternate instanceof UnionType",
    "!alternate.isUnknownType()",
    "unknown",
    "prototype == null",
    "implicitProto == null || implicitProto.isNativeObjectType()",
    "it.hasNext()",
    "!current.isUnknownType()",
    "!(alternate.isSubtype(current))",
    "!(JSType.isSubtype(this, that))",
    "!(thatType.isUnknownType())",
    "!(thisType.equals(thatType))",
    "this == that",
    "that instanceof JSType && this.isNominalType()",
    "thatObj != null && thatObj.isNominalType()",
    "className != null",
    "!(thatType.isAllType())",
    "thatType instanceof UnionType",
    "!(thatType instanceof NamedType)",
    "that instanceof UnionType",
    "!(that instanceof RecordType)",
    "thatCtor != null && thatCtor.isInterface()",
    "that != null",
    "!(isUnknownType() || implicitPrototypeChainIsUnknown())",
    "p != null",
    "!(p.isUnknownType())",
    "!(nativeType)",
    "implicitPrototype == null",
    "!(prototype == null)",
    "!(isConstructor() && prototype == getInstanceType())",
    "isConstructor() || isInterface()",
    "!(maybeSuperInstanceType == null)",
    "superClass != null",
    "!(subTypes == null)",
    "current != null",
    "!(current.equals(prototype))",
    "jsType instanceof ProxyObjectType",
    "!(alternate instanceof UnionType)",
    "!(current.isSubtype(alternate))",
    "result == null",
    "!(isAllType)",
    "isNativeUnknownType",
    "hasReferenceName()",
    "!(size > MAX_UNION_SIZE)",
    "size > 1",
    "!(that.isRecordType())",
    "!(thatType.isEmptyType() || thatType.isAllType())",
    "!(thisType.isUnknownType() || thatType.isUnknownType())",
    "!(t.isUnknownType())",
    "!(thisType.isSubtype(thatType))",
    "!element.isSubtype(that)",
    "!(this == that)",
    "!(thatType.isSubtype(thisType))",
    "!(thisType.isSubtype(element))",
    "thisType.isUnionType()",
    "!(alternate.isSubtype(that))",
    "!(that.isSubtype(this))",
    "!(thatType instanceof UnionType)",
    "!(jsType instanceof ProxyObjectType)",
    "!(isNativeUnknownType)",
    "!(size > 1)",
    "!(size == 1)",
    "result != null"
  ],
  "dataFlow": [
    "variants = VOID_TYPE",
    "builder = new UnionTypeBuilder(this)",
    "this.registry = registry",
    "alternate = type",
    "builder.addAlternate(type) = this",
    "isAllType = isAllType || alternate.isAllType()",
    "isAlternateUnknown = alternate instanceof UnknownType",
    "isNativeUnknownType = isNativeUnknownType || isAlternateUnknown",
    "implicitProto = getImplicitPrototype()",
    "getConstructor().getPrototype() = prototype",
    "unknown = false",
    "it = alternates.iterator()",
    "result = null",
    "current = it.next()",
    "getConstructor().hasReferenceName() = className != null",
    "getConstructor().hasReferenceName() = getConstructor().hasReferenceName()",
    "thatObj = ObjectType.cast((JSType) that)",
    "type.toObjectType() = this instanceof ObjectType ? (ObjectType) this : null",
    "that = thatObj.getReferenceName()",
    "getReferenceName().equals(thatObj.getReferenceName()) = getReferenceName().equals(thatObj.getReferenceName())",
    "getConstructor().getReferenceName() = getConstructor().getReferenceName()",
    "getConstructor().getReferenceName() = className",
    "thatObj = that.toObjectType()",
    "thatCtor = thatObj == null ? null : thatObj.getConstructor()",
    "p = getImplicitPrototype()",
    "p = getConstructor().getPrototype()",
    "p = implicitPrototype",
    "p = p.getImplicitPrototype()",
    "prototype = new FunctionPrototypeType(registry, this, null)",
    "setPrototype(new FunctionPrototypeType(registry, this, null)) = true",
    "this.properties = Maps.newHashMap()",
    "this.className = className",
    "this.nativeType = nativeType",
    "typeId = JSTypeNative.OBJECT_TYPE",
    "this.implicitPrototype = (ObjectType) getNativeType(typeId)",
    "this.implicitPrototype = registry.getNativeObjectType(JSTypeNative.OBJECT_TYPE)",
    "typeId = typeId",
    "getNativeType(typeId) = nativeTypes[typeId.ordinal()]",
    "this.ownerFunction = ownerFunction",
    "isConstructor() = kind == Kind.CONSTRUCTOR",
    "this.prototype = prototype",
    "superClass = getSuperClassConstructor()",
    "isInterface() = kind == Kind.INTERFACE",
    "maybeSuperInstanceType = getPrototype().getImplicitPrototype()",
    "maybeSuperInstanceType.getConstructor() = constructor",
    "subType = this",
    "unknown = implicitProto.isUnknownType()",
    "prototype = thatObj",
    "this.isImplicitPrototype(thatObj) = false",
    "jsType = thatObj.getReferenceName()",
    "getReferenceName().equals(thatObj.getReferenceName()) = this == jsType",
    "builder.build() = result",
    "alternateSet = Sets.newUnmodifiableHashSet(alternates)",
    "getReferenceName().hashCode() = getReferenceName().hashCode()",
    "size = alternateSet.size()",
    "result = new UnionType(registry, alternateSet)",
    "this.alternates = alternates",
    "thatType = that",
    "thisType = this",
    "getGreatestSubtype(this, that) = ((UnionType) thisType).meet(thatType)",
    "getGreatestSubtype(this, that) = getGreatestSubtype(this, that)",
    "isNoObjectType() = false",
    "isNoType() = false",
    "getReferenceName().equals(thatObj.getReferenceName()) = false",
    "union = (UnionType) thatType",
    "that = thatType",
    "((UnionType) thisType).meet(thatType) = result",
    "builder = new UnionTypeBuilder(registry)",
    "getReferenceName().equals(thatObj.getReferenceName()) = this == that",
    "result = builder.build()",
    "typeId = NO_TYPE",
    "result = nativeTypes[typeId.ordinal()]",
    "result = registry.getNativeType(NO_TYPE)"
  ],
  "declarators": [
    "UnionType union",
    "Object jsType",
    "FunctionType ownerFunction",
    "ObjectType maybeSuperInstanceType",
    "Set<JSType> alternates",
    "JSType alternate",
    "JSType thisType",
    "JSType type",
    "Set<JSType> alternateSet",
    "ObjectType thatObj",
    "FunctionPrototypeType prototype",
    "JSType current",
    "JSTypeNative typeId",
    "ObjectType implicitProto",
    "Object that",
    "UnionTypeBuilder builder",
    "FunctionType subType",
    "JSTypeRegistry registry",
    "String className",
    "JSType that",
    "JSType thatType",
    "int size",
    "ObjectType implicitPrototype",
    "Iterator<JSType> it",
    "ObjectType prototype",
    "ObjectType p",
    "JSType result",
    "ObjectType thatCtor",
    "JSType... variants",
    "boolean isAlternateUnknown",
    "FunctionType superClass"
  ],
  "variables": [
    "thisType",
    "isAlternateUnknown",
    "thatCtor",
    "thatObj",
    "isNativeUnknownType",
    "className",
    "variants",
    "type",
    "implicitProto",
    "unknown",
    "result",
    "that",
    "current",
    "alternateSet",
    "maybeSuperInstanceType",
    "builder",
    "element",
    "thatType",
    "implicitPrototype",
    "registry",
    "isAllType",
    "alternate",
    "subTypes",
    "union",
    "it",
    "alternates",
    "prototype",
    "ownerFunction",
    "NO_TYPE",
    "p",
    "superClass",
    "nativeType",
    "typeId"
  ],
  "mappingVars": {
    "UnionType": [
      "PAR#1#alternates",
      "PAR#0#registry"
    ],
    "isNoType": [
      "RETURN#false"
    ],
    "getSuperClassConstructor": [
      "RETURN#maybeSuperInstanceType.getConstructor()"
    ],
    "UnionTypeBuilder": [
      "PAR#0#registry"
    ],
    "isEmptyType": [
      "RETURN#isNoType() || isNoObjectType()"
    ],
    "isUnionType": [
      "RETURN#true"
    ],
    "isRecordType": [
      "RETURN#false"
    ],
    "createUnionType": [
      "RETURN#builder.build()"
    ],
    "isSubtype": [
      "PAR#0#thisType",
      "PAR#0#that",
      "RETURN#false",
      "RETURN#this.isImplicitPrototype(thatObj)",
      "PAR#1#thatType"
    ],
    "cast": [
      "PAR#0#type",
      "RETURN#type == null ? null : type.toObjectType()"
    ],
    "ObjectType": [
      "PAR#0#registry"
    ],
    "getImplicitPrototype": [
      "RETURN#implicitPrototype",
      "RETURN#getConstructor().getPrototype()"
    ],
    "PrototypeObjectType": [
      "PAR#1#className",
      "PAR#2#implicitPrototype",
      "PAR#0#registry"
    ],
    "getGreatestSubtype": [
      "PAR#0#that"
    ],
    "isInterface": [
      "RETURN#kind == Kind.INTERFACE"
    ],
    "getInstanceType": [
      "RETURN#typeOfThis"
    ],
    "isNativeObjectType": [
      "RETURN#nativeType"
    ],
    "isAllType": [
      "RETURN#false"
    ],
    "JSType": [
      "PAR#0#registry"
    ],
    "isUnknownType": [
      "RETURN#unknown",
      "RETURN#false"
    ],
    "FunctionPrototypeType": [
      "PAR#2#implicitPrototype",
      "PAR#0#registry",
      "PAR#1#ownerFunction"
    ],
    "getConstructor": [
      "RETURN#constructor"
    ],
    "isNominalType": [
      "RETURN#hasReferenceName()"
    ],
    "implicitPrototypeChainIsUnknown": [
      "RETURN#false"
    ],
    "hasInstanceType": [
      "RETURN#isConstructor() || isInterface()"
    ],
    "isConstructor": [
      "RETURN#kind == Kind.CONSTRUCTOR"
    ],
    "equals": [
      "PAR#0#that"
    ],
    "toString": [
      "RETURN#\"NoObject\"",
      "RETURN#\"None\""
    ]
  },
  "constants": [
    "{...}",
    "1",
    "NoObject",
    "null",
    false,
    "None",
    true
  ]
}
"""

system_prompt = {
    'deepseek-r1': apca7,
    'gpt-4-1106-preview_new0': apca7,
    'llama-2-70b': apca7,
    'claude-3-7-sonnet-20250219': apca7,
    'claude-3-5-haiku-20241022': apca7,
    'qwq-32b': apca7,
    'gemini-2.5-flash-lite-preview-06-17': apca7,
}



# print(deepseek_r1_apca3)
