## 5. Method in brief (budget: 900 words)

**Claim:** The model transparently propagates selected assumptions from an Indian market anchor and transfers the resulting path to Pakistan; it does not estimate adoption from observed purchases.

**Evidence:**

- GFI India/Deloitte's **2022** category estimates are **INR 100 crore meat**, **250 crore dairy** and **1 crore eggs**, totalling **351 crore**. [Original economic summary](https://gfi-india.org/wp-content/uploads/2024/06/GFI-India-economic-analysis.pdf), physical final page; precise publication date and price/valuation basis unstated. Evidence family: externally modelled level.
- The retained calculation converts the total to **$45.286640 million at 2025 prices**, conditional on its valuation assumptions. [Proxy inputs and equations](../../revisions/2026-10-27/methods/proxy.md), explanation dated **27 October 2026**. Evidence family: derived conversion.
- **10,000 draws** of **four parameters** produce the **10th, 50th and 90th percentiles**. The retained lower and upper additional-growth bounds are approximately **−2%** and **17.8%** annually. Source: the same methods and [retained engine](../../../tools/build_altprotein_proxy.py). Evidence family: analyst specification; the bounds use a US retail decline and Indian vacancy growth.

**Plain-language sequence:** Establish the Indian starting level under the stated price assumption. Grow spending per person using real income, urbanisation and an additional growth term. Multiply by population to obtain national spending. Construct Pakistan's path using relative income, urban share, animal-protein supply and industry proxies. Reuse each draw across countries and years. Report how deliberately changing overlapping assumptions changes the result. Detailed equations belong in Appendix A.

**Caveat:** The proxy includes fermentation-derived foods in its intended scope but has no separately estimated category-entry term; its anchor contains plant-based meat, dairy and eggs. Cultivated meat is excluded. Mapping vacancy growth or a US nominal sales decline into a real spending-growth bound is an assumption. The uncertainty range reflects selected distributions and has no demonstrated predictive coverage. The top-down Pakistan check is an independent companion calculation, not an input or a refit.

**Cross-reference:** The US chapter's elicitation method and the Africa chapter's qualitative proxy method remain distinct. Shared labels do not establish a shared estimand.

**Figures or tables:** Reuse the plain-language sequence above; place exact equations and the retained input ledger in Appendix A.

**AI draft, replace:** We start from an external estimate of India's market and make the assumptions needed to carry it forward explicit. The Pakistani estimate is a further transfer because the retained collection provides no comparable national sales anchor. Repeating the calculation under different parameters shows what the chosen assumptions permit. It does not turn those assumptions into observed relationships or assign calibrated probabilities to future sales.

**Open questions for Umar:** The unresolved Indian source price and retail basis must stay visible in the final prose and shared definitions box.
