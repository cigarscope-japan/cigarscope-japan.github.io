# Build Notes — Deep-Dive #10 Steve Saka / Dunbarton, English Galley

Built 2026-11-17 from the Kazu-approved JP galley (v117 state,
`src/hidden-feature-dunbarton/index.html`), following the conventions of the
#9 EN galley (`src/hidden-feature-carrillo-en/BUILD-NOTES.md`) and the #8 EN
galley. Published as site v120 at the limited link
`/hidden-feature-dunbarton-en/` (the precedent form is the root-level
`-en` path, as with `/hidden-feature-carrillo-en/` — not `/en/...`).

## Deliverable

- `index.html` — approx. **6,900 words** of page text (incl. captions,
  table, boxes and footer).
- `img/` — 27 images copied from the JP galley's `img/`: every image the
  EN page references (hero, body figures, in-text thumbnails, lineage-table
  thumbnails, the NO IMAGE placeholder). The 2 images used only by the JP
  price table (`brulee.png`, `sin-compromiso-box.jpg`) are not present and
  not referenced.

## Structure

- Masthead / series band ("Editor-in-Chief's Deep-Dive Series", the #9 EN
  form) / feature band "Steve Saka" (centered) / subtitle mirroring the
  tentative JP title in English.
- Date line in the #8/#9 EN style: "English edition — scheduled for
  publication (galley), November 17, 2026".
