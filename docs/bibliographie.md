# Bibliographie

Toutes les références sur lesquelles ce travail s'appuie, avec **ce que chacune y sert**. Une
référence sans usage identifiable n'appartient pas à une bibliographie mais à une liste de
lectures.

Cette page est **dérivée** de `paper/refs.bib`, le fichier que compilent les deux notes : les
deux ne peuvent pas diverger, et un test le vérifie. Elle se régénère par
`docker compose run --rm lab python scripts/build_bibliography.py`.


## Entropie et information

- **Shannon, Claude E.** (1948). *A Mathematical Theory of Communication*, Bell System Technical Journal, vol. 27(3), p. 379–423.  
  Définit l'entropie dont l'indice est la version normalisée.
- **von Neumann, John** (1932). *Mathematische Grundlagen der Quantenmechanik*.  
  Entropie du sous-système réduit, sur laquelle reposait l'analogie.
- **Jost, Lou** (2006). *Entropy and diversity*, Oikos, vol. 113(2), p. 363–375.  
  Justifie de publier l'indice en **nombre effectif de points de vue** plutôt qu'en entropie normalisée.


## Décohérence quantique — l'analogie de départ, réfutée depuis

- **Zeh, H. Dieter** (1970). *On the interpretation of measurement in quantum theory*, Foundations of Physics, vol. 1(1), p. 69–76.  
  Source de l'analogie décohérence / effondrement du consensus.
- **Zurek, Wojciech H.** (2003). *Decoherence, einselection, and the quantum origins of the classical*, Reviews of Modern Physics, vol. 75(3), p. 715–775.  
  Le résultat dont $\tau_D \propto \tau_R/N$ était une lecture heuristique et fausse.


## Physique statistique de l'opinion

- **Ising, Ernst** (1925). *Beitrag zur Theorie des Ferromagnetismus*, Zeitschrift f\"ur Physik, vol. 31(1), p. 253–258.  
  Modèle de la température sociale et de la transition de phase.
- **Onsager, Lars** (1944). *Crystal Statistics. I. A Two-Dimensional Model with an Order-Disorder Transition*, Physical Review, vol. 65(3-4), p. 117–149.  
  Température critique exacte, seule prédiction vérifiable du formalisme.
- **Galam, Serge** (2004). *Sociophysics: a personal testimony*, Physica A, vol. 336(1-2), p. 49–55.  
  Lignée sociophysique dont relève ce qui subsiste du modèle.
- **Castellano, Claudio ; Fortunato, Santo ; Loreto, Vittorio** (2009). *Statistical physics of social dynamics*, Reviews of Modern Physics, vol. 81(2), p. 591–646.  
  Revue de référence des dynamiques d'opinion.
- **Clifford, Peter ; Sudbury, Aidan** (1973). *A model for spatial conflict*, Biometrika, vol. 60(3), p. 581–588.  
  Voter Model, employé pour les lois d'échelle du consensus.
- **Holley, Richard A. ; Liggett, Thomas M.** (1975). *Ergodic Theorems for Weakly Interacting Infinite Systems and the Voter Model*, The Annals of Probability, vol. 3(4), p. 643–663.  
  Formalisation du Voter Model et de son temps de consensus.
- **Deffuant, Guillaume ; Neau, David ; Amblard, Frederic ; Weisbuch, G\'erard** (2000). *Mixing beliefs among interacting agents*, Advances in Complex Systems, vol. 3(01n04), p. 87–98.  
  Opinions continues : rappelle que les individus ne sont pas des spins.
- **Kramers, Hendrik A.** (1940). *Brownian motion in a field of force and the diffusion model of chemical reactions*, Physica, vol. 7(4), p. 284–304.  
  Franchissement de barrière par activation — l'analogue correct de l'« effet tunnel social ».
- **Risken, Hannes** (1989). *The Fokker-Planck Equation: Methods of Solution and Applications*.  
  Équation de Fokker-Planck et ses solutions stationnaires.
