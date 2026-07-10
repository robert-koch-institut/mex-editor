## MEx Editor – Technical Documentation

> A simple and fast way to create and edit resources and activities — built for basic users, i.e. employees, not metadata specialists.

This documentation covers the **technical building blocks** of the MEx Editor frontend: components, classes, interfaces, services and modules. If you're looking for installation or usage instructions instead, see the project [README](https://github.com/robert-koch-institut/mex-editor-ng/blob/main/README.md).

### Why this editor exists

Most RKI employees who need to describe research data or activities are not metadata experts. They simply need to capture _what_ a resource or activity is, _who_ is responsible for it, and _how_ it relates to other entities — without learning a complex data model first.

The MEx Editor is designed around that constraint:

- **Simple** — guided forms instead of raw metadata schemas, sensible defaults, and inline validation that explains itself.
- **Fast** — common actions (create, edit, link, publish) take a few clicks, not a training session.
- **Safe** — edits are applied as non-destructive rules on top of the underlying metadata, so automated updates never overwrite manual input.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 989 310" width="989" style="max-width:100%;height:auto" role="img" aria-label="An employee at a laptop creates and edits Resource and Activity entities">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 z" fill="#8593c4"/>
    </marker>
  </defs>
  <rect width="989" height="310" fill="#eef1fa"/>
  <g transform="translate(66,-25)">
  <g transform="translate(33 31) scale(0.8)">
    <circle cx="165" cy="110" r="32" fill="#2e4ca6"/>
    <path d="M110 235 Q110 148 165 148 Q220 148 220 235 Z" fill="#2e4ca6"/>
  </g>
  <text x="382" y="160" text-anchor="middle" font-size="16" fill="#8593c4">creates &amp; edits</text>
  <line x1="308" y1="180" x2="452" y2="180" stroke="#8593c4" stroke-width="4" marker-end="url(#arrow)"/>
  <g>
    <rect x="492" y="42" width="150" height="140" rx="18" fill="#fff" stroke="#e3e7f3" stroke-width="2"/>
    <rect x="537" y="72" width="60" height="78" rx="7" fill="#fff" stroke="#2e4ca6" stroke-width="4"/>
    <line x1="550" y1="92"  x2="584" y2="92"  stroke="#2e4ca6" stroke-width="4" stroke-linecap="round"/>
    <line x1="550" y1="106" x2="584" y2="106" stroke="#3f62c4" stroke-width="4" stroke-linecap="round"/>
    <line x1="550" y1="120" x2="576" y2="120" stroke="#3f62c4" stroke-width="4" stroke-linecap="round"/>
    <circle cx="636" cy="52" r="17" fill="#34a853"/>
    <path d="M628 52 l6 6 l10 -12" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>
    <text x="567" y="210" text-anchor="middle" font-size="18" font-weight="700" fill="#24305a">Resource</text>
  </g>
  <line x1="642" y1="150" x2="666" y2="168" stroke="#b8c0dd" stroke-width="2.5" stroke-dasharray="4 4"/>
  <g>
    <rect x="655" y="150" width="150" height="140" rx="18" fill="#fff" stroke="#e3e7f3" stroke-width="2"/>
    <circle cx="730" cy="212" r="31" fill="#fff" stroke="#2e4ca6" stroke-width="4"/>
    <line x1="730" y1="212" x2="730" y2="192" stroke="#2e4ca6" stroke-width="4" stroke-linecap="round"/>
    <line x1="730" y1="212" x2="746" y2="220" stroke="#2e4ca6" stroke-width="4" stroke-linecap="round"/>
    <circle cx="799" cy="160" r="17" fill="#34a853"/>
    <path d="M791 160 l6 6 l10 -12" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>
    <text x="730" y="318" text-anchor="middle" font-size="18" font-weight="700" fill="#24305a">Activity</text>
  </g>
  </g>
</svg>

### How it fits together

