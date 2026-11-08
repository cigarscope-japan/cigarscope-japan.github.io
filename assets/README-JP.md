# CigarScope Japan — Web logo assets

## Contents
- `cigarscope-japan-logo-master.png`: original generated artwork (1536 × 1024).
- `cigarscope-japan-logo-web.png`: resized website PNG.
- `cigarscope-japan-logo.webp`: optimized WebP for modern browsers.
- `cigarscope-japan-logo-embedded.svg`: SVG container with the PNG embedded. This is NOT a true vector logo.
- `cigarscope-mascot-512.png`: square puppy mascot crop for avatar/icon use.
- `favicon-64.png`, `favicon.ico`: small site icon options.

## Suggested HTML
```html
<img
  src="assets/cigarscope-japan-logo.webp"
  alt="CigarScope Japan — World Cigar News"
  class="site-logo"
>
```

```css
.site-logo {
  display: block;
  width: min(100%, 720px);
  height: auto;
  margin-inline: auto;
}
```

## Suggested favicon
```html
<link rel="icon" type="image/x-icon" href="assets/favicon.ico">
<link rel="icon" type="image/png" sizes="64x64" href="assets/favicon-64.png">
```

## Notes for publication
- The current artwork has a white background; it is not transparent.
- Keep the master PNG unchanged as the source asset.
- The SVG file is only a wrapper around an embedded raster image; request/vectorize a true SVG separately if crisp, editable vector artwork is needed at any size.
- The generated lettering should be checked before final publication. For perfect typography, use the puppy illustration as a separate mascot layer and typeset “CigarScope Japan” and “WORLD CIGAR NEWS” in HTML/CSS or a vector editor.
