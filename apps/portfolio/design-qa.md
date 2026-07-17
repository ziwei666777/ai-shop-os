# Design QA

final result: blocked

Reference: user-provided poster layout screenshot with oversized top typography, central image overlap, and bottom-left manifest text.

Implemented checks:
- Production build passes with `npm.cmd run build:portfolio`.
- Hero source includes poster layout structure: `.posterTitleBlock`, `.posterVisual`, `.posterManifest`, and `.posterIntro`.
- Vite build uses relative asset paths so `dist/index.html` can be opened directly.

Blocked check:
- Browser screenshot comparison was blocked because the in-app browser automation policy rejected control of the local `file://` page.
