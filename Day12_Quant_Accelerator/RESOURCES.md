# Day 12 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Why pre-register (01_why_preregister)
- ✅ Nosek, Ebersole, DeHaven & Mellor (2018), "The Preregistration Revolution," PNAS 115(11):2600–2606 (author manuscript). Open access: https://doi.org/10.1073/pnas.1708274114
- ✅ Harvey (2017), "Presidential Address: The Scientific Outlook in Financial Economics," J. Finance 72(4) (Duke copy). p-hacking, minimum Bayes factor, research-culture guidelines.

## The hurdle (see Day 5 kit)
- Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns": t > 3. Already in Day 5 kit.
- Harvey & Liu (2015), "Backtesting": haircut Sharpe. Already in Day 5 kit. Their code: https://people.duke.edu/~charvey/backtesting
- Bailey & López de Prado (2014), Deflated Sharpe Ratio. Already in Day 5 kit (you'll use it on Day 20).

## Templates and registries 
- OSF template list (incl. AsPredicted's questions): https://osf.io/zab38/overview
- COS guide to choosing a template: https://www.cos.io/blog/choosing-preregistration-template-guide-for-researchers
- AsPredicted (free, private-until-you-share registrations): https://aspredicted.org/
- Optional: register on OSF for a third-party timestamp: https://osf.io/registries

## Videos
- Center for Open Science, "The What, Why, and How of Preregistration" (56 min): https://www.youtube.com/watch?v=8QK2-udwoK8
- Brunel University London, "Why you should pre-register your research study – and how easy it is to do": https://www.youtube.com/watch?v=_505Oek-wHM

## Build-along (04_build_along), tested
- `prereg_designer.py` / `.ipynb`: power table, fixed-grid stability, block-bootstrap falsifier sizing, SHA-256 lock/verify. Reuses Day 7 `nse_costs.py`.

## Templates (05_templates)
- `preregistration-template.md`: an AsPredicted-style form adapted for trading (data status, leakage note, overlay vs alpha, falsifier, kill date, backup).

## Data (07_data)
- NIFTY50_daily.csv (Yahoo; script reads only to 2018-12-31), IIMA monthly four factors (Dec 2025 release).
