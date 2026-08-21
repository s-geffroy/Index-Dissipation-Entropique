# Bibliography

Every reference this work rests on, together with **what each is used for here**. A reference
with no identifiable use belongs to a reading list, not to a bibliography.

This page is **derived** from `paper/refs.bib`, the file both notes compile: the two cannot
diverge, and a test checks it. Regenerate with
`docker compose run --rm lab python scripts/build_bibliography.py`.


## Entropy and information

- **Shannon, Claude E.** (1948). *A Mathematical Theory of Communication*, Bell System Technical Journal, vol. 27(3), p. 379–423.  
  Defines the entropy of which the index is the normalised version.
- **von Neumann, John** (1932). *Mathematische Grundlagen der Quantenmechanik*.  
  Reduced-subsystem entropy, on which the analogy rested.
- **Jost, Lou** (2006). *Entropy and diversity*, Oikos, vol. 113(2), p. 363–375.  
  Justifies publishing the index as an **effective number of viewpoints** rather than a normalised entropy.


## Quantum decoherence — the founding analogy, since refuted

- **Zeh, H. Dieter** (1970). *On the interpretation of measurement in quantum theory*, Foundations of Physics, vol. 1(1), p. 69–76.  
  Source of the decoherence / consensus-collapse analogy.
- **Zurek, Wojciech H.** (2003). *Decoherence, einselection, and the quantum origins of the classical*, Reviews of Modern Physics, vol. 75(3), p. 715–775.  
  The result of which $\tau_D \propto \tau_R/N$ was a heuristic and incorrect reading.


## Statistical mechanics of opinion

- **Ising, Ernst** (1925). *Beitrag zur Theorie des Ferromagnetismus*, Zeitschrift f\"ur Physik, vol. 31(1), p. 253–258.  
  Model of social temperature and the phase transition.
- **Onsager, Lars** (1944). *Crystal Statistics. I. A Two-Dimensional Model with an Order-Disorder Transition*, Physical Review, vol. 65(3-4), p. 117–149.  
  Exact critical temperature, the formalism's only checkable prediction.
- **Galam, Serge** (2004). *Sociophysics: a personal testimony*, Physica A, vol. 336(1-2), p. 49–55.  
  The sociophysics lineage to which what survives of the model belongs.
- **Castellano, Claudio ; Fortunato, Santo ; Loreto, Vittorio** (2009). *Statistical physics of social dynamics*, Reviews of Modern Physics, vol. 81(2), p. 591–646.  
  Reference survey of opinion dynamics.
- **Clifford, Peter ; Sudbury, Aidan** (1973). *A model for spatial conflict*, Biometrika, vol. 60(3), p. 581–588.  
  Voter model, used for consensus scaling laws.
- **Holley, Richard A. ; Liggett, Thomas M.** (1975). *Ergodic Theorems for Weakly Interacting Infinite Systems and the Voter Model*, The Annals of Probability, vol. 3(4), p. 643–663.  
  Formalisation of the voter model and its consensus time.
- **Deffuant, Guillaume ; Neau, David ; Amblard, Frederic ; Weisbuch, G\'erard** (2000). *Mixing beliefs among interacting agents*, Advances in Complex Systems, vol. 3(01n04), p. 87–98.  
  Continuous opinions: a reminder that individuals are not spins.
- **Kramers, Hendrik A.** (1940). *Brownian motion in a field of force and the diffusion model of chemical reactions*, Physica, vol. 7(4), p. 284–304.  
  Activated barrier crossing — the correct analogue of "social tunnelling".
- **Risken, Hannes** (1989). *The Fokker-Planck Equation: Methods of Solution and Applications*.  
  The Fokker-Planck equation and its stationary solutions.
