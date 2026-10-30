# Corpus manifest — heat-safety guidance

Source documents behind the `search_guidance` tool. Every chunk the agent retrieves
traces back to a row here.

**Accessed:** 25 September 2026
**Retrieval scope:** occupational heat risk for outdoor work in Victoria, Australia.

## Jurisdiction note

Victoria did not adopt the national model WHS laws. It operates under the Victorian
Occupational Health and Safety Act 2004 and the OHS Regulations 2017.

- **WorkSafe Victoria** material is the authoritative source for users of this tool.
- **Safe Work Australia** material is national guidance. It is useful and widely
  followed, but it is not law in Victoria.

This distinction is carried as metadata on every document so the agent can say which
kind of source an answer came from, and never present national guidance as a Victorian
legal requirement.

## Documents

| # | Title | Publisher | Authority in Victoria | File | Licence |
|---|---|---|---|---|---|
| 1 | Guide for managing the risks of working in heat | Safe Work Australia | National guidance, not law in Vic | `Guide for managing the risks of working in heat.pdf` | CC BY-NC 4.0 |
| 2 | Working in heat — frequently asked questions | Safe Work Australia | National guidance, not law in Vic | `swa-working-in-heat-faq.md` | CC BY-NC 4.0 |
| 3 | Checklist for managing the risks of heat in the workplace | Safe Work Australia | National guidance, not law in Vic | `swa-heat-checklist.md` | CC BY-NC 4.0 |
| 4 | Working in heat (guidance note, July 2012) | WorkSafe Victoria | Victorian regulator | `ISBN-Working-in-heat-2012-07.pdf` | `<confirm>` |
| 5 | Prevention and protection from heat illness | WorkSafe Victoria | Victorian regulator | `worksafevic-prevention-heat-illness.md` | `<confirm>` |
| 6 | Compliance code: Workplace amenities and working environment (Dec 2023) | WorkSafe Victoria | Victorian regulator — compliance code | `Compliance-code-Workplace-facilities-working-environment-2023-12.pdf` | `<confirm>` |

## Source URLs

1. https://www.safeworkaustralia.gov.au/doc/guide-managing-risks-working-heat
2. https://www.safeworkaustralia.gov.au/safety-topic/hazards/working-heat/frequently-asked-questions
3. https://www.safeworkaustralia.gov.au/safety-topic/hazards/working-heat/checklist-managing-risks-heat-workplace
4. https://www.worksafe.vic.gov.au/resources/working-heat
5. https://www.worksafe.vic.gov.au/prevention-and-protection-heat-illness
6. https://www.worksafe.vic.gov.au/resources/compliance-code-workplace-facilities-and-working-environment

## Document age and format notes

- Document 4 is the WorkSafe Victoria guidance note dated **July 2012**. It is still the
  document published on the WorkSafe resource page, but it is over a decade old. Check for
  a newer edition before any demo, and state the publication date whenever the agent cites
  it.
- Document 6 is the **December 2023** edition of the compliance code. A compliance code
  carries more weight than a guidance note: following it is deemed compliance with the
  duty it covers.
- Documents 2, 3 and 5 exist only as web pages, and were captured as Markdown (see
  Capture method below) rather than printed to PDF.
- Document 5 states explicitly that no maximum working temperature is set under the
  Victorian OHS Act 2004 or OHS Regulations 2017. This is the citable Victorian source
  behind the agent's refusal to give a stop-work threshold.

## What this corpus does not contain

- **No numeric stop-work temperature.** Neither the Victorian OHS Act nor the OHS
  Regulations set a maximum working temperature, and Safe Work Australia states that a
  single air-temperature cutoff is not an appropriate control, because risk depends on
  humidity, radiant heat, workload, clothing and acclimatisation.
- Consequence for the agent: it must not produce a threshold, a work/rest ratio or a
  stop-work rule, because no retrievable source supports one. It can return symptoms,
  control measures, and the duty to assess.
- **No clinical or first-aid treatment protocols** beyond what the guidance itself
  states. The agent refers to medical help rather than instructing on treatment.

## Capture method

- Documents 1, 4 and 6 were downloaded as published PDFs.
- Documents 2, 3 and 5 were captured from the live pages by `fetch_guidance_pages.py`
  using trafilatura 2.2.0, which extracts the main content and discards navigation,
  menus and footers. Each file carries a header with title, publisher, jurisdiction,
  source URL and access date.
- Printing those pages to PDF was tried first and rejected: the output was roughly half
  site navigation, and menu text inside a chunk competes with real guidance at retrieval
  time.
- Both Safe Work Australia pages returned nothing until the request was sent with a
  browser user-agent; the site rejects the default client.
- Manual cleanup after extraction: trailing "Related information" and external-link
  sections trimmed from document 5, and stray encoding artefacts removed from document 3.
  No wording inside any regulator's text was altered.

## Licence and use

- Safe Work Australia material is CC BY-NC 4.0: attribution required, non-commercial use
  only. This project is a non-commercial portfolio piece and attributes the source in
  every answer that uses it.
- WorkSafe Victoria terms to be confirmed from each page footer before publishing the
  repository.

## Maintenance

- Guidance is revised periodically. Re-check all six sources before any demo, and record
  the new access date here.
- If a document is replaced, keep the old row and mark it superseded rather than deleting
  it, so past agent answers remain explainable.
