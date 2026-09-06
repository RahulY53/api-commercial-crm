# Arkenstone CRM branding

The user-facing product name is **Arkenstone CRM**. The Python package,
Frappe app name, module identifiers, and database object names remain
`api_commercial` so the rebrand does not break migrations or integrations.

## Assets

- Full logo: `api_commercial/public/images/arkenstone-logo.png`
- Favicon: `api_commercial/public/images/arkenstone-favicon.png`

The logo is an original AI-generated gemstone mark. It is inspired by the
general literary idea of a radiant legendary white gemstone; it does not copy
a film prop, franchise wordmark, book-cover illustration, or existing logo.

Generation prompt:

> Create an original premium, vector-friendly enterprise CRM logo featuring a
> singular faceted white gemstone with ice-blue and silver refractions in a
> restrained midnight-navy geometric setting. Use a transparent background,
> no text, and a silhouette that remains legible at favicon size. Avoid film
> imagery, franchise lettering, characters, rings, crowns, and ornate crests.

## Configuration surfaces

`api_commercial.setup.seed_branding` applies the name, logo, and favicon to:

- FCRM Settings
- System Settings
- Website Settings
- Navbar Settings
- the API Commercial app launcher and workspace label

The setup routine replaces only empty values and known framework/default
branding. If an administrator later installs a different custom brand, normal
migrations preserve that choice.

Upstream Frappe and Frappe CRM package names, copyright notices, license files,
and source attribution remain unchanged.
