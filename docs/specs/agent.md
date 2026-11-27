# وضّاح — Agent spec

وضّاح helps Saudi high school students find scholarship and university options, understand what applies to them, and take the next step in «خطتي».

Build after the redesign. See the [roadmap](../plan.md), [accounts spec](accounts.md), [search spec](search.md), and [evaluation seed](eval-seed.json).

## First release

- Keep Wadih’s guides and University Finder free to browse. Give students a clear invitation to try وضّاح. Open the agent after Google sign-in.
- Answer in clear Modern Standard Arabic. Let students ask in their own words and personalize advice using relevant details they choose to share, such as school year, intended major, destination, or English test scores.
- Build and verify one complete first-time journey. A student asks where to study a subject, gets a shortlist with reasons and official sources, and adds one useful next step to «خطتي».

## Answers and evidence

- Use the university and scholarship records Wadih already uses for list membership, requirements, scores, and deadlines. Use `app/search.py` to retrieve relevant guides for explanations. Let evaluation results guide changes to retrieval.
- Explain why an option appeared, what the student meets based on the available information, and what still needs checking. Keep scholarship eligibility, published admission requirements, and admission decisions distinct.
- Cite official sources beside the claims they support. Verify that each cited fact applies to the correct institution, program, applicant type, and cycle where relevant. If the evidence is incomplete or conflicting, explain the gap and show the relevant sources.
- Provide useful source links when the model is unavailable or the evidence is insufficient for a reliable answer.

## Actions

- Give وضّاح tools backed by the same operations the website uses. Support comparing universities, saving or removing them, adding a task to «خطتي», and updating application progress as those capabilities are released.
- Use the signed-in account to authorize each change. Ask which item the student means when the request is ambiguous. Preview changes that affect multiple items and offer undo for reversible actions.
- Show the result after the server confirms it. Make the updated plan visible in the site as well as in the conversation.
- Add deadline emails after the core pilot. Students opt in, choose which saved universities to follow, and can turn reminders off. Send from verified deadlines through a scheduled job. Test date changes, cancellations, and retries.

## Implementation and evaluation

- Start with the existing FastAPI app and Claude API tool calling. Check the current API documentation before implementation. Choose the model using measured Arabic answer quality, correct tool use, response time, and cost.
- Use the evaluation seed and add realistic Arabic requests for comparisons and actions. Include missing scores, ambiguous university names, outdated cycles, conflicting sources, failed writes, undo, and account isolation.
- Check the cited answer and the actual state change separately. When a case fails, identify whether the problem came from the source data, retrieval, the model’s interpretation, or the tool.
- Test the complete journey in staging, then run a small pilot. Compare it with using the Finder and «خطتي» directly. Fix failures, rerun the same cases, and use the results to decide what to expand.