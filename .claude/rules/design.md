---
paths:
  - "app/templates/**"
  - "app/static/**"
  - "tests/test_design.py"
---

# Wadih design guidance

## Student experience

- Design Arabic-first. Use clear Modern Standard Arabic and right-to-left layouts. Check how Arabic reads alongside English university names, scores, and dates on a phone.
- Give each screen a clear purpose and a useful next step. Put official sources beside the claims they support. Distinguish scholarship eligibility from university admission and label gaps in the available information.
- Make key journeys usable by keyboard and touch. Check visible focus, contrast, readability, and reduced motion. If motion or 3D conveys information, provide a lightweight way to access it.

## Brand and assets

- Use the existing Wadih logo and وضّاح mascot assets. Save new mascot poses as separate files. Give the mascot a purpose wherever it appears, and label agent previews as examples.
- Choose photography, illustration, diagrams, or 3D based on what each page needs. Use original or appropriately licensed assets and credit them where applicable. Use clear status labels and avoid decorative four-point sparkles.

## Design skills

Start with Taste for substantial redesigns, plus Impeccable when it is installed. Use the other available skills where they help.

- **Taste (`design-taste-frontend`)** develops the visual direction, typography, imagery, and interactions.
- **Impeccable (`impeccable`)**, when installed locally (it is not in the repository), critiques the rendered pages and helps refine hierarchy, spacing, copy, and mobile behavior.
- **Animate (`animate`)** helps when motion explains a change or guides the student’s attention.
- **3D tools** are useful when depth or interaction makes something easier to understand. Check mobile performance, touch controls, and the fallback.
- **`web-design-guidelines`** helps review accessibility and usability. Verify findings in the browser.
- **`research-wave`** and **`update-site`** apply when their documented workflows fit the task.

## Design changes

- Treat the existing palette, typography, layouts, components, and motion as starting points. Explore alternatives and choose what best serves the student. Reuse shared components where they fit.
- Review the result in a browser on mobile and desktop. When replacing a visual convention, review the tests that check the previous appearance. Keep coverage for accessibility, source accuracy, and working student interactions.