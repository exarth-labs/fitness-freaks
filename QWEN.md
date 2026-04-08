## Qwen Added Memories
- Project design system for detail pages and forms:

**Detail Pages Pattern:**
- Header: `d-flex flex-column me-3` with breadcrumb links using `text-muted text-decoration-none`
- Back button: `btn-primary shadow-sm`
- Profile card: `shadow-none border`, centered 150px image, stat columns with `h3` icons
- Section dividers: `<h6 class="text-uppercase text-muted fw-bold small">` with `<div class="flex-grow-1 border-bottom ms-3"></div>`
- KPI cards: `card kpi-card shadow-none border h-100`, content with `d-flex justify-content-between align-items-start`, icon in `kpi-icon bg-light`
- Tables: `table-hover` with `table-light` headers
- Empty states: `{% include 'include/globals/not-found.html' %}` in `text-center py-5` div

**Form Layout Pattern:**
- Use crispy forms with `FormHelper()` and `form_tag = False`
- Sectioned with `<h6 class="mb-3 text-primary"><i class="bx bx-*"></i>Section</h6>`
- Fields in `Row(Column('field', css_class='form-group col-md-X mb-0'))`
- Separators: `HTML('<hr class="my-4">')` between sections
- Boolean fields use check/cross icons in list views
