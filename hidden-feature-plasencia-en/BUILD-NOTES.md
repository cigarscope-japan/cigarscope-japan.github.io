# Build Notes — Deep-Dive #12 Plasencia, English Galley

Built 2026-11-19 from the Kazu-proofread JP galley (v147 state,
`src/hidden-feature-plasencia/index.html`: burlap-sack wording in 4
places, Chapter 4 heading shortened), following the conventions of the
#10 EN galley (`src/hidden-feature-dunbarton-en/BUILD-NOTES.md`), the
#9 EN galley and the #8 EN galley. Published as site v148 at the
limited link `/hidden-feature-plasencia-en/` (root-level `-en` path,
as with the earlier EN galleys — not `/en/...`). Formal publication
and Discord posting are NOT part of this build.

## Deliverable

- `index.html` — approx. **6,940 words** of page text (incl. captions,
  tables, boxes and footer).
- `img/` — all 28 images copied from the JP galley's `img/`: every
  image the EN page references (hero, body figures, the location map,
  lineage-table thumbnails, the NO IMAGE placeholder). The JP galley
  has no Japan-only photos, so nothing was held back.

## Structure

- Masthead / series band ("Editor-in-Chief's Deep-Dive Series") /
  feature band "Plasencia" (centered) / subtitle mirroring the JP
  title in English, with the JP two-block `nbkeep` split preserved.
- Date line in the #8/#9/#10 EN style: "English edition — scheduled
  for publication (galley), November 19, 2026".
