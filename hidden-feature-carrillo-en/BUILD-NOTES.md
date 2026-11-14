# Build Notes — Deep-Dive #9 E.P. Carrillo, English Galley

Built 2026-11-14 from the approved JP galley (v97 state,
`src/hidden-feature-carrillo/index.html`), following the conventions of the
#8 EN galley (`src/hidden-feature-crowned-heads-en/index.html`).
**Not published.** No other folder was touched.

## Deliverable

- `index.html` — approx. **4,450 words** of page text (incl. captions,
  table, boxes and footer).
- `img/` — the 14 non-`jp-*` images copied from the JP galley's `img/`
  (atlantic-inch-nicaragua, ca-carrillo-portrait, ca-endure,
  cigarbid-los-gloriosos, cigarcom-serie-r, halfwheel-pledge-prequel,
  nextcigar-allegiance, nextcigar-essence-sumatra, no-image,
  official-encore-majestic, retail-historia-eiii,
  retail-newwave-connecticut, thompson-wavell, wfr-fourkicks-box).
  The 11 `jp-*.jpg` price-table photos are not present and not referenced.

## Structure

- Masthead / series band ("Editor-in-Chief's Deep-Dive Series") /
  feature band "E.P. Carrillo" (centered) / subtitle mirroring the title.
- Date line in the #8 EN style: "English edition — scheduled for
  publication (galley), November 14, 2026".
- Feature-box intro (3 paragraphs + hero photo) + verification note box.
- Chapter 1 — The Senator's Son (JP 一）
- Chapter 2 — The Drummer's Dream (JP 二） + side-story box "Blending in
  5/4 Time"
