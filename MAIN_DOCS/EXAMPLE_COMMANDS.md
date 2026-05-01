"""
Code Morphing Agent for Obfelisk

Applies continuous code mutation techniques that
transform code structure while preserving semantics.
"""
from typing import Any, Dict, Optional

from ..obfuscation_agent import ObfuscationAgent
from framework.build_context import BuildContext


class CodeMorphingAgent(ObfuscationAgent):
    """
    Agent that applies code morphing techniques for continuous
    mutation of code structure while preserving semantics.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="code_morphing_agent",
            name="Code Morphing Agent",
            description="Applies continuous code mutation techniques",
            capabilities=config.get(
                "capabilities",
                [
                    "semantic-preserving mutations",
                    "structural transformation",
                    "expression rewriting",
                    "control flow morphing",
                ],
            ),
            config=config,
        )

    def execute(self, context: BuildContext) -> BuildContext:
        """Execute the code morphing agent on the build context."""
        if not context.source_files:
            self.logger.error("No source files found in build context")
            return context

        source_file_path = list(context.source_files.keys())[0]
        source_code = context.source_files[source_file_path]

        self.logger.info(f"Starting code morphing for file: {source_file_path}")

        result = self.run(source_code, context={"original_code": source_code})

        if result.get("status") == "success":
            context.source_files[source_file_path] = result.get("findings", source_code)
            self.logger.info(f"Code morphing completed for file: {source_file_path}")
        else:
            self.logger.error(f"Code morphing failed: {result.get('error', 'Unknown error')}")

        return context

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply code morphing transformations"""
        try:
            code_to_obfuscate = self._extract_code_from_pipeline(task, context)
            entropy_var = self.get_random_variation(1, 10000)

            prompt = f"""<role>You are an expert in code morphing and semantic-preserving code transformations.</role>

<task>Apply code morphing techniques to transform the code:
1. You **MUST** rewrite expressions using equivalent forms
2. You **MUST** morph arithmetic operations (a+b -> a-(-b), etc.)
3. You **MUST** transform boolean expressions using logical equivalences
4. You **MUST** restructure loops (for to while, do-while variations)
5. You **MUST** modify conditional structures (if-else chains, ternary operators)
6. You **MUST** inline and outline functions selectively
7. You **MUST** split and merge statements
8. You **MUST** use temporary variables and expression decomposition</task>

<code>
{code_to_obfuscate}
</code>

<requirements>
You **MUST** produce code that is:
- **SEMANTICALLY EQUIVALENT** to the original
- **STRUCTURALLY DIFFERENT** in every way possible
- Using **DIFFERENT** morphing patterns each execution
- With **UNIQUE** variable names and expression forms
You **MUST** preserve **ALL** original functionality.
You **MUST** include all necessary header files and dependencies.
Entropy factor: {entropy_var}

Morphing principles:
- You **MUST** use De Morgan's laws or similar for boolean transformations
- You **MUST** apply algebraic identities for arithmetic
- You **MUST** transform control flow patterns
- You **MUST** use functionally equivalent idioms
</requirements>
{self.MULTI_FILE_INSTRUCTIONS}
<output_format>
You **MUST** return **ONLY** the raw morphed code.
You **MUST NOT** include markdown formatting, code blocks, or backticks.
The output **MUST** start directly with code syntax.
</output_format>"""

            temperature = 0.6 + self.get_random_float(0.0, 0.3)

            response_text = self.call_llm_with_continuation(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 16384),
                temperature=temperature,
                max_continuations=self.config.get("max_continuations", 3),
                enable_continuation=self.config.get("enable_continuation", False),
            )

            if response_text and len(response_text) < 500 and response_text.startswith("Error:"):
                return self._create_error_response(Exception(response_text), task)

            return self._create_success_response(
                obfuscated_code=response_text,
                task=task,
                entropy_var=entropy_var,
                artifact_name="morphed_code",
            )

        except Exception as e:
            return self._create_error_response(e, task)
