# Milestone 1 — Jiening's Slide Content and Speaking Notes

These are English notes for the first three slides of the team's 6–7-slide, six-minute presentation. They are ready to integrate into the team deck; they are not a rendered slide file. Target about three minutes for Jiening and leave the remaining time for Yikang's results and plans. Use the report draft for full citations.

## Slide 1 — Who Connects the Departments? (about 35 seconds)

**Subtitle:** Dependence and Resilience in an Email Network

**Authors:** Jiening Yang and Yikang Cheng

- Which department pairs rely most on a small number of employees?
- Do employees with many cross-department contacts also bridge directed network paths?
- Does targeted employee removal affect the network differently from random removal?

**Speaking note:** "We study structural dependence in an institutional email network. Many email relationships do not necessarily mean every department pair has redundant contacts. We first identify concentrated contacts and important employees; the removal experiments then test what those patterns mean for connectivity."

## Slide 2 — Network and Data Validation (about 55 seconds)

**Visual:** `results/figures/department_contacts.png`, with a compact statistics panel.

- Source: SNAP email-Eu-core; nodes are employees, directed edges are observed email relationships.
- 1,005 employees, 42 anonymous departments.
- Original: 25,571 edges. Analysis: 24,929 edges after removing 642 self-loops.
- Retain all employees, including 19 isolates; 16,284 edges cross departments.
- No message counts, employee roles, or temporal behavior are inferred.

**Speaking note:** "Each edge means at least one email, not a count of messages. In this heatmap, rows send and columns receive; the colors count employee relationships, and internal ties are excluded. All path calculations still use the employee network, because department aggregation can introduce apparent paths that no individual employee path supports."

**Footer citation:** SNAP email-Eu-core [1].

## Slide 3 — Two Complementary Views of Dependence (about 90 seconds)

**Visual:** select the dependence figure or employee-ranking figure at a readable size; pass the other figure to Yikang for the preliminary-results slide if space is tight.

- Pair dependence = fraction of directed pair edges involving the most involved employee.
- Employee rankings: distinct cross-department contacts versus exact directed betweenness.
- All 27 edges from department 32 → 14 involve employee 971.
- Among pairs with at least five edges, 13 of 673 have dependence one.
- Top-ten ranking sets overlap in 8 employees, with meaningful differences.

**Speaking note:** "We count both sending and receiving employees when measuring a pair's dependence. Sparse pairs naturally have high concentration, so we show edge counts and inspect a five-edge threshold. The 32-to-14 example remains fully concentrated with 27 edges. Separately, the two employee rankings overlap but are not identical. These observations supply candidate weak points; they do not prove indirect connectivity is lost. Yikang's removal experiments address that next."

**Brief prior-work connection:** "We use Brandes's betweenness approach [3]; random-versus-targeted removal is motivated by Albert and colleagues [4]. Our focus is dependence between supplied department labels rather than community discovery [2]."

## Integration checklist

- Yikang supplies the actual removal findings on the subsequent slides; do not claim an unobserved targeted-removal effect.
- Include challenges, timeline, division of labor, conclusion, and compact references in the remaining slides.
- Keep only legible graphics; include detailed tables in the report rather than shrinking them onto a slide.
- Rehearse the handoff and enforce the six-minute total.
