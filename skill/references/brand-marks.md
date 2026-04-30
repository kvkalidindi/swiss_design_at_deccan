# Brand Marks — Secondary Green Usage

The Deccan corporate logo includes a green leaf icon at `#71BF4D` (the `green-500` step in our palette). This document specifies its allowed usage in the design system.

## What is the secondary green mark?

`#71BF4D` is the dominant green from the Deccan logo. It appears alongside the deep blue navy (`#164999`) in the official mark.

## Where you may use the green mark

| Context | Allowed | Notes |
|---------|---------|-------|
| The corporate logo | Yes | The leaf icon is the canonical use. |
| Sustainability / ESG content | Yes | Hero illustrations, callouts, badges associated with explicit sustainability or environmental themes. |
| Charts / data visualization | Yes | See `references/data-viz.md`. Charts treat the palette differently. |
| Print collateral with sustainability theme | Yes | Annual sustainability reports, environmental certifications. |

## Where you may NOT use the green mark

The green is **never** to be used as a UI accent alongside or instead of Deccan Blue. The Swiss design "one accent" principle (`references/design-system.md`) governs all standard UI: buttons, links, navigation, active states, focus rings, hover indicators, structural accents.

| Context | Allowed | Reason |
|---------|---------|--------|
| Buttons, CTAs | NO | UI accents = Deccan Blue only. |
| Links, active nav | NO | UI accents = Deccan Blue only. |
| Borders, focus rings | NO | UI accents = Deccan Blue only. |
| Status indicators (success / warning / error) | NO | Use a separate traditional status palette, never the brand green. |
| Decorative elements not tied to sustainability | NO | The green has a specific meaning; using it decoratively dilutes that meaning. |

## Why this restriction matters

Mixing two accents undermines the visual hierarchy. Two equally-saturated brand colors fight for attention, and the user can no longer tell which color signals action. By restricting the green to logo and sustainability contexts, we preserve its meaning and keep the UI's call-to-action signal (Deccan Blue) unambiguous.

## Specifying it in code

When you DO use it (logo, sustainability):

```css
:root {
  --brand-green: #71BF4D;
  --brand-green-dark: #4F8D33;  /* green-700, for emphasis */
}
```

When in doubt: do not use it. Default to Deccan Blue.
