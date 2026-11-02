# Regulatory source notes

## RBI payment systems FAQ

- Source: [Reserve Bank of India, RTGS System FAQs](https://www.rbi.org.in/Scripts/FAQView.aspx?Id=65)
- Page version observed: updated October 14, 2026
- Checked: November 2026
- Limited concept checked: the FAQ describes NEFT transactions as processed in batches and RTGS as continuous, transaction-by-transaction processing.

This source check supports only that limited conceptual distinction. It does not verify current transaction charges, minimums, service availability at a particular bank, beneficiary details, complaint routes, or any other time-sensitive conditions. No current threshold or fee from the page has been added to the training dataset.

The dated local retrieval corpus also contains limited general-awareness excerpts from the SEBI investor website, the Income Tax Department e-Filing Portal, and IRDAI policyholder FAQs, each with a review date and source URL. The SEBI/IRDAI material is general education; it cannot establish a product's suitability or an individual policy's coverage. The tax portal excerpt is a dated notice and official-portal navigation guidance, not a tax-rate, eligibility, or deadline determination. No current tax-rate or eligibility claim was adopted from it. Tax, insurance, banking, and securities statements that depend on jurisdiction, date, product, or individual facts remain flagged for external verification.

All four official URLs were checked on November 1, 2026 and were reachable during that check. The RBI FAQ displayed its October 14, 2026 update date; the Income Tax portal displayed its October 27, 2026 notice; the SEBI and IRDAI pages did not provide a publication date in the retrieved page text, so only the checked/retrieved date is recorded for those pages. The eight corpus passages represent four distinct URLs/source IDs (two passages per source ID).

The historical lexical retriever returned 37/110 benchmark prompts, including plainly unrelated passages (for example, an RTGS beneficiary-account excerpt for a fixed-deposit comparison). These historical report outputs are preserved. The current matcher requires source-specific query anchors in addition to the TF-IDF threshold; it returned 2/110 benchmark prompts. Those two excerpts support only part of their questions (policy exclusions but not waiting periods; official tax-portal direction but not a specific deadline). The current corpus therefore has low recall and does not provide complete coverage.

Machine retrieval is not a live check or a completeness guarantee. A source may be related without answering every detail. Inspect its actual scope and follow the publisher link; citation presence is not proof of the generated explanation.