- Feature-box intro (3 paragraphs + hero photo) + verification note box.
- Chapter 1 — The Navy and the Dawn of the Internet (JP 一）
- Chapter 2 — Under the King of Retail (JP 二）
- Chapter 3 — The Man Who Made Liga Privada (JP 三）, incl. the Melillo
  paragraph; its closing line now points to "the next installment"
  (the JP v116 concretization).
- Chapter 4 — Walking Away from the CEO's Chair (JP 四） + fact-check box
  "The 'Driven Out by an Acquisition' Story Does Not Hold"
- Chapter 5 — A "Trust Company" in a Town of Three Thousand (JP 五）
- Chapter 6 — The No-Compromise Laboratory (JP 六） + side-story boxes
  "The Hidden Pipe Smoker's Confession" and "Who Is the Sakasquatch?" +
  fact-check box "Why Cigar Aficionado Does Not Score His Cigars"
- Chapter 7 — A Triple Connection with Joya (JP 七）
- Home Ground — A Town of Three Thousand, and the Line the Home Market
  Cannot Buy (unnumbered; replaces the JP Japan chapter)
- Chapter 8 — The Lineage (JP 九）: lineup table, all 18 rows with
  `tthumb` thumbnails under the names; 10th Jubilee = NO IMAGE (`noimg`)
- Shokai Bushido photo + the Takumi/Fiddlehead paragraphs (from JP,
  after the lineage table), with the link pointed at the EN news article
  (`../en/news/dunbarton-shokai-bushido.html`)
- Conclusion (JP 結び）, incl. the Laudisi/Caldwell vertical thread and
  the Melillo bridge to the next installment.
- Footer colophon in the #8/#9 EN form; site footer links to the JP
  galley and the English top page. No share buttons, no GoatCounter,
  noindex.

## Compliance checks (machine-run)

- 0 Japanese characters, 0 yen signs, 0 honorifics; no Japanese shops,
  no Japan price table, no Japan cigar database references.
- The word "Japan/Japanese" occurs only inside "CigarScope Japan" and in
  two factual references carried from the approved JP text (see judgment
  call 4) — no Japan-market content of any kind.
- All 27 referenced images exist in `img/` and all 27 files in `img/` are
  referenced; every non-NO IMAGE image participates in the lightbox
  (selector `main img:not(.noimg)`).
- Key figures cross-checked against the JP galley and the claims ledger
  (`audits/claims/feature-dunbarton.md`): non-compete expiry June 19,
  2015; last day July 11, 2013; Swisher acquisition 2014; Sobremesa first
  shipment November 6, 2015, $9.95–$13.45, 1,000 boxes / 108 shops /
  126 waitlisted; Sin Compromiso $15.95–$18.45, No. 2 = 92 pts / 2018
  Top 25 No. 9, Paladín de Saka 91; PapaSaka 3,500 boxes; #GFY 4,150
  boxes; #NLMTHA 63 trial blends; Cosmic Corona $211.30, shipped
  November 9, 2026; Year of the Duque 2,000 boxes / 91; Overseas No. 1
  Halfwheel 88; StillWell Star prototypes 500, launch November 5, 2021;
  Joya U.S. distribution April 25, 2008 → SAG Imports from January 1,
  2026; Laudisi's Caldwell acquisition March 2024; Ethiopia order
  founded 1889, Melillo invested 2022. All match.

## Judgment calls (condensations / rephrasings beyond straight translation)

1. **Intro roadmap paragraph rewritten at the end**: the JP ending
   promising a report on distribution and prices in Japan was replaced
   with a closing look at where the company stands "at home and abroad"
   (no Japan content), as in the #9 EN build.
2. **Note box rewritten**: dropped the Japan-database sourcing sentence
   and the yen-conversion sentence; closes with "U.S. prices are the
   published prices of the time."
3. **Home Ground chapter is a new composition**, built only from facts
   already in the JP galley: the Dunbarton, New Hampshire base, some
   3,000 people, Cindy as partner (Ch. 5); no factory of its own,
   production at Joya and NACSA (Ch. 5/6); the no-scoring arrangement
   with CA and the nine-consecutive-years Top 5 Consensus record, the
   latter flagged in-text as the company's own account (fact-check box,
   Ch. 6); Overseas No. 1 as the first international-only line, made and
   distributed outside the U.S. by Joya, not sold at home, Halfwheel 88
   (Ch. 7). No new dates, figures or place descriptions were introduced.
4. **Two intrinsic "Japanese" references kept**: (a) Cultivo Tonto is
   documented in the JP text as inspired by Japanese fruit farmers —
   removing it would falsify the blend's record; (b) Shokai Bushido
   "bearing a Japanese word in its name" is the subject itself. Neither
   is Japan-market content. (The #9 EN page could reach zero occurrences
   because the Carrillo JP text carried no such intrinsic references.)
   By contrast, the JP conclusion's Melillo bridge detail — that Drew's
   offer email reached him on the day he arrived in Japan during his
   round-the-world trip — is rendered as "in the middle of a journey
   around the world"; the arrival-in-Japan color is JP-edition material.
   Likewise the Caldwell bridge's "answers to our interview with RACC"
   is rendered as "the answers to our interview" (no shop named).
5. **Lineup table notes scrubbed**: Mi Querida — the Japan
   approval-only note dropped, "secret mistress" / Triqui Traca kept;
   Overseas No. 1 — the Japan sales note dropped, leaving "not sold in
   the United States / Halfwheel 88"; 10th Jubilee — the Japan
   distributor sales note dropped, leaving "tenth-anniversary release /
   Halfwheel 91."
6. **Yen conversions dropped everywhere** ($9.95–$13.45; $15.95–$18.45;
   Unicorn $100; LecheBurra about $19): USD kept as published.
7. **Direct quotations** (Martínez-Cuenca on the 2007 negotiation;
   Saka's "less than cordial" and "Bravo Zulu"; "I choose to abide by
   my principles over commercial concerns"; the company motto and the
   Consensus proclamations) are faithful English renderings of the JP
   galley's quoted text; they are not re-sourced from the original
   English publications. Wording may differ slightly from the originals.
8. The `jptable` and shop-link CSS blocks of the JP galley were dropped
   (no Japan table / no shop links in EN); all other CSS, including the
   `fig-narrow` / `fig-small` period-photo caps and the lightbox, is
   carried over.
9. The title is a translation of the JP tentative title (the formal
   title is still undecided, as in JP); the footer colophon marks it
   "(tentative title)", mirroring the JP galley's （仮タイトル）.

## Names / spellings

- Standard English forms used throughout: Lew Rothman, Raúl Disla,
  Alejandro Martínez-Cuenca, Shane Ireland, Tim Vanderpool, Jeremy
  Reeves, Chris Duque, Robert Caldwell. Spanish cigar names follow the
  JP galley / brand usage (Sobremesa Solita, Paladín de Saka, Unstolen
  Valor for アンストールン・ヴェイラー, Lengua de Suegra, LecheBurra).
- "Cultivo Tonto," "El Gringo Gruñón," "Sakasquatch" — as in the JP
  galley and the claims ledger.