- **Watts, Duncan J. ; Strogatz, Steven H.** (1998). *Collective dynamics of `small-world' networks*, Nature, vol. 393(6684), p. 440–442.  
  Small-world networks, from which the original argument drew a false conclusion.
- **Reynolds, Craig W.** (1987). *Flocks, herds and schools: A distributed behavioral model*, Proceedings of SIGGRAPH '87, p. 25–34.  
  Agent model from which the archived prototype derives.


## Recommendation, diversity and normativity

- **Pariser, Eli** (2011). *The Filter Bubble: What the Internet Is Hiding from You*.  
  Popular formulation of the filter bubble.
- **Carbonell, Jaime ; Goldstein, Jade** (1998). *The Use of MMR*, Proceedings of the 21st Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, p. 335–336. [→](https://doi.org/10.1145/290941.291025)  
  MMR: the baseline that holds the frontier as well as the filter proposed here.
- **Rao, C. Radhakrishna** (1982). *Diversity and dissimilarity coefficients: A unified approach*, Theoretical Population Biology, vol. 21(1), p. 24–43.  
  Quadratic entropy, the first replacement considered — and discarded.
- **Ohsaka, Naoto ; Togashi, Riku** (2023). *A Critical Reexamination of Intra-List Distance and Dispersion*, Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval, p. 1619–1628. [→](https://arxiv.org/abs/2305.13801)  
  Establishes the degenerate optima of intra-list distance, recovered here by constrained optimisation.
- **Steck, Harald** (2018). *Calibrated Recommendations*, Proceedings of the 12th ACM Conference on Recommender Systems, p. 154–162. [→](https://doi.org/10.1145/3240323.3240372)  
  Calibrated recommendations: the target as a declared distribution.
- **Vrijenhoek, Sanne ; Bénédict, Gabriel ; Gutierrez Granada, Mateo ; Odijk, Daan ; de Rijke, Maarten** (2022). *RADio – Rank-Aware Divergence Metrics to Measure Normative Diversity in News Recommendations*, Proceedings of the 16th ACM Conference on Recommender Systems, p. 208–219. [→](https://arxiv.org/abs/2209.13520)  
  RADio: rank-aware divergences and normative diversity, of which the index occupies only one dimension.


## Position bias and counterfactual evaluation

- **Joachims, Thorsten ; Swaminathan, Adith ; Schnabel, Tobias** (2017). *Unbiased Learning-to-Rank with Biased Feedback*, Proceedings of the Tenth ACM International Conference on Web Search and Data Mining, p. 781–789. [→](https://doi.org/10.1145/3018661.3018699)  
  Position-bias model $e(R) = R^{-\eta}$ and inverse-propensity correction.
- **Agarwal, Aman ; Zaitsev, Ivan ; Wang, Xuanhui ; Li, Cheng ; Najork, Marc ; Joachims, Thorsten** (2019). *Estimating Position Bias without Intrusive Interventions*, Proceedings of the Twelfth ACM International Conference on Web Search and Data Mining, p. 474–482.  
  Intervention harvesting: estimating severity without an experiment.
- **Swaminathan, Adith ; Joachims, Thorsten** (2015). *The Self-Normalized Estimator for Counterfactual Learning*, Advances in Neural Information Processing Systems 28, p. 3231–3239. [→](https://papers.nips.cc/paper/2015/hash/39027dfad5138c9ca0c474d71db915c3-Abstract.html)  
  The self-normalised estimator, used in the comparisons.
- **Vardasbi, Ali ; Oosterhuis, Harrie ; de Rijke, Maarten** (2020). *When Inverse Propensity Scoring does not Work: Affine Corrections for Unbiased Learning to Rank*, Proceedings of the 29th ACM International Conference on Information and Knowledge Management, p. 1475–1484. [→](https://arxiv.org/abs/2008.10242)  
  Trust bias and the affine model: proves IPS cannot correct it, and provides notebook 20's counter-test.
- **Hager, Philipp ; Deffayet, Romain ; Renders, Jean-Michel ; Zoeter, Onno ; de Rijke, Maarten** (2024). *Unbiased Learning to Rank Meets Reality: Lessons from Baidu's Large-Scale Search Dataset*, Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. [→](https://arxiv.org/abs/2404.02543)  
  On the very dataset where this repository measures $\hat\eta = 1.10$: correcting position bias does not improve ranking.


## Public datasets

- **Wu, Fangzhao ; Qiao, Ying ; Chen, Jiun-Hung ; Wu, Chuhan ; Qi, Tao ; Lian, Jianxun ; Liu, Danyang ; Xie, Xing ; Gao, Jianfeng ; Wu, Winnie ; Zhou, Ming** (2020). *MIND: A Large-scale Dataset for News Recommendation*, Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, p. 3597–3606. [→](https://aclanthology.org/2020.acl-main.331/)  
  MIND, whose recorded order this repository shows to be shuffled.
- **Zou, Lixin ; Mao, Haitao ; Chu, Xiaokai ; Tang, Jiliang ; Ye, Wenwen ; Wang, Shuaiqiang ; Yin, Dawei** (2022). *A Large Scale Search Dataset for Unbiased Learning to Rank*, arXiv preprint arXiv:2207.03051. [→](https://arxiv.org/abs/2207.03051)  
  Baidu-ULTR, the exchangeability test's positive control.
- **Saito, Yuta ; Aihara, Shunsuke ; Matsutani, Megumi ; Narita, Yusuke** (2020). *Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation*, arXiv preprint arXiv:2008.07146. [→](https://arxiv.org/abs/2008.07146)  
  Open Bandit Dataset: true propensities and a random bucket, the only confrontation with a ground truth.
- **van Drunen, Max ; Vrijenhoek, Sanne** (2025). *How public datasets constrain the development of diversity-aware news recommender systems, and what law could do about it*, arXiv preprint arXiv:2510.05952. [→](https://arxiv.org/abs/2510.05952)  
  Establishes before us that public datasets are the bottleneck, and European law the route to access.


## European law

- **European Union** (2022). *Regulation (EU) 2022/2065 on a Single Market For Digital Services (Digital Services Act)*, Official Journal of the European Union. [→](https://eur-lex.europa.eu/eli/reg/2022/2065/oj)  
  Regulatory framework: systemic risks (Art. 34) and data access (Art. 40).
- **Commission européenne** (2025). *Règlement délégué (UE) 2025/2050 du 1er juillet 2025 complétant le règlement (UE) 2022/2065 en ce qui concerne l'accès aux données des chercheurs agréés*, Journal officiel de l'Union européenne. [→](https://eur-lex.europa.eu/eli/reg_del/2025/2050/oj)  
  Operational procedure for the data access request.


---

*Source: `paper/refs.bib` · both synthesis notes cite these same entries ·
[critical audit](limites.en.md) · [call for review](relecture.md)*