- Feature-box intro (3 paragraphs + hero photo) + verification note box.
- Chapter 1 — Immigrants in the Vuelta Abajo: Cuba, 1865 (JP 一）
- Chapter 2 — Seizure and Exile: 1963, Losing Everything (JP 二）
- Chapter 3 — A Second Revolution! And the Fight Against Blue Mold:
  A Quarter-Century of Hardship (JP 三）
- Chapter 4 — Contract Manufacturing for Others (JP 四） + the Rocky
  Patel insert under its own h5 ("The Biggest Client — The Man Who
  Won a 'Factory Within a Factory'") + side-story box "The Pinnacle
  of Collaboration: Casa Magna Takes Cigar of the Year"
- Chapter 5 — An Empire of Leaf: Selling Leaf to the Industry (JP 五）,
  incl. the location map with its legend directly under it (place
  names stay in Latin characters; the legend is explained in English —
  the EN policy recorded 2026-11-18)
- Chapter 6 — The Pesticide-Free Challenge: The Farm Chapter (JP 六）
  + fact-check box "Drawing the Line Between 'Certified Organic' and
  'Ecological Methods'"
- Chapter 7 — The First Graduate: AJ Fernandez, from Three Rolling
  Tables (JP 七） + fact-check box "We Do Not Assert AJ's Kinship to
  Néstor"
- Chapter 8 — The Second Graduate: Oliva, the House Born Inside a
  Factory (JP 八）
- Chapter 9 — Four Points of Contact with Davidoff: From Leaf Deals
  to a Double Name (JP 九） + fact-check box "No Contract Manufacturing
  for Davidoff Itself Can Be Confirmed"
- Chapter 10 — Until They Signed Their Own Name: 2016, the Signature
  in the 150th Year (JP 十）
- Chapter 11 — The Lineage of the Lines: Alma and Cosecha (JP 十一）:
  lineup table, all 9 rows with `tthumb` thumbnails under the names;
  Triunfal = NO IMAGE (`noimg`); CA Top 25 table (6 rows); side-story
  box "Cosecha 149 Toro, 'Best of Honduras'"; fact-check box "We Do
  Not Assert a Single Origin for Cosecha 146"
- Home Ground — Estelí and Danlí, the Empire's Two Homes (unnumbered;
  replaces the JP Japan chapter)
- Conclusion (JP 結び）, incl. the Drew Estate bridge to the next
  installment.
- Footer colophon in the #8/#9/#10 EN form; site footer links to the
  JP galley and the English top page. No share buttons, no
  GoatCounter, noindex.

## Compliance checks (machine-run)

- 0 Japanese characters, 0 yen signs, 0 honorifics; "Japan" occurs
  only inside "CigarScope Japan" (title / header / colophon / footer)
  and in the site-footer link label "Japanese-edition galley" (the
  #10 EN form). No Japanese shops, no Japan price data, no Japan
  cigar database references.
- Structure counts match the JP galley exactly: h4 = 13, h5 = 1,
  captions = 22, `tthumb` = 9 (NO IMAGE = 1), side-story boxes = 2,
  note boxes = 1 + map legend = 1. Fact-check boxes = 4 (JP has 5;
  the fifth is the Japan chapter's Davidoff-Japan box, dropped with
  that chapter — see judgment call 3).
- All 28 referenced images exist in `img/`, all 28 files in `img/`
  are referenced, 29 placements (salomon.jpg appears twice, as in
  JP); every non-NO IMAGE image participates in the lightbox
  (selector `main img:not(.noimg)`).
- The JP v147 proofread fixes are reflected: the tobacco bales are
  "burlap sacks" in all 4 places (father-son alt + caption, bales alt
  + caption); the Chapter 4 heading carries only the second half of
  the JP original — "Contract Manufacturing for Others."

## Judgment calls (condensations / rephrasings beyond straight translation)

1. **Intro roadmap paragraph rewritten at the end**: the JP closing
   sentence reporting the Japan importer's 30 own-brand items was
   dropped; the paragraph closes on the Davidoff double name and the
   feature's method (no Japan content), as in the #9/#10 EN builds.
2. **Note box rewritten**: dropped the Japan-database sourcing
   sentence and the yen-conversion sentence; closes with "U.S. prices
   are the published prices of the time."
3. **The JP Japan chapter is replaced by "Home Ground"**, per the
   standing EN convention (#8/#9/#10). It is a new composition built
   only from facts already in the JP galley: the Estelí "Cathedral"
   and Ocotal factories and the Danlí (Tabacos de Oriente / El
   Paraíso) factory (map legend, Ch. 4/5); the own lines rolled on
   the same floor as contract products (Ch. 4 caption); Patel's
   stationed personnel at El Paraíso (Ch. 4); the farm geography and
   the certified-organic plots of Estelí and Jalapa (Ch. 5/6); the
   two graduates (Ch. 7/8); half the harvest sold raw, Davidoff and
   Drew Estate among the buyers (Ch. 5/9); the October 2016 Alma
   Fuerte release and Plasencia 1865 in the U.S. (Ch. 10); the May
   2019 New York launch of the Davidoff double name (Ch. 9). The JP
   Japan chapter's fact-check box (the "Davidoff Japan as agent"
   question) has no EN counterpart. No new dates, figures or place
   descriptions were introduced.
4. **Cosecha 149 side-story box scrubbed**: the JP box's closing
   sentences — that the Toro is a reader/member request item tracked
   as a bargain candidate and vanished from a discount shop's brand
   page on the morning of 2026-11-18 — are Japan-side patrol content
   and were dropped; the Cigar Trophy fact itself is kept whole.
5. **Yen conversions dropped everywhere** (Casa Magna $5.25;
   Davidoff double name $16 / $320; Alma del Cielo $25–$29.50): USD
   kept as published. The lineup table's Japan shelf prices and the
   Japan chapter's store counts/prices have no EN counterpart.
6. **Direct quotations** (Patel's recollections and proposals, the
   "carte blanche" declaration, Néstor Andrés on the organic start
   and on regenerative agriculture, José Luis on the B2C turn, the
   2013 Cigar Journal assessment and the visiting retailers'
   testimony) are faithful English renderings of the JP galley's
   quoted text; they are not re-sourced from the original English
   publications. Wording may differ slightly from the originals.
7. **Chapter 10 heading vs. body**: the JP heading says "the 150th
   year" while the JP body counts 151 years from 1865; both are
   carried as written in the approved JP text (the #9 EN precedent:
   follow the approved JP wording where the tension is the source's
   own).
8. The JP galley's CSS is carried over in full (the JP page has no
   Japan-table or shop-link CSS blocks to drop); CSS comments are
   rendered in English so the page contains no Japanese characters.
   The lightbox script is identical, with the close button's
   aria-label in English.

## Names / spellings

- Standard English forms used throughout: Néstor Plasencia Sr.,
  Néstor Andrés Plasencia, Sixto Plasencia Juárez, Jorge Plasencia,
  José Luis Plasencia, Phil Zanghi, Michael Herklots, Jim Young,
  Ed Bello, Gilberto Oliva Sr., Eduardo Fernández. Spanish cigar and
  line names follow the JP galley / brand usage (Alma Fuerte
  Generación V, Alma del Fuego Concepción, Cosecha 151 La Música,
  Reserva Orgánica, Clásica, Reserva 1898, Romeo 505, Epic Craft
  Cure, Flor de Selva, Timeless, LB1, TaviCusa).
- "Double name" renders the JP edition's term for the co-branded
  collaboration (Davidoff chapter); "rolling floor" renders the
  galera, glossed once as "(galera)" in the Estelí caption.
