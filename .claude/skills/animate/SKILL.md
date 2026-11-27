---
name: animate
description: Add purposeful motion to Wadih's web interface. Use when building an animation or transition that helps students understand a change, receive feedback, or follow a sequence.
---

# Animate Wadih

Build motion that supports the student’s task. Start with what the student should understand or feel, then choose the simplest implementation that achieves it.

## Decide what should move

- Keep frequent actions immediate. A keyboard shortcut, filter change, or repeated navigation should feel responsive from the moment the student acts.
- Use subtle motion to confirm an action, connect two states, or show where something appeared or went. A save button can confirm a successful save without shifting the university row.
- Use expressive motion sparingly for moments that benefit from it, such as introducing a walkthrough or celebrating a completed milestone.
- Use explanatory motion in guides and tools when it makes a relationship easier to understand. Keep requirements, scores, deadlines, and sources stable while students read them.
- If an instant state change communicates the same thing equally well, use it.

## Build with Wadih’s existing components

- Start with the existing Jinja templates, CSS, and vanilla JavaScript. Follow the current `.claude/rules/design.md`.
- Use [RECIPES.md](RECIPES.md) for interaction ideas. Adapt the relevant example to Wadih’s components and stack.
- Use a CSS transition for simple state changes, hover, and press feedback. Use a CSS animation for a predetermined sequence. Use the Web Animations API when JavaScript needs to pause, reverse, or interrupt an animation.
- Reuse existing easing and duration tokens where they fit. Treat the timings in the recipes as starting points and adjust them after seeing the interaction in the browser.
- Name the specific properties in each transition. Prefer `transform` and `opacity` for movement and fades, and check performance on the rendered page. Anchor popover motion to its trigger when that helps the student see the connection.
- Handle repeated taps, reversals, and exits. Keep focus and interaction working while the interface changes.

## Accessibility and verification

- Honor `prefers-reduced-motion`. Use an instant change, a static explanation, or a minimal fade as appropriate. Keep the same information and actions available.
- Apply hover-only motion on devices that support hover. Check the same interaction with touch and keyboard.
- Check the result in the browser at mobile and desktop widths. For directional motion, verify that it makes sense in Arabic RTL and English LTR.
- Test repeated input and reduced motion. Confirm that the student can read the content and complete the task while the animation runs.

Implement the motion, verify it, and briefly explain what it communicates and what you checked.