- **Watts, Duncan J. ; Strogatz, Steven H.** (1998). *Collective dynamics of `small-world' networks*, Nature, vol. 393(6684), p. 440–442.  
  Réseaux « petit monde », dont l'argument d'origine tirait une conclusion fausse.
- **Reynolds, Craig W.** (1987). *Flocks, herds and schools: A distributed behavioral model*, Proceedings of SIGGRAPH '87, p. 25–34.  
  Modèle à agents dont dérive le prototype archivé.


## Recommandation, diversité et normativité

- **Pariser, Eli** (2011). *The Filter Bubble: What the Internet Is Hiding from You*.  
  Formulation populaire de la bulle de filtres.
- **Carbonell, Jaime ; Goldstein, Jade** (1998). *The Use of MMR*, Proceedings of the 21st Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, p. 335–336. [→](https://doi.org/10.1145/290941.291025)  
  MMR : la ligne de base qui tient la frontière aussi bien que le filtre proposé ici.
- **Rao, C. Radhakrishna** (1982). *Diversity and dissimilarity coefficients: A unified approach*, Theoretical Population Biology, vol. 21(1), p. 24–43.  
  Entropie quadratique, premier remplaçant envisagé — et écarté.
- **Ohsaka, Naoto ; Togashi, Riku** (2023). *A Critical Reexamination of Intra-List Distance and Dispersion*, Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval, p. 1619–1628. [→](https://arxiv.org/abs/2305.13801)  
  Établit les optima dégénérés de l'*intra-list distance*, retrouvés ici par optimisation sous contrainte.
- **Steck, Harald** (2018). *Calibrated Recommendations*, Proceedings of the 12th ACM Conference on Recommender Systems, p. 154–162. [→](https://doi.org/10.1145/3240323.3240372)  
  Recommandations calibrées : la cible comme distribution déclarée.
- **Vrijenhoek, Sanne ; Bénédict, Gabriel ; Gutierrez Granada, Mateo ; Odijk, Daan ; de Rijke, Maarten** (2022). *RADio – Rank-Aware Divergence Metrics to Measure Normative Diversity in News Recommendations*, Proceedings of the 16th ACM Conference on Recommender Systems, p. 208–219. [→](https://arxiv.org/abs/2209.13520)  
  RADio : divergences conscientes du rang et diversité normative, dont l'indice n'occupe qu'une dimension.


## Biais de position et évaluation contrefactuelle

- **Joachims, Thorsten ; Swaminathan, Adith ; Schnabel, Tobias** (2017). *Unbiased Learning-to-Rank with Biased Feedback*, Proceedings of the Tenth ACM International Conference on Web Search and Data Mining, p. 781–789. [→](https://doi.org/10.1145/3018661.3018699)  
  Modèle de biais de position $e(R) = R^{-\eta}$ et correction par propension inverse.
- **Agarwal, Aman ; Zaitsev, Ivan ; Wang, Xuanhui ; Li, Cheng ; Najork, Marc ; Joachims, Thorsten** (2019). *Estimating Position Bias without Intrusive Interventions*, Proceedings of the Twelfth ACM International Conference on Web Search and Data Mining, p. 474–482.  
  Récolte d'interventions : estimer la sévérité sans expérience.
- **Swaminathan, Adith ; Joachims, Thorsten** (2015). *The Self-Normalized Estimator for Counterfactual Learning*, Advances in Neural Information Processing Systems 28, p. 3231–3239. [→](https://papers.nips.cc/paper/2015/hash/39027dfad5138c9ca0c474d71db915c3-Abstract.html)  
  Estimateur auto-normalisé, employé dans les comparaisons.
- **Vardasbi, Ali ; Oosterhuis, Harrie ; de Rijke, Maarten** (2020). *When Inverse Propensity Scoring does not Work: Affine Corrections for Unbiased Learning to Rank*, Proceedings of the 29th ACM International Conference on Information and Knowledge Management, p. 1475–1484. [→](https://arxiv.org/abs/2008.10242)  
  Biais de confiance et modèle affine : démontre que l'IPS ne peut pas le corriger, et fournit la contre-épreuve du notebook 20.
- **Hager, Philipp ; Deffayet, Romain ; Renders, Jean-Michel ; Zoeter, Onno ; de Rijke, Maarten** (2024). *Unbiased Learning to Rank Meets Reality: Lessons from Baidu's Large-Scale Search Dataset*, Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. [→](https://arxiv.org/abs/2404.02543)  
  Sur le jeu même où ce dépôt mesure $\hat\eta = 1{,}10$ : corriger le biais de position n'améliore pas le classement.


## Jeux de données publics

- **Wu, Fangzhao ; Qiao, Ying ; Chen, Jiun-Hung ; Wu, Chuhan ; Qi, Tao ; Lian, Jianxun ; Liu, Danyang ; Xie, Xing ; Gao, Jianfeng ; Wu, Winnie ; Zhou, Ming** (2020). *MIND: A Large-scale Dataset for News Recommendation*, Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, p. 3597–3606. [→](https://aclanthology.org/2020.acl-main.331/)  
  MIND, dont ce dépôt établit que l'ordre enregistré est mélangé.
- **Zou, Lixin ; Mao, Haitao ; Chu, Xiaokai ; Tang, Jiliang ; Ye, Wenwen ; Wang, Shuaiqiang ; Yin, Dawei** (2022). *A Large Scale Search Dataset for Unbiased Learning to Rank*, arXiv preprint arXiv:2207.03051. [→](https://arxiv.org/abs/2207.03051)  
  Baidu-ULTR, le contrôle positif du test d'échangeabilité.
- **Saito, Yuta ; Aihara, Shunsuke ; Matsutani, Megumi ; Narita, Yusuke** (2020). *Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation*, arXiv preprint arXiv:2008.07146. [→](https://arxiv.org/abs/2008.07146)  
  Open Bandit Dataset : propensions vraies et seau aléatoire, seule confrontation à une vérité terrain.
- **van Drunen, Max ; Vrijenhoek, Sanne** (2025). *How public datasets constrain the development of diversity-aware news recommender systems, and what law could do about it*, arXiv preprint arXiv:2510.05952. [→](https://arxiv.org/abs/2510.05952)  
  Établit avant nous que les jeux publics sont le goulot d'étranglement, et le droit européen la voie d'accès.


## Droit européen

- **European Union** (2022). *Regulation (EU) 2022/2065 on a Single Market For Digital Services (Digital Services Act)*, Official Journal of the European Union. [→](https://eur-lex.europa.eu/eli/reg/2022/2065/oj)  
  Cadre réglementaire : risques systémiques (art. 34) et accès aux données (art. 40).
- **Commission européenne** (2025). *Règlement délégué (UE) 2025/2050 du 1er juillet 2025 complétant le règlement (UE) 2022/2065 en ce qui concerne l'accès aux données des chercheurs agréés*, Journal officiel de l'Union européenne. [→](https://eur-lex.europa.eu/eli/reg_del/2025/2050/oj)  
  Procédure opérationnelle de la demande d'accès aux données.


---

*Source : `paper/refs.bib` · les deux notes de synthèse citent ces mêmes entrées ·
[audit critique](limites.md) · [appel à relecture](relecture.md)*
