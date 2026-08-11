VERBOSITY_MITIGATION_INSTRUCTIONS = """
VERBOSITY AND LENGTH CONTROL:

Do not reward a response merely because it is longer,
more detailed, or contains more information.

Evaluate whether the response provides the amount of
information actually required by the user's request.

When comparing responses:

1. Do not use response length as a proxy for quality.
2. Do not reward unnecessary explanation, repetition,
   background information, or tangential details.
3. Do not penalize a concise answer when it completely
   satisfies the user's request.
4. Reward additional detail only when that detail is
   relevant, accurate, useful, and required or clearly
   beneficial for the task.
5. Penalize irrelevant, redundant, speculative, or
   unsupported additions when they reduce the quality
   of the response.
6. If the user explicitly requests detail, explanation,
   examples, or a comprehensive answer, sufficient
   detail should be rewarded.
7. If the user explicitly requests a concise answer,
   unnecessary detail should count against the response.
8. Judge the substance and usefulness of the response,
   not its word count.

IMPORTANT:
A longer response is not inherently better.
A shorter response is not inherently better.

Prefer the response that best satisfies the user's
actual requirements with the appropriate level of detail.
"""