The editor is a two-part application: an Angular client that the employee interacts with, and a FastAPI service that exposes editor-specific endpoints and proxies the wider MEx Backend.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 989 310" width="989" style="max-width:100%;height:auto" role="img" aria-label="Request flow from the employee through the Angular client and Editor API to the MEx Backend">
<defs>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0 L10 5 L0 10 z" fill="#8593c4"/>
</marker>
</defs>
<rect width="989" height="310" fill="#eef1fa"/>
<g transform="translate(0,-10)">
<g>
<rect x="18" y="90" width="132" height="96" rx="16" fill="#fff" stroke="#e3e7f3" stroke-width="2"/>
<circle cx="84" cy="126" r="15" fill="#2e4ca6"/>
<path d="M60 160 Q60 138 84 138 Q108 138 108 160 Z" fill="#2e4ca6"/>
<text x="84" y="212" text-anchor="middle" font-size="17" font-weight="700" fill="#24305a">Employee</text>
</g>
<g>
<rect x="250" y="90" width="170" height="96" rx="16" fill="#fff" stroke="#e3e7f3" stroke-width="2"/>
<rect x="272" y="106" width="126" height="64" rx="10" fill="#fcebec" stroke="#e05c5c" stroke-width="2"/>
<text x="335" y="148" text-anchor="middle" font-size="26" font-weight="800" fill="#dd2c2c">ng</text>
<text x="335" y="212" text-anchor="middle" font-size="17" font-weight="700" fill="#24305a">Angular Client</text>
<text x="335" y="234" text-anchor="middle" font-size="13" fill="#8593c4">mex/editor/client</text>
</g>
<g>
<rect x="520" y="90" width="170" height="96" rx="16" fill="#fff" stroke="#e3e7f3" stroke-width="2"/>
<rect x="542" y="106" width="126" height="64" rx="10" fill="#eaf6ee" stroke="#34a853" stroke-width="2"/>
<line x1="560" y1="126" x2="650" y2="126" stroke="#34a853" stroke-width="4" stroke-linecap="round"/>
<line x1="560" y1="140" x2="636" y2="140" stroke="#34a853" stroke-width="4" stroke-linecap="round"/>
<line x1="560" y1="154" x2="646" y2="154" stroke="#34a853" stroke-width="4" stroke-linecap="round"/>
<text x="605" y="212" text-anchor="middle" font-size="17" font-weight="700" fill="#24305a">Editor API</text>
<text x="605" y="234" text-anchor="middle" font-size="13" fill="#8593c4">FastAPI · mex/editor/api</text>
</g>
<g>
<rect x="805" y="90" width="166" height="96" rx="16" fill="#fff" stroke="#e3e7f3" stroke-width="2"/>
<rect x="827" y="106" width="122" height="64" rx="10" fill="#f0f3fc" stroke="#2e4ca6" stroke-width="2"/>
<rect x="845" y="122" width="86" height="14" rx="5" fill="#2e4ca6"/>
<rect x="845" y="144" width="86" height="14" rx="5" fill="#b8c0dd"/>
<text x="888" y="212" text-anchor="middle" font-size="17" font-weight="700" fill="#24305a">MEx Backend</text>
<text x="888" y="234" text-anchor="middle" font-size="13" fill="#8593c4">metadata catalog</text>
</g>
<line x1="158" y1="138" x2="242" y2="138" stroke="#8593c4" stroke-width="4" marker-end="url(#arr)"/>
<text x="470" y="116" text-anchor="middle" font-size="13" fill="#8593c4">/api/v0</text>
<line x1="428" y1="138" x2="512" y2="138" stroke="#8593c4" stroke-width="4" marker-end="url(#arr)"/>
<text x="748" y="116" text-anchor="middle" font-size="13" fill="#8593c4">/api/v0/backend</text>
<line x1="698" y1="138" x2="797" y2="138" stroke="#8593c4" stroke-width="4" marker-end="url(#arr)"/>
</g>
</svg>

| Layer                                    | Responsibility                                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Angular Client** (`mex/editor/client`) | Renders forms, lists and detail views; talks to the Editor API                             |
| **Editor API** (`mex/editor/api`)        | Serves editor-specific data under `/api/v0`, proxies `mex.backend` under `/api/v0/backend` |
| **MEx Backend**                          | Stores and publishes the metadata catalog                                                  |

### What you'll find in these docs

This reference is generated from the source and organized by the usual Angular building blocks:

- **Components** – UI building blocks for editing resources and activities (forms, lists, detail panels)
- **Services** – data access, state, and API communication
- **Classes & Interfaces** – the shared models and contracts entities are built from
- **Modules** – how the above are grouped and wired together

Use the navigation to browse by type, or search for a specific symbol by name.

### Contributing to this documentation

Keep docstrings close to the code they describe — most of this reference is generated directly from TSDoc comments in the source. When adding or changing a public class, interface, or component, update its doc comment in the same change so this page stays accurate.

---

**Contact:** mex@rki.de · **License:** [MIT](https://github.com/robert-koch-institut/mex-editor-ng/blob/main/LICENSE)