- Chapter 3 — The Miami Boom (JP 三） + fact-check box "Same Name, a
  Different Cigar"
- Chapter 4 — The Sale and the Ten Years He Stayed (JP 四）
- Chapter 5 — A Fresh Start at 57 (JP 五）
- Chapter 6 — Twice to the Summit (JP 六）
- Chapter 7 — The Third Handshake (JP 七） + side-story box "The
  Homecoming He Didn't Hide"
- Home Ground — Santiago, the City That Rebuilt Him (unnumbered;
  replaces the JP Japan chapter)
- Chapter 8 — The Lineage (JP 九）: lineup table, all 12 rows with
  `tthumb` thumbnails under the names; Edición Inaugural 2009 = NO IMAGE
  (`noimg`)
- Conclusion (JP 結び）, incl. the Caldwell-at-12 bridge to Part 10 and
  the closing arc ending at the third handshake at age 74.
- Footer colophon in the #8 EN form; site footer links to the JP galley
  and the English top page. No share buttons, no GoatCounter, noindex.

## Compliance checks (machine-run)

- 0 Japanese characters, 0 yen signs, 0 honorifics; "Japan" occurs only
  inside "CigarScope Japan" (title/header/footer).
- No Japanese shops, no Japan price table, no Japan cigar database
  references; no Arsenio Ramos; no "Boveda" misspelling (the word does
  not occur in this article).
- All 14 referenced images exist in `img/`; every non-NO IMAGE image
  participates in the lightbox (selector `main img:not(.noimg)`).
- Headless render comparison: served locally, this page behaves
  identically to the JP galley and the #8 EN galley (the shared
  `../style.css` is absent from the `src/` tree — it is supplied at
  publish/assembly time — so a bare local render is not meaningful;
  parity with the two proven pages is the check that matters).

## Judgment calls (condensations / rephrasings beyond straight translation)

1. **Intro roadmap paragraph rewritten**: the JP ending promising a
   report on distribution and prices in Japan was replaced with the arc
   summary ending at the "third handshake" (no Japan content).
2. **Note box rewritten**: dropped the Japan-database sourcing sentence
   and the yen-conversion sentence; closes with "U.S. prices are the
   published prices of the time."
3. **Home Ground chapter is a new composition**, built only from facts
   already in the JP galley: Dominican production from April 1996
   (2.2M vs Miami 1.2M in Apr–Dec 1996, Ch. 3); the 40,000 sq ft
   free-zone plant founded April 2009 and named Tabacalera La Alianza
   (Ch. 5); factory renamed Casa Carrillo Feb 2024 and company rebrand
   Apr 2025 (Ch. 7); the factory's outside-brand work — Four Kicks
   (2011, first), Headley Grange, Le Carême, Coroneta Maduro, "Best
   Small Factory (2018)" (Ch. 7); the Feb 2025 Procigar tour and PCA
   2025 booth episodes (Ch. 7 side-story box). Closing line "the exile,
   in his seventies, blended a cigar once more for the kingdom he had
   sold" is a summary of Ch. 7 facts, not a new fact. No new dates,
   figures or place descriptions were introduced ("free zone" and
   Santiago are from the JP text).
4. **Lineup table notes scrubbed**: Allegiance — Japan sales note
   dropped, friendship-line/Oliva note kept (wrapper cell kept as "―"
   per JP); New Wave Connecticut — the yen approval-price note dropped,
   leaving "A mild, everyday line"; Endure and Essence — "Japan
   approval pending" replaced with their release facts already in the
   JP table (Endure 2025 foot-band experiment; Essence Series from
   2024, six-blend "wrapper takes the lead" concept).
5. **Yen conversions dropped everywhere** (Wavell $1.95→$2.85, Edición
   Inaugural $13, Los Gloriosos Toro $8.99): USD kept as published.
6. **Direct quotations** (Carrillo's "54 years" line, Lissette's two
   quotations, the SmokingPipes drumming passage, Halfwheel's "shining
   lever" line) are faithful English renderings of the JP galley's
   quoted text; they are not re-sourced from the original English
   interviews. Wording may differ slightly from the original
   publications.
7. **Chapter 4, Rick Rodriguez**: the JP galley states he joined the
   LGC blend team in 2008 "after Carrillo's departure" (Carrillo left
   in March 2009). The EN follows the approved JP wording exactly; the
   tension is in the source text and was not silently rewritten.
8. **Chapter 6, Encore**: JP says the second act "begun at 58" reached
   the summit at 66; kept as written (founding in 2009 is elsewhere
   consistently "at 57" — again the source's own wording, preserved).
9. Chapter headings follow the #8 EN pattern "◆ Chapter N — Title:
   Subtitle"; Home Ground and Conclusion are unnumbered, as in #8 EN.
   The series band uses the wording specified for this build
   ("Editor-in-Chief's Deep-Dive Series"; #8 EN's band carried its
   number, this one follows the brief).
10. The `jptable` and shop-link CSS blocks of the JP galley were
    dropped (no Japan table / no shop links in EN); all other CSS,
    including the `.nb` wrap fix and the lightbox, is carried over.

## Names / spellings not independently verified

- "Cuban Land & Leaf Tobacco" — the father's employer, rendered from
  the JP galley's katakana; spelling follows the claims ledger's
  rendering, not re-checked against a primary source in this build.
- "Meerapfel" (Endure's Cameroon wrapper supplier family) — standard
  spelling as used in the trade press and the JP table; kept.
- "Edición Inaugural 2009", "Regalias de Celia", "El Senador",
  "Doña Elena" — Spanish forms as in the JP galley / brand usage.
- No other name raised a flag; all ratings, dates and figures were
  carried from the JP galley and its claims ledger (born November
  1951; sale agreed 1999-07-02, closed August 1999; left March 2009 at
  57; Encore Majestic 2018 #1/96; Pledge Prequel 2020 #1/98 "tied
  highest", twice-in-three-years = Padrón and Carrillo only in the
  2004– list; La Historia E-III 2014 #2/95; Pledge naming from Big
  Smoke Las Vegas 2019 consumers, homage to all smokers; Huber drum
  mention kept with the weight difference, not as a parallel pair;
  Los Gloriosos framed as the third handshake with the 2014 and 2017
  precedents).
