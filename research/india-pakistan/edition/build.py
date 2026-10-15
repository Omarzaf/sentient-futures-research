"""Build the approved editorial edition from exact CSV rows and the claim ledger."""

from __future__ import annotations

import csv
import hashlib
import html
import io
import json
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read original CSV strings without rounding or numerical coercion."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    """Escape text for authored HTML and attribute contexts."""
    return html.escape(str(value), quote=True)


def json_html(value: object) -> str:
    """Serialize JSON safely inside an inert HTML script."""
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def number_kind(value: object, kind: str = "year") -> str:
    """Mark a structural date or chapter without claiming it is a data value."""
    return f'<span data-number-kind="{kind}">{esc(value)}</span>'


class Edition:
    """Assemble source-bound charts, claims, prose and accessible table fallbacks."""

    def __init__(self) -> None:
        """Load local evidence and keep only explicit edition data selections."""
        self.sources = {r["source_id"]: r for r in read_csv(DATA / "sources.csv")}
        self.dataset_metadata = json.loads(
            (DATA / "dataset-manifest.json").read_text()
        )["datasets"]
        self.claims = read_csv(DATA / "edition_claims.csv")
        if any(row.get("audience") != "edition_and_report" for row in self.claims):
            raise ValueError("The edition claims ledger contains report-only material")
        self.used_sources: set[str] = set()
        self.chart_ids: set[str] = set()
        self.link_index = 0
        self.datasets: dict[str, list[dict[str, str]]] = {}
        self.claim_uses: list[str] = []
        self.numeric_sources: set[str] = set()
        self.reader_links = json.loads((DATA / "reader-links.json").read_text())
        status_path = DATA / "link-status.json"
        self.link_status = (
            json.loads(status_path.read_text()) if status_path.exists() else {}
        )

    def rows(self, dataset: str) -> list[dict[str, str]]:
        """Load an approved dataset, rejecting report-only annotation evidence."""
        if "newsframing" in dataset or "sentiment" in dataset:
            raise ValueError("News-framing numbers cannot enter the edition")
        if dataset not in self.datasets:
            self.datasets[dataset] = read_csv(DATA / f"{dataset}.csv")
        return self.datasets[dataset]

    def selected(self, dataset: str, filters: dict) -> list[dict[str, str]]:
        """Use exactly the verifier's equality or membership filter semantics."""
        return [
            row
            for row in self.rows(dataset)
            if all(
                (
                    row.get(key) in value["in"]
                    if isinstance(value, dict)
                    else row.get(key) == value
                )
                for key, value in filters.items()
            )
        ]

    def claim(self, dataset: str, filters: dict, column: str = "value") -> str:
        """Resolve a narrative value to one canonical value-operation claim."""
        wanted = self.selected(dataset, filters)
        if len(wanted) != 1:
            raise ValueError(f"Narrative claim must identify one row: {filters}")
        matches = [
            r
            for r in self.claims
            if r["dataset"] == dataset
            and r["value_column"] == column
            and r["operation"] == "value"
            and self.selected(dataset, json.loads(r["filter_json"])) == wanted
        ]
        if not matches:
            raise ValueError(f"Missing canonical claim: {dataset} {filters} {column}")
        # A source may offer multiple rounding variants; explicit shortest precision
        # remains a ledger-bound display, never a number produced by this builder.
        matches.sort(key=lambda row: (int(row["rounding"]), row["claim_id"]))
        row = matches[0]
        self.claim_uses.append(row["claim_id"])
        self.used_sources.update(json.loads(row["source_ids"]))
        self.numeric_sources.update(json.loads(row["source_ids"]))
        return f'<span data-claim="{esc(row["claim_id"])}">{esc(row["display"])}</span>'

    def link(self, url: str, label: str, prefix: str = "link") -> str:
        """Give every reader-operable link a unique stable identifier."""
        self.link_index += 1
        return f'<a id="{prefix}-{self.link_index:04}" href="{esc(url)}">{label}</a>'

    def source_link(self, source_id: str, label: str, prefix: str = "source") -> str:
        """Apply the audited reader route without altering the source-record URL."""
        row = self.sources[source_id]
        alternate = self.reader_links.get(source_id)
        status = self.link_status.get(source_id, {})
        if alternate:
            if (
                alternate.get("original_url") != row["url"]
                or alternate.get("status") != 200
            ):
                raise ValueError(
                    f"Reader-link identity or access mismatch: {source_id}"
                )
            link = self.link(alternate["url"], label, prefix)
            return link.replace(
                " href=", f' title="{esc(alternate["reason"])}" href=', 1
            )
        if status.get("inactive") is True:
            if source_id in self.numeric_sources:
                raise ValueError(
                    f"Cannot deactivate a used numeric source: {source_id}"
                )
            message = "Access unavailable at last check; original URL retained in source record"
            return f'<span class="unavailable-source" title="{esc(message)}" aria-describedby="source-access-{esc(source_id)}">{label}</span>'
        return self.link(row["url"], label, prefix) if row["url"] else label

    def source_access_note(self, source_id: str) -> str:
        """Explain alternate copies and unavailable routes in readable, bounded language."""
        if source_id == "S01" and source_id in self.reader_links:
            return "Reader link opens the structured NLM abstract record. Abstract access supports only the statements verified there; it does not provide the full questionnaire."
        if source_id == "S06" and source_id in self.reader_links:
            return "Reader link opens a third-party Semantic Scholar mirror of the published paper. The title and DOI were matched; disputed outcome wording remains unresolved."
        if source_id in self.reader_links:
            return "Reader link opens a checked accessible copy of the same source. The original URL remains in the source record and download."
        if self.link_status.get(source_id, {}).get("inactive") is True:
            return "Access unavailable at last check; original URL retained in source record."
        return ""

    def source(self, source_id: str, named: bool = False) -> str:
        """Bind a citation label to exact source metadata, preserving its grade."""
        row = self.sources[source_id]
        self.used_sources.add(source_id)
        field = "title" if named or not row.get("publisher") else "publisher"
        label = self.source_field(source_id, field)
        link = self.source_link(source_id, label)
        year = (
            f'<span data-source-id="{esc(source_id)}" data-source-column="year">{esc(row["year"])}</span>'
            if row.get("year")
            else "date unresolved"
        )
        return f'{link} <span class="tier">Source tier {esc(row["tier"])}</span> <span class="source-year">Release: {year}</span>'

    def source_field(self, source_id: str, column: str) -> str:
        """Preserve an exact source-metadata field in visible narrative."""
        self.used_sources.add(source_id)
        return f'<span data-source-id="{esc(source_id)}" data-source-column="{esc(column)}">{esc(self.sources[source_id][column])}</span>'

    def named_citations(self, labels: list[tuple[str, str]]) -> str:
        """Keep dense chart citations readable while retaining release and source grade."""
        citations = []
        for source_id, label in labels:
            row = self.sources[source_id]
            self.used_sources.add(source_id)
            link = self.source_link(source_id, esc(label), "named-source")
            year = f' · {self.source_field(source_id, "year")}' if row["year"] else ""
            citations.append(
                f'{link}{year} <span class="tier">Source tier {esc(row["tier"])}</span>'
            )
        return " · ".join(citations)

    def csv_download(
        self, rows: list[dict[str, str]], columns: list[str], filename: str, label: str
    ) -> str:
        """Create a local CSV download from an explicit public-field projection."""
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        link = self.link(
            "data:text/csv;charset=utf-8," + quote(buffer.getvalue()), label, "download"
        )
        return link.replace(" href=", f' download="{esc(filename)}" href=', 1)

    def chart(
        self,
        key: str,
        dataset: str,
        filters: dict,
        columns: list[str],
        title: str,
        unit: str,
        caveat: str,
        kind: str = "line",
        options: dict | None = None,
        extra_sources: list[str] | None = None,
        heading_html: str | None = None,
        class_name: str = "",
        observation_html: str = "",
        content_html: str = "",
        citation_note: str = "",
    ) -> str:
        """Embed exact ordered source strings alongside the exact accessible table."""
        if key in self.chart_ids:
            raise ValueError(f"Repeated chart: {key}")
        rows = self.selected(dataset, filters)
        if not rows:
            raise ValueError(f"Empty chart: {key} {filters}")
        if any(r.get("evidence_status", "").upper().startswith("HELD") for r in rows):
            raise ValueError(f"Held evidence selected for chart: {key}")
        projected = [{column: row[column] for column in columns} for row in rows]
        row_sources: set[str] = set()
        for row in rows:
            for column in self.dataset_metadata[dataset]["primary_source_columns"]:
                value = row[column].strip()
                values = (
                    json.loads(value)
                    if value.startswith("[")
                    else value.replace("|", ";").split(";")
                )
                row_sources.update(
                    source_id.strip() for source_id in values if source_id.strip()
                )
        sources = sorted(row_sources | set(extra_sources or []))
        self.chart_ids.add(key)
        self.used_sources.update(sources)
        if kind in {
            "line",
            "paired",
            "bars",
            "map",
            "stack",
            "reference",
            "range",
            "dots",
            "forecast",
            "benchmark-history",
            "coverage",
            "outcomes",
        }:
            self.numeric_sources.update(sources)
        spec = {
            "dataset": dataset,
            "filter": filters,
            "columns": columns,
            "rows": projected,
            "title": title,
            "unit": unit,
            "source_ids": sources,
            "caveat": caveat,
        }
        option_attr = esc(json.dumps(options or {}, separators=(",", ":")))
        headings = "".join(f'<th scope="col">{esc(column)}</th>' for column in columns)
        cells = "".join(
            "<tr>"
            + "".join(f"<td>{esc(row[column])}</td>" for column in columns)
            + "</tr>"
            for row in projected
        )
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=columns)
        writer.writeheader()
        writer.writerows(projected)
        download = self.link(
            "data:text/csv;charset=utf-8," + quote(buffer.getvalue()),
            "Download these source rows",
            "download",
        )
        download = download.replace(" href=", f' download="{key}.csv" href=', 1)
        citation = citation_note or ' <span aria-hidden="true">·</span> '.join(
            self.source(s) for s in sources
        )
        if any(row.get("tier") == "derived" for row in rows):
            citation = '<span class="tier">Row tier derived</span> · ' + citation
        return f"""<figure class="evidence-chart {esc(class_name)}" data-chart-container="{key}">
<h3>{heading_html or esc(title)}</h3><p class="fig-sub" data-chart-unit="{key}">{esc(unit)}</p>{f'<p class="observation-period">{observation_html}</p>' if observation_html else ''}
<div class="chart-visual" id="visual-{key}" data-render="{kind}" data-options="{option_attr}" aria-label="{esc(title)}">{content_html}</div>
<p class="chart-caveat">{esc(caveat)}</p><p class="src" data-chart-source="{key}">{citation}</p>
<details class="chart-data"><summary id="table-toggle-{key}">Show data</summary><div class="table-wrap" id="table-region-{key}" tabindex="0" role="region" aria-label="{esc(title)} source table"><table data-chart-table="{key}"><caption class="sr-only">{esc(title)}</caption><thead><tr>{headings}</tr></thead><tbody>{cells}</tbody></table></div><p class="download">{download}</p></details>
<script type="application/json" data-chart="{key}">{json_html(spec)}</script></figure>"""

    def section(
        self,
        number: int,
        title: str,
        lede: str,
        body: str,
        packages: str = "P03",
        extra_class: str = "",
    ) -> str:
        """Mark real inventory coverage and a stable chapter anchor."""
        key = f"chapter-{number:02}"
        anchor = self.link(
            f"#{key}",
            '<span aria-hidden="true">↗</span><span class="sr-only">Link to this chapter</span>',
            "chapter-anchor",
        )
        return f"""<section id="{key}" data-chapter="{number}" data-packages="{packages} P12" data-title="{esc(title)}" class="chapter {extra_class}"><div class="ch-head"><div class="ch-num">Chapter {number_kind(str(number).zfill(2), "chapter")}</div><h2>{esc(title)} {anchor}</h2><p class="lede">{lede}</p></div>{body}</section>"""

    def supply_claim(self, country: str, item: str) -> str:
        """Select the headline's exact official food-balance cell."""
        return self.claim(
            "meat_supply_national",
            {
                "country": country,
                "item": item,
                "year": "2023",
                "metric": "food_supply_quantity",
            },
        )

    def risk_claim(self, country: str, indicator: str) -> str:
        """Select the named contemporary risk proxy without combining surveys."""
        source = (
            "jme_country_model_march2026"
            if indicator == "under5_stunting"
            else "fao_sofi_2025"
        )
        return self.claim(
            "deficiency_population",
            {
                "country": country,
                "year": "2024",
                "indicator": indicator,
                "source_id": source,
            },
        )

    def opening(self) -> str:
        """Keep the approved title, paired-number layout and disclosure."""
        pairs = []
        definitions = [
            (
                "poultry",
                "Poultry availability",
                "meat_supply_national",
                {
                    "item": "Poultry Meat",
                    "metric": "food_supply_quantity",
                    "year": "2023",
                },
                "kg per person per year",
                "value",
                "Supply in a food balance sheet, not measured individual intake.",
            ),
            (
                "pulses",
                "Pulse availability",
                "meat_supply_national",
                {"item": "Pulses", "metric": "food_supply_quantity", "year": "2023"},
                "kg per person per year",
                "value",
                "Source food categories and national averages do not describe every diet.",
            ),
            (
                "affordability",
                "A healthy diet is out of reach",
                "deficiency_population",
                {
                    "indicator": "unable_to_afford_healthy_diet",
                    "source_id": "fao_sofi_2025",
                    "year": "2024",
                },
                "% of the population",
                "value",
                "Modelled economic access to a healthy diet, not a protein diagnosis.",
            ),
            (
                "stunting",
                "Child stunting remains widespread",
                "deficiency_population",
                {
                    "indicator": "under5_stunting",
                    "source_id": "jme_country_model_march2026",
                    "year": "2024",
                },
                "% of children under five",
                "value",
                "A modelled growth indicator; its causes and denominator differ from affordability.",
            ),
        ]
        for key, title, dataset, filters, unit, column, caveat in definitions:
            observation = f'Observation year: {number_kind(filters["year"])}.'
            if key == "affordability":
                observation += " The State of Food Security and Nutrition in the World (SOFI) reports this modelled economic-access measure."
            elif key == "stunting":
                observation += " Joint Child Malnutrition Estimates (JME), produced by UNICEF, the World Health Organization and the World Bank."
            numbers = "".join(
                f'<div class="n {"in" if country == "India" else "pk"}">{self.claim(dataset, {**filters, "country": country}, column)}<small>{country}</small></div>'
                for country in ("India", "Pakistan")
            )
            chart = self.chart(
                f"opening-{key}",
                dataset,
                filters,
                ["country", "year", column, "unit", "source_id", "tier"],
                title,
                unit,
                caveat,
                "paired",
                {"value": column},
                class_name="pair",
                observation_html=observation,
            )
            chart = chart.replace(
                '<div class="chart-visual"',
                f'<div class="nums">{numbers}</div><div class="chart-visual"',
                1,
            )
            pairs.append(chart)
        return f"""<section class="hero chapter" id="chapter-01" data-chapter="1" data-packages="P03 P12" data-title="Two neighbours, one protein question"><div class="kicker">Sentient Futures · Research edition</div><h1>Two neighbours,<br><em>one protein question</em></h1><p class="stand">Food supply differs across India and Pakistan. Affordability, dietary practice and food regulation complicate the case for new proteins. This edition follows the evidence from national food balances to the questions that still need consumer data.</p><div class="byline"><span>By <strong>Muhammad Umar Zafar</strong></span><span>Evidence reviewed {number_kind("2026-10-13", "date")}</span><span class="pill">AI-assisted · Human verification pending · human scholarly review pending</span></div><h2 class="sr-only">Headline indicators</h2><div class="pairs">{''.join(pairs)}</div></section>"""

    def findings(self) -> str:
        """Write findings from ledger-bound numbers and scoped qualitative results."""
        entries = [
            (
                4,
                f"Pakistan's poultry availability was {self.supply_claim('Pakistan', 'Poultry Meat')} kg per person in {number_kind('2023')}, compared with India's {self.supply_claim('India', 'Poultry Meat')} kg.",
            ),
            (
                4,
                f"India's pulse availability was {self.supply_claim('India', 'Pulses')} kg per person in {number_kind('2023')}; Pakistan's was {self.supply_claim('Pakistan', 'Pulses')} kg.",
            ),
            (
                8,
                f"The healthy-diet affordability indicator was {self.risk_claim('India', 'unable_to_afford_healthy_diet')}% in India and {self.risk_claim('Pakistan', 'unable_to_afford_healthy_diet')}% in Pakistan in {number_kind('2024')}.",
            ),
            (
                7,
                "India publishes intake per energy-based consumer unit. Comparing it with an adult protein reference is a descriptive scenario.",
            ),
            (
                7,
                "Pakistan's complete dietary-protein total remains missing. The revised physical calculations cover named food subsets.",
            ),
            (
                9,
                "The forecasting benchmark measures national protein supply. Its validation does not establish an alternative-protein adoption forecast.",
            ),
            (
                10,
                "A company announcement, consultation or future-effective rule does not establish current sales or product approval.",
            ),
            (
                11,
                "The consumer studies cover different countries, products and outcomes. Their samples cannot be pooled into a regional adoption rate.",
            ),
            (
                12,
                "Religious conditions, certification, food approval and purchase are separate questions for cultivated chicken.",
            ),
        ]
        items = "".join(
            f'<li><p>{text}</p>{self.link(f"#chapter-{chapter:02}", "Read the evidence", "finding")}</li>'
            for chapter, text in entries
        )
        return self.section(
            2,
            "What the evidence supports",
            "The strongest findings concern supply and access. Evidence about acceptance and adoption is narrower.",
            f'<ol class="findings prose">{items}</ol>',
            "P03 P04 P08 P07 P09",
        )

    def theory(self) -> str:
        """Present the brief as a conceptual framework, not an identified causal model."""
        drivers = [
            (
                "Religious norms",
                "Food acceptability may depend on ingredients, process and religious interpretation.",
            ),
            (
                "Caste and class",
                "Eating practices and commensality vary within countries and social groups.",
            ),
            (
                "Affordability",
                "Price and access shape the choices that households can consider.",
            ),
            (
                "Cities and diaspora",
                "Location and migration alter food availability and social context.",
            ),
            (
                "Policy and certification",
                "Institutional pathways affect what may be produced, labelled and sold.",
            ),
        ]
        notes = "".join(
            f"<div><b>{esc(title)}</b>{esc(note)}</div>" for title, note in drivers
        )
        body = f"""<div class="theory"><div id="theory-diagram" class="concept-diagram" role="img" aria-label="Conceptual questions: religious norms, caste and class, affordability, cities and diaspora, and policy and certification connect to acceptability. Trial, purchase and habitual use are separate outcomes."></div><div class="theory-grid">{notes}</div><p class="note">This diagram organizes research questions. It does not estimate causal effects or assume that stated interest becomes a purchase.</p><p class="src">Framework: {self.source('package_P01')}</p></div>"""
        return self.section(
            3,
            "Questions linking acceptability, trial and habitual use",
            "The research brief connects dietary context with distinct stages of possible adoption. Each stage requires its own evidence.",
            body,
            "P01",
        )

    def supply(self) -> str:
        """Render the approved scrolly with separate source-method panels."""
        steps = []
        for key, item, title in [
            ("poultry", "Poultry Meat", "Pakistan supplies more poultry per person"),
            ("pulses", "Pulses", "India supplies more pulses per person"),
            (
                "milk",
                "Milk - Excluding Butter",
                "Milk contributes substantial food availability",
            ),
        ]:
            prose = f"In {number_kind('2023')}, the balance-sheet value was {self.supply_claim('India', item)} kg per person in India and {self.supply_claim('Pakistan', item)} kg in Pakistan."
            figure = self.chart(
                f"supply-{key}",
                "meat_supply_national",
                {"item": item, "metric": "food_supply_quantity"},
                ["country", "year", "item", "value", "unit", "source_id", "tier"],
                title,
                "kg per person per year",
                "National availability is not observed household intake or retail demand.",
                "line",
                {"x": "year", "y": "value", "series": "country"},
            )
            steps.append(
                f'<div class="supply-step" data-scrolly-step="{key}"><div class="step-copy"><h3>{title}</h3><p>{prose}</p></div>{figure}</div>'
            )
        outlook = self.chart(
            "supply-outlook",
            "meat_supply_national",
            {
                "item": "Poultry meat",
                "metric": {
                    "in": [
                        "oecd_human_consumption_historical_or_base_estimate",
                        "oecd_human_consumption_projection",
                    ]
                },
            },
            ["country", "year", "metric", "value", "unit", "source_id", "tier"],
            "The Outlook describes a separate consumption series",
            "kg per person per year, retail weight",
            "The OECD–FAO series has a different weight basis and is not spliced into FAOSTAT food availability.",
            "line",
            {"x": "year", "y": "value", "series": "country", "projection": True},
        )
        steps.append(
            f'<div class="supply-step" data-scrolly-step="outlook"><div class="step-copy"><h3>The Outlook has its own method</h3><p>Historical or base estimates and projections stay in this separate panel. A projected series is not an observation of future demand.</p></div>{outlook}</div>'
        )
        multiples = []
        for key, item, title in [
            ("poultry", "Poultry Meat", "Poultry"),
            ("bovine", "Bovine Meat", "Bovine meat"),
            ("mutton", "Mutton & Goat Meat", "Mutton and goat"),
            ("fish", "Fish, Seafood", "Fish and seafood"),
            ("eggs", "Eggs", "Eggs"),
            ("milk", "Milk - Excluding Butter", "Milk excluding butter"),
            ("pulses", "Pulses", "Pulses"),
        ]:
            multiples.append(
                self.chart(
                    f"multiple-{key}",
                    "meat_supply_national",
                    {"item": item, "metric": "food_supply_quantity"},
                    ["country", "year", "value", "source_id", "tier"],
                    title,
                    "kg per person per year",
                    "Independent zero-based scale; supply is not individual intake.",
                    "line",
                    {"x": "year", "y": "value", "series": "country", "mini": True},
                )
            )
        body = (
            '<div class="supply-scrolly">'
            + "".join(steps)
            + '</div><div class="multiples"><h3>The food categories have different scales</h3><div class="grid7">'
            + "".join(multiples)
            + "</div></div>"
        )
        return self.section(
            4,
            "Pakistan supplies more poultry; India supplies more pulses",
            "Food balances show national availability after the source's accounting adjustments. They do not establish what a particular person eats.",
            body,
        )

    def regions(self) -> str:
        """Keep survey populations, boundary matches and country scales separate."""
        india = self.chart(
            "regions-india",
            "meat_regional",
            {
                "country": "India",
                "source_id": "nfhs5_india_2019_21",
                "indicator": "women_15_49_fish_chicken_or_meat_at_least_weekly",
                "region_type": {"in": ["state", "union_territory"]},
            },
            [
                "region",
                "year",
                "period",
                "denominator",
                "fieldwork_start",
                "fieldwork_end",
                "value",
                "unit",
                "residence",
                "boundary_shape_id",
                "boundary_match_status",
                "source_id",
                "tier",
            ],
            "Reported eating frequency varies across Indian states",
            "% of women aged fifteen to forty-nine",
            "Women reporting fish, chicken or meat at least weekly, including daily responses. The National Family Health Survey (NFHS-5) measures frequency, not meat weight. Residence splits are unavailable in this state series.",
            "map",
            {"country": "India", "value": "value"},
            ["geoboundaries_ind_adm1_9469f09"],
            observation_html=f'Fieldwork: {number_kind("2019–2021")}; regional months are retained in the source data.',
        )
        pakistan = self.chart(
            "regions-pakistan",
            "meat_regional",
            {
                "country": "Pakistan",
                "source_id": "pakistan_hies_2024_25_table23",
                "indicator": "monthly_per_capita_chicken_meat_consumption",
                "quintile": "all",
                "region_type": "province",
            },
            [
                "region",
                "year",
                "value",
                "unit",
                "residence",
                "boundary_shape_id",
                "boundary_match_status",
                "source_id",
                "tier",
            ],
            "Published chicken quantities differ across provinces",
            "kg per person per month",
            "These are household-derived per-capita quantities. The residence selector changes source rows, not a protein-intake ranking.",
            "map",
            {
                "country": "Pakistan",
                "value": "value",
                "residenceControl": "regions-pakistan-residence",
            },
            ["geoboundaries_pak_adm1_9469f09"],
            observation_html=f'Household Integrated Economic Survey (HIES), {number_kind("2024–2025")}.',
        )
        controls = '<div class="local-controls"><label for="regions-pakistan-residence">Pakistan HIES residence<select id="regions-pakistan-residence"><option value="all">All households</option><option value="rural">Rural</option><option value="urban">Urban</option></select></label></div>'
        nns = self.chart(
            "regions-nns-context",
            "meat_regional",
            {
                "country": "Pakistan",
                "source_id": "pakistan_nns2018_volume1",
                "indicator": "women_15_49_minimum_dietary_diversity",
                "residence": "all",
            },
            [
                "region",
                "year",
                "value",
                "unit",
                "residence",
                "boundary_match_status",
                "denominator",
                "source_id",
                "tier",
            ],
            "Diet diversity is another survey measure",
            "% of women aged fifteen to forty-nine",
            "Minimum dietary diversity means eating at least five of ten food groups during the previous day or night. All-residence estimates from Pakistan's National Nutrition Survey. Khyber Pakhtunkhwa (KP) and its Newly Merged Districts (KP-NMD) remain separate observations; they are not assigned to one combined boundary.",
            "bars",
            {"country": "Pakistan", "label": "region", "value": "value"},
            observation_html=f'Fieldwork: April {number_kind("2018")} to January {number_kind("2019")}.',
        )
        distribution = self.source("geoboundaries_distribution_licence")
        distribution_license = self.source_field(
            "geoboundaries_distribution_licence", "license"
        )
        india_license = self.source_field("geoboundaries_ind_adm1_9469f09", "license")
        pakistan_license = self.source_field(
            "geoboundaries_pak_adm1_9469f09", "license"
        )
        body = f'<div class="wide">{controls}<div class="maps">{india}{pakistan}</div><p class="note">The maps use separate country scales and incompatible measures. Jammu and Kashmīr, Ladākh, Azad Kashmir and Gilgit-Baltistan are hatched without data colour. Available values remain in tooltips and tables. Boundary depictions do not assert sovereignty.</p><p class="note">Boundary distribution: {distribution}, licensed under {distribution_license}. Original country-source metadata records {india_license} for India and {pakistan_license} for Pakistan.</p>{nns}</div>'
        return self.section(
            5,
            "Regional differences need their survey definitions",
            "Compare regions within a source. A frequency percentage and a household food quantity cannot measure the same cross-border difference.",
            body,
        )

    def diet(self) -> str:
        """Show India protein composition and Pakistan food quantities independently."""
        india = self.chart(
            "diet-india",
            "diet_composition",
            {"country": "India"},
            [
                "residence",
                "fractile",
                "food_group",
                "value",
                "unit",
                "period",
                "source_id",
                "tier",
            ],
            "Cereals contribute a large share of recorded dietary protein",
            "% of total protein intake",
            "Fractiles rank the population by monthly per capita consumption expenditure within rural or urban areas. Lower-ranked groups spend less per person; rural and urban groups are not pooled.",
            "stack",
            {"residenceControl": "diet-india-residence"},
        )
        pakistan = self.chart(
            "diet-pakistan",
            "diet_composition",
            {
                "country": "Pakistan",
                "food_group": "chicken_meat",
                "residence": "all",
                "quintile": {"in": ["Q1", "Q2", "Q3", "Q4", "Q5"]},
            },
            ["quintile", "food_group", "value", "unit", "period", "source_id", "tier"],
            "Chicken quantity rises across published expenditure quintiles",
            "kg per person per month",
            "These are published food quantities, not dietary-protein amounts or independently formed model quintiles.",
            "bars",
            {"country": "Pakistan", "label": "quintile", "value": "value"},
        )
        body = (
            '<div class="wide"><div class="local-controls"><label for="diet-india-residence">India residence<select id="diet-india-residence"><option value="rural">Rural</option><option value="urban">Urban</option></select></label></div><div class="two-panels">'
            + india
            + pakistan
            + "</div></div>"
        )
        return self.section(
            6,
            "Food quantities and protein shares answer different questions",
            "India reports how food groups contribute to protein intake. Pakistan's major-food table reports native quantities by expenditure group.",
            body,
        )

    def protein(self) -> str:
        """Keep the incomplete Pakistan subtotal outside adult-reference arithmetic."""
        india = self.chart(
            "protein-india",
            "protein_gap",
            {"country": "India"},
            [
                "survey_group",
                "residence",
                "fractile",
                "reference_type",
                "reference_weight_kg",
                "intake_g",
                "requirement_g",
                "gap_g",
                "unit",
                "comparison_status",
                "source_id",
                "tier",
            ],
            "India's consumer-unit means sit beside adult reference scenarios",
            "published g per consumer unit per day; adult reference in g per day",
            "Fractiles rank the population by monthly per capita consumption expenditure within rural or urban areas. Consumer units scale energy needs, not protein requirements. Neither scenario establishes individual adequacy or deficiency prevalence.",
            "reference",
            {
                "referenceControl": "protein-reference",
                "weightControl": "protein-weight",
                "residenceControl": "protein-residence",
            },
            ["icmr_nin_dietary_guidelines_2024"],
        )
        pakistan = self.chart(
            "protein-pakistan",
            "protein_model_method_ranges",
            {"group": "all_all"},
            [
                "scope",
                "low",
                "high",
                "low_method",
                "high_method",
                "unit",
                "range_type",
                "source_id",
                "tier",
            ],
            "Pakistan has conditional subtotals, not a complete protein total",
            "g per person per day",
            "These are extrema of named physical-conversion cases, not confidence intervals or bounds on true intake. Missing foods and unresolved product forms remain.",
            "range",
            {"country": "Pakistan", "label": "scope", "low": "low", "high": "high"},
            citation_note="Quantity input and composition references: "
            + self.named_citations(
                [
                    (
                        "pakistan_hies_2024_25_table23",
                        "Pakistan HIES major-food quantities",
                    ),
                    (
                        "pakistan_food_composition_2001",
                        "Pakistan Food Composition Table",
                    ),
                    ("bangladesh_fct_2013", "Bangladesh Food Composition Table"),
                    ("india_ifct_2017", "Indian Food Composition Tables"),
                    ("usda_fdc_sr_legacy_2018", "USDA SR Legacy composition data"),
                    ("fao_infoods_density_v2_2012", "FAO INFOODS density database"),
                ]
            )
            + ". Conversion and interpretation methods: "
            + self.named_citations(
                [
                    (
                        "fao_infoods_food_matching_v1_2_2012",
                        "FAO INFOODS food matching",
                    ),
                    (
                        "usda_sr_legacy_documentation_2018",
                        "USDA SR Legacy documentation",
                    ),
                    ("pbs_hies_2024_25_manual", "HIES survey manual"),
                    (
                        "fao_hces_technical_notes",
                        "FAO household-survey technical notes",
                    ),
                    (
                        "worldbank_adept_food_security_2014",
                        "World Bank food-security analysis",
                    ),
                ]
            )
            + ". These sources support conditional conversion choices, not a measured complete Pakistan diet.",
        )
        controls = '<div class="local-controls"><label for="protein-reference">India reference<select id="protein-reference"><option value="EAR">EAR · primary</option><option value="RDA">RDA · sensitivity</option></select></label><label for="protein-weight">Adult weight<select id="protein-weight"><option value="60">Reference adult</option><option value="55">Lighter adult sensitivity</option><option value="65">Heavier adult sensitivity</option></select></label><label for="protein-residence">India residence<select id="protein-residence"><option value="rural">Rural</option><option value="urban">Urban</option></select></label></div>'
        body = f'<div class="wide">{controls}<div class="two-panels">{india}{pakistan}</div><div class="rule-box"><div><b>No deficiency rate</b><span>A household group mean cannot identify how many individuals fall below their physiological needs. Pakistan\'s partial subtotal is excluded from all reference comparisons. The previous pooled-basket full total is withdrawn.</span></div></div></div>'
        return self.section(
            7,
            "A reference comparison is not a deficiency diagnosis",
            "The estimated average requirement (EAR) is the primary adult scenario. The recommended dietary allowance (RDA) is a labelled sensitivity. Both require care with the denominator.",
            body,
            "P03 P04",
        )

    def risks(self) -> str:
        """Retain each nutrition proxy's source series and denominator."""
        affordability = self.chart(
            "risk-affordability",
            "deficiency_population",
            {
                "indicator": "unable_to_afford_healthy_diet",
                "source_id": "fao_sofi_2025",
            },
            ["country", "year", "value", "unit", "denominator", "source_id", "tier"],
            "Healthy-diet affordability has improved more in India",
            "% of the population",
            "Modelled economic access measures a different problem from growth outcomes or dietary-protein adequacy.",
            "line",
            {"x": "year", "y": "value", "series": "country"},
            observation_html=f'Selected observation years: {number_kind("2017–2024")}. The State of Food Security and Nutrition in the World (SOFI) reports this economic-access measure.',
        )
        stunting = self.chart(
            "risk-stunting",
            "deficiency_population",
            {
                "indicator": "under5_stunting",
                "source_id": "jme_country_model_march2026",
                "year": "2024",
            },
            ["country", "year", "value", "unit", "denominator", "source_id", "tier"],
            "Modelled child-stunting rates are similar",
            "% of children under five",
            "Each dot represents a percentage point; a fractional final dot preserves the published rate. Stunting is not a direct protein-deficiency measure.",
            "dots",
            observation_html=f'Observation year: {number_kind("2024")}. Joint Child Malnutrition Estimates (JME), produced by UNICEF, the World Health Organization and the World Bank.',
        )
        undernourishment = self.chart(
            "risk-undernourishment",
            "deficiency_population",
            {
                "indicator": "prevalence_of_undernourishment",
                "source_id": "fao_sofi_2025",
            },
            [
                "country",
                "year",
                "period",
                "value",
                "unit",
                "denominator",
                "source_id",
                "tier",
            ],
            "Dietary-energy risk persists in both countries",
            "% of the population",
            "The source period is a multi-year estimate. It is not a point-year nutrition survey.",
            "line",
            {"x": "year", "y": "value", "series": "country"},
            observation_html=f'Three-year observation periods: {number_kind("2004–2006")} and {number_kind("2022–2024")}.',
        )
        body = f'<div class="wide"><div class="two-panels">{affordability}{stunting}</div>{undernourishment}<div class="rule-box"><div><b>Do not add</b><span>Affordability, undernourishment and stunting overlap and use different denominators. Adding them would double-count people and combine different risks.</span></div></div></div>'
        return self.section(
            8,
            "Nutrition risks overlap without becoming one measure",
            "The figures describe economic access, dietary-energy risk and child growth. None is a direct count of people with protein deficiency.",
            body,
        )

    def benchmark(self) -> str:
        """Show each experimental forecast separately from observed national supply."""
        figures = []
        for country in ("India", "Pakistan"):
            for series in ("animal", "total"):
                key = f"benchmark-{country.lower()}-{series}"
                figures.append(
                    self.chart(
                        key,
                        "benchmark_forecast",
                        {"country": country, "series": series},
                        [
                            "country",
                            "series",
                            "year",
                            "model",
                            "point",
                            "lower80",
                            "upper80",
                            "unit",
                            "source_id",
                            "tier",
                        ],
                        f"{country}: projected {series} protein supply",
                        "g per person per day",
                        "Exploratory supply forecast with a nominal interval. It does not predict alternative-protein sales or adoption.",
                        "forecast",
                        {
                            "x": "year",
                            "y": "point",
                            "low": "lower80",
                            "high": "upper80",
                            "country": country,
                        },
                    )
                )
        annual = self.chart(
            "benchmark-observations",
            "benchmark_annual",
            {},
            ["country", "series", "year", "value", "unit", "source_id", "tier"],
            "The benchmark starts from historical supply",
            "g per person per day",
            "Animal-source protein is part of total protein. These series are not independent quantities to add.",
            "benchmark-history",
            {"x": "year", "y": "value"},
        )
        coverage = self.chart(
            "benchmark-coverage",
            "benchmark_coverage",
            {},
            [
                "country",
                "series",
                "covered",
                "n_evaluated",
                "nominal_level",
                "split",
                "unit",
                "source_id",
                "tier",
            ],
            "Interval coverage differs sharply in the held-out cells",
            "covered evaluation cells out of evaluated cells",
            "The evaluation set is small and overlapping across model horizons. Observed coverage does not establish future calibration.",
            "coverage",
        )
        return self.section(
            9,
            "Supply forecasts remain exploratory",
            "The benchmark carries national food-balance histories forward. Supply is the measured outcome; adoption still lacks a matched baseline.",
            '<div class="wide">'
            + annual
            + '<div class="two-panels">'
            + "".join(figures)
            + "</div>"
            + coverage
            + "</div>",
            "P08",
        )

    def alternatives(self) -> str:
        """Separate crop context, dated firm evidence and legal instrument status."""
        feed = self.chart(
            "alternative-feedstock",
            "altprotein_sources",
            {
                "source_type": "pulses_total",
                "metric": "crop_production_potential_feedstock_context",
            },
            ["country", "year", "value", "unit", "source_id", "tier"],
            "Crop tonnage provides context, not an alternative-protein market size",
            "tonnes of whole pulses",
            "There is no measured allocation from these crops to alternative-meat products.",
            "line",
            {"x": "year", "y": "value", "series": "country"},
        )
        company = self.chart(
            "alternative-companies",
            "altprotein_companies",
            {},
            [
                "company",
                "country",
                "category",
                "inclusion_status",
                "status",
                "status_evidence_date",
                "closure_reported_date",
                "closure_effective_date",
                "application_date",
                "source_id",
                "tier",
            ],
            "Company evidence records activity and closures at different dates",
            "dated source evidence; undated entries remain undated",
            "A closure report is not the closure event date. Food, adjacent ingredients and feed-only activity are not one operating-company census.",
            "companies",
        )
        policy = self.chart(
            "alternative-policy",
            "altprotein_policy",
            {},
            [
                "country",
                "policy",
                "policy_date",
                "publication_date",
                "application_date",
                "effective_date",
                "status",
                "freshness",
                "pathway",
                "source_id",
                "tier",
            ],
            "A policy pathway is not a product approval",
            "instrument, publication, filing and effective dates remain distinct",
            "Consultations and future-effective amendments keep their stated status. Punjab's functional-food scope does not establish blanket cultivated-meat approval.",
            "policy",
        )
        return self.section(
            10,
            "Alternative proteins have pathways, but little measured demand",
            "The evidence records feedstocks, company events and regulatory instruments. It does not establish current sales across either country.",
            f'<div class="wide"><p class="note">The Food Safety and Standards Authority of India (FSSAI) regulates food. BioE3 is India\'s Biotechnology for Economy, Environment and Employment policy; an innovation-policy pathway and a food-product authorization answer different questions.</p>{feed}{company}{policy}</div>',
        )

    def consumers(self) -> str:
        """Place heterogeneous study samples and acquisition leads beside their limits."""
        india_sample = self.claim("phase_two_leads", {"route_id": "IN-D03"}, "sample_n")
        pakistan_sample = self.claim(
            "phase_two_leads", {"route_id": "PK-D01"}, "sample_n"
        )
        contexts = [
            (
                "Bryant and colleagues · India",
                "india_cultural_bryant_2019",
                f"The survey addresses perceptions of plant-based and clean meat across India, the United States and China. Its published India subgroup has {india_sample} respondents. The online panel skews urban, affluent and educated; hypothetical purchase intentions do not measure sales or national adoption. Exact fieldwork dates remain unverified here.",
            ),
            (
                "Arora, Brent and Jaenicke · India",
                "arora-brent-jaenicke-2020-india-alt-meat-wtp",
                "The paper examines preferences and willingness to pay for meat alternatives. Its discrete-choice study concerns Mumbai respondents, uses English and Hindi, and includes chana as an alternative. These local stated choices do not establish national buying behavior. The original methods are accessible through the publisher's article PDF; no outcome estimate is admitted here.",
            ),
            (
                "Ahsan, Uzair and Ali · Pakistan",
                "ahsan-uzair-ali-cultured-meat-pakistan",
                "The paper concerns attitudes and perceptions towards cultured meat in Pakistan. The historical register describes an online convenience sample and unresolved differences between headline and item-level response figures. The publication date is also unresolved in this source record. Neither the broad title nor the available extraction establishes national representativeness; no outcome estimate is admitted here.",
            ),
            (
                "Dean and colleagues · Pakistan subgroup",
                "PK-D01",
                f"The mycoprotein paper asks about willingness to try, buy and pay a premium. Its published Pakistan subgroup has {pakistan_sample} respondents in a young, nonprobability multicountry sample. The subgroup count is not a verified complete-case denominator. Internal pooled-count and outcome inconsistencies require resolution, and respondent files have not been acquired. This is distinct from the later Dean premium study in the comparison-study register below.",
            ),
        ]
        bilateral = '<h3>Named studies frame the bilateral research questions</h3><p class="fig-sub">These study contexts identify what to investigate in India and Pakistan. They do not add adoption estimates to the verified comparison findings below.</p><div class="study-list">'
        for name, source_id, context in contexts:
            access = self.source_access_note(source_id)
            bilateral += (
                f'<article class="study-card"><h4>{esc(name)}</h4>'
                f'<p class="source-name">{self.source_field(source_id, "title")}</p>'
                f'<p>{context}</p><p class="src">'
                + self.named_citations([(source_id, "Original source")])
                + "</p>"
                + (f'<p class="note">{esc(access)}</p>' if access else "")
                + "</article>"
            )
        bilateral += "</div>"
        admitted = self.selected("survey_findings", {"admitted_for_synthesis": "true"})
        if not admitted or any(
            row["original_verification_status"] != "original_outcome_verified"
            for row in admitted
        ):
            raise ValueError("Consumer outcomes require explicit original verification")
        outcome_claims = {
            row["record_id"]: {
                "value": self.claim(
                    "survey_findings", {"record_id": row["record_id"]}, "value_percent"
                ),
                "sample": self.claim(
                    "survey_findings", {"record_id": row["record_id"]}, "sample_n"
                ),
            }
            for row in admitted
        }
        outcomes = self.chart(
            "consumer-outcomes",
            "survey_findings",
            {"admitted_for_synthesis": "true"},
            [
                "record_id",
                "source_id",
                "geography",
                "protein",
                "measure",
                "value",
                "unit",
                "value_percent",
                "sample_n",
                "measurement_type",
                "question_wording",
                "fieldwork",
                "recruitment",
                "denominator",
                "limitation",
                "original_locator",
                "original_verification_status",
                "admitted_for_synthesis",
                "tier",
            ],
            "Verified study findings keep their original questions",
            "source-reported percentages within each study or country subgroup",
            "These outcomes concern the named comparison populations; a compatible India and Pakistan adoption baseline remains missing. Products, questions and recruitment differ. Country sample counts are source-reported; item nonresponse has not been independently recounted. Missing or disputed outcomes remain excluded.",
            "outcomes",
            {
                "claims": outcome_claims,
                "sourceLabels": {
                    row["source_id"]: self.sources[row["source_id"]]["title"]
                    for row in admitted
                },
            },
            citation_note=self.named_citations(
                [
                    ("S07", "Rakuten Insight"),
                    ("S02", "Maqsood and colleagues"),
                    ("S04", "Alptekin and colleagues"),
                    ("S05", "Alabdulmohsen and Al-Otaibi"),
                ]
            ),
        )
        studies = self.chart(
            "consumer-studies",
            "survey_studies",
            {},
            [
                "study_id",
                "title",
                "country",
                "measure",
                "sample_size",
                "sample_size_basis",
                "year",
                "fieldwork",
                "method",
                "selection_limits",
                "original_verification_status",
                "original_locator",
                "original_verification_limit",
                "limitations",
                "source_id",
                "tier",
            ],
            "Each study keeps its population and recruitment context",
            "published sample descriptors; outcome denominators may differ",
            "A sample descriptor is not an adoption finding. Studies outside India and Pakistan remain labelled by their actual geography; unknown sample sizes are not zeros.",
            "studies",
            {
                "claims": {
                    row["study_id"]: self.claim(
                        "survey_studies", {"study_id": row["study_id"]}, "sample_size"
                    )
                    for row in self.rows("survey_studies")
                    if row["sample_size"]
                }
            },
            citation_note=self.named_citations(
                [
                    ("S01", "Chriki and colleagues"),
                    ("S02", "Maqsood and colleagues"),
                    ("S03", "Dean and colleagues"),
                    ("S04", "Alptekin and colleagues"),
                    ("S05", "Alabdulmohsen and Al-Otaibi"),
                    ("S06", "Terano and colleagues"),
                    ("S07", "Rakuten Insight"),
                    ("S08", "GFI APAC"),
                    ("S09", "Lwin and colleagues"),
                ]
            ),
        )
        leads = self.chart(
            "consumer-data-leads",
            "phase_two_leads",
            {},
            [
                "route_id",
                "country",
                "title",
                "data_kind",
                "access_status",
                "respondent_data_acquired",
                "baseline_eligible",
                "sample_n",
                "sample_n_scope",
                "priority_request",
                "additional_inspection_lead",
                "request_url",
                "acquired_sample_n",
                "sample_n_interpretation",
                "limitations",
                "source_id",
                "tier",
            ],
            "Access routes are leads, not acquired respondent data",
            "source and access-route records",
            "A discoverable publication or repository listing does not establish a licensed, compatible respondent dataset. Candidate sample sizes are published descriptors; acquired usable sample sizes remain unknown.",
            "leads",
            {
                "claims": {
                    row["route_id"]: self.claim(
                        "phase_two_leads", {"route_id": row["route_id"]}, "sample_n"
                    )
                    for row in self.rows("phase_two_leads")
                    if row["priority_request"] == "true"
                    or row["additional_inspection_lead"] == "true"
                }
            },
            citation_note=self.named_citations(
                [
                    ("PK-D01", "Dean mycoprotein study"),
                    ("IN-D01", "Mendeley consumer-acceptance deposit"),
                    ("IN-D03", "Bryant consumer-perception study"),
                    ("IN-D02", "Cultured-meat adoption deposit"),
                    ("IN-S02", "GFI/Kantar consumer work"),
                    ("CTX-01", "Pakistan household survey"),
                    ("IN-B01", "India household-consumption survey"),
                ]
            )
            + ". The source ledger and exact table preserve the wider register.",
        )
        return self.section(
            11,
            "Consumer studies cannot be pooled into a regional adoption rate",
            "Willingness to try, stated purchase intent and observed buying are different outcomes. Recruitment methods and product descriptions also vary across studies.",
            f'<div class="wide">{bilateral}{outcomes}<p class="note">The Chriki willingness-to-try approximation and the disputed Terano outcome remain outside the findings panel. An approximate extraction cannot replace the source\'s threshold wording, and conflicting product or response labels need resolution in the original evidence.</p>{studies}<div class="rule-box"><div><b>Do not pool</b><span>Keep each study\'s country, recruitment, product, question and denominator attached to its result. Sample counts cannot be added into evidence of national adoption.</span></div></div>{leads}</div>',
            "P01 P06 P07",
        )

    def halal(self) -> str:
        """Give the published paper a bounded, source-linked summary."""
        body = f"""<div class="wide halal-summary"><div class="halal-question"><span class="kicker">Product and process</span><h3>Ingredients and production conditions matter</h3><p>Cell provenance, culture inputs, processing and contamination controls form distinct questions. A label alone cannot resolve them.</p></div><div class="halal-question"><span class="kicker">Institutions</span><h3>Religious interpretation and food approval have separate authorities</h3><p>MUIS is the Islamic Religious Council of Singapore. Its religious guidance, halal certification and a food-authority decision answer different institutional questions. Conditions vary by jurisdiction and certifier.</p><p>The International Islamic Fiqh Academy (IIFA) excludes prohibited culture media and substances and requires supervision by a credible specialist authority. {self.named_citations([("IIFA265", "IIFA conditional resolution")])}.</p><p>MUIS requires halal cell sources and ingredients, with a clean, non-toxic product. {self.named_citations([("MUIS2024", "MUIS cultivated-meat guidance")])}.</p></div><div class="halal-question"><span class="kicker">What remains open</span><h3>Approval cannot stand in for acceptance</h3><p>The paper does not establish a local market size, an adoption baseline or permission for every cultivated-chicken product.</p></div><p class="src">Read the source-led paper: {self.source('package_P09')}</p><p class="note">This is an AI-assisted synthesis awaiting human scholarly review. Later Pakistan policy evidence is presented in the alternative-protein chapter, with its specific functional-food scope.</p></div>"""
        return self.section(
            12,
            "Halal status depends on more than the name of the food",
            "The cultivated-chicken paper separates product conditions, scholarly interpretation and institutional decisions. Consumer acceptance remains another question.",
            body,
            "P09",
        )

    def culture(self) -> str:
        """Render a source-bound qualitative matrix without promoting weak point estimates."""
        matrix = self.chart(
            "cultural-matrix",
            "cultural_context",
            {},
            [
                "country",
                "region",
                "dimension",
                "finding",
                "date",
                "denominator",
                "evidence_scope",
                "display_rule",
                "source_id",
                "tier",
            ],
            "Dietary practices differ within each country",
            "source-specific cultural evidence",
            "Qualitative and diaspora evidence retains its geography. The weak Eid-volume point estimate is excluded from this projection and download.",
            "culture",
        )
        return self.section(
            13,
            "Culture complicates a single national story",
            "Religion, law, status, hospitality and migration shape different questions about food. The matrix preserves the source scope of each finding.",
            '<div class="wide">' + matrix + "</div>",
        )

    def open_questions(self) -> str:
        """Expose review dispositions without carrying any framing numbers into the edition."""
        reviews = self.chart(
            "review-status",
            "review_status",
            {
                "review_id": {
                    "in": [
                        "H1",
                        "H2",
                        "H3",
                        "H6",
                        "H7",
                        "M8",
                        "M9",
                        "M10",
                        "M11",
                        "M12",
                        "M13",
                        "M14",
                        "M17",
                        "L1",
                        "L2",
                        "L3",
                        "L4",
                        "E1",
                    ]
                }
            },
            [
                "review_id",
                "severity",
                "status",
                "finding",
                "resolution",
                "limitation",
                "source_id",
                "tier",
            ],
            "Corrections and limitations have separate dispositions",
            "review findings and documented resolutions",
            "A fixed calculation is not human scholarly approval. Disclosed gaps remain open research needs.",
            "reviews",
        )
        body = f"""<div class="wide"><div class="open"><article><span class="st holds">Source-bound</span><h3>Published supply and survey measures</h3><p>The edition preserves source definitions and links each displayed data selection to a downloadable table.</p></article><article><span class="st partial">Partial</span><h3>Pakistan dietary protein</h3><p>Named physical conversions cover only part of the diet. The complete total and a compatible adequacy assessment remain unavailable.</p></article><article><span class="st partial">Limited</span><h3>News framing</h3><p>The bounded annotation exercise concerns reporting, not public opinion. Its limitations belong in the full report appendix; no framing estimates or article corpus are included here.</p></article></div>{reviews}<p class="note">Further progress needs compatible consumer microdata, evidence of actual purchase, and qualified review of the food and religious claims. No data-request message has been sent autonomously.</p></div>"""
        return self.section(
            14,
            "The repaired evidence still has boundaries",
            "This edition makes the review outcomes visible. Missing baselines, incomplete dietary coverage and unreviewed scholarly judgments are substantive limits.",
            body,
            "P03 P04 P06",
        )

    def methods(self) -> str:
        """Build a searchable ledger only from cited source records."""
        source_rows = []
        for source_id in sorted(self.used_sources):
            row = self.sources[source_id]
            columns = ["source_id", "title", "publisher", "year", "tier", "url"]
            cells = []
            for column in columns:
                value = esc(row.get(column, ""))
                if column == "url" and row.get(column):
                    value = self.source_link(source_id, value, "ledger-link")
                cells.append(f'<td data-source-column="{column}">{value}</td>')
            source_rows.append(
                f'<tr data-source-id="{esc(source_id)}">' + "".join(cells) + "</tr>"
            )
            access_note = self.source_access_note(source_id)
            if access_note:
                source_rows.append(
                    f'<tr class="source-access-note" data-source-note-for="{esc(source_id)}"><td colspan="6" id="source-access-{esc(source_id)}">{esc(access_note)}</td></tr>'
                )
        headers = "".join(
            f'<th scope="col">{label}</th>'
            for label in [
                "Source ID",
                "Title",
                "Publisher",
                "Year",
                "Tier",
                "Public source",
            ]
        )
        source_download = self.csv_download(
            [self.sources[key] for key in sorted(self.used_sources)],
            ["source_id", "title", "publisher", "year", "tier", "url", "license"],
            "edition-sources.csv",
            "Download cited sources",
        )
        claim_download = self.csv_download(
            [row for row in self.claims if row["claim_id"] in self.claim_uses],
            list(self.claims[0]),
            "edition-claims.csv",
            "Download narrative claims",
        )
        body = f"""<div class="wide"><div class="method-grid"><div><h3>Keep source grades separate from calculations</h3><p>Source tier A covers official datasets and eligible peer-reviewed studies. B covers institutional reports. C covers industry and news. D covers social or model-labelled material. Analyst arithmetic carries the separate row tier derived.</p></div><div><h3>Trace the displayed value</h3><p>Every numerical statement is bound to the claims ledger. Each chart embeds its selected CSV strings and exposes the same rows in an exact table. The tests recompute values and reject source, table and receipt drift.</p></div><div><h3>Read the unit before comparing countries</h3><p>Food balances describe supply. Household surveys describe source-specific consumption measures. A consumer unit adjusts for energy requirements. Forecast intervals and conditional method ranges express different forms of uncertainty.</p></div><div><h3>Credit the work and its limits</h3><p>AI agents collected, processed and checked the evidence under the author's direction. The edition remains a research draft pending human scholarly review. Reproducibility and agent review do not substitute for that approval.</p></div></div><div class="institution-glossary"><h3>Institution and survey glossary</h3><dl><div><dt>SOFI</dt><dd>The State of Food Security and Nutrition in the World, the international report used here for affordability and undernourishment.</dd></div><div><dt>JME</dt><dd>Joint Child Malnutrition Estimates from UNICEF, the World Health Organization and the World Bank.</dd></div><div><dt>NFHS-5</dt><dd>India's fifth National Family Health Survey, used here for reported eating frequency.</dd></div><div><dt>HIES</dt><dd>Pakistan's Household Integrated Economic Survey, used here for published food quantities.</dd></div><div><dt>MUIS</dt><dd>The Islamic Religious Council of Singapore.</dd></div><div><dt>FSSAI</dt><dd>The Food Safety and Standards Authority of India.</dd></div><div><dt>BioE3</dt><dd>India's Biotechnology for Economy, Environment and Employment policy.</dd></div><div><dt>KP-NMD</dt><dd>The Newly Merged Districts of Khyber Pakhtunkhwa, retained as a separate National Nutrition Survey observation.</dd></div></dl></div><div class="reader-link-note"><h3>Reader links preserve the original record</h3><p>Some reader links open a checked accessible copy while the ledger and CSV retain the original URL. The Chriki link provides a structured NLM abstract, with abstract-only limits. The Terano link uses a third-party Semantic Scholar mirror; its disputed outcome remains unresolved. The link title explains each substitution.</p><p>Unavailable discovery routes are marked as inactive. This is a reader-access projection, not a claim that every recorded source URL works. Link status describes the last check and does not establish a source's findings, reuse rights or data availability.</p></div><label class="search-label" for="source-search">Search the cited source ledger<input id="source-search" type="search" placeholder="Source, publisher, country or tier"></label><p id="source-search-status" role="status" aria-live="polite">The ledger contains the sources cited in this edition.</p><div class="table-wrap source-ledger"><table id="source-ledger"><caption class="sr-only">Cited source registry</caption><thead><tr>{headers}</tr></thead><tbody>{''.join(source_rows)}</tbody></table></div><p class="download">{source_download} · {claim_download}</p><p class="note">CSV downloads beside each chart contain its declared public columns. Article text, private workspace material and report-only framing data are excluded. Source websites may have separate reuse conditions.</p></div>"""
        return self.section(
            15,
            "Methods and sources remain inspectable",
            "Read the charts as an account of available evidence, with units, dates and missing values preserved.",
            body,
            "P01 P03 P04 P06 P08 P09",
        )

    def build(self) -> None:
        """Write one self-contained HTML after every evidence dependency resolves."""
        sections = [
            self.opening(),
            self.findings(),
            self.theory(),
            self.supply(),
            self.regions(),
            self.diet(),
            self.protein(),
            self.risks(),
            self.benchmark(),
            self.alternatives(),
            self.consumers(),
            self.halal(),
            self.culture(),
            self.open_questions(),
        ]
        sections.append(self.methods())
        titles = [
            "Two neighbours, one protein question",
            "What the evidence supports",
            "Acceptability and adoption",
            "National food supply",
            "Regional evidence",
            "Household diets",
            "Protein reference scenarios",
            "Nutrition risks",
            "Supply futures",
            "Alternative proteins",
            "Consumer evidence",
            "Halal and cultivated chicken",
            "Cultural context",
            "What remains open",
            "Methods and sources",
        ]
        toc = (
            '<nav class="toc" aria-label="Contents"><div class="kicker">Contents</div><ol>'
            + "".join(
                "<li>"
                + self.link(f"#chapter-{index:02}", esc(title), "contents")
                + "</li>"
                for index, title in enumerate(titles, 1)
            )
            + "</ol></nav>"
        )
        sections.insert(1, toc)
        geometry = {}
        for iso, country in [("IND", "India"), ("PAK", "Pakistan")]:
            geometry[country] = json.loads(
                (HERE / f"geo/geoBoundaries-{iso}-ADM1.geojson").read_text()
            )
        css = (HERE / "styles.css").read_text()
        runtime = (HERE / "runtime.js").read_text()
        d3 = (HERE / "lib/d3-7.9.0.min.js").read_text()
        output = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Ccircle cx=%2216%22 cy=%2216%22 r=%2212%22 fill=%22%232a6cb5%22/%3E%3C/svg%3E"><title>Protein in India and Pakistan | Sentient Futures</title><meta name="description" content="A source-led research edition on protein supply, diets and alternative proteins in India and Pakistan. AI-assisted; human scholarly review pending."><script>try{{const theme=localStorage.getItem('sf-theme');if(['light','dark'].includes(theme))document.documentElement.dataset.theme=theme;}}catch(error){{}}</script><style>{css}</style></head><body><a id="skip-main" class="skip-link" href="#main">Skip to the edition</a><header class="bar"><div class="bar-in"><span class="mark"><b>India</b> · <i>Pakistan</i></span><span class="now" id="chapter-current">Protein evidence edition</span><button id="theme-toggle" type="button" aria-label="Toggle colour theme" aria-pressed="false">Theme</button></div><div class="progress" id="reading-progress" aria-hidden="true"></div></header><main id="main">{''.join(sections)}</main><footer><div>Sentient Futures research edition. AI-assisted, human scholarly review pending. Every chart includes its selected source rows. This local edition has not been published.</div></footer><div class="tip" id="chart-tooltip" role="tooltip" aria-label="Chart source details" aria-hidden="true"></div><script type="application/json" id="edition-geography">{json_html(geometry)}</script><script>{d3}</script><script>{runtime}</script></body></html>"""
        (HERE / "index.html").write_text(output)
        receipt = {
            "html_sha256": hashlib.sha256(output.encode()).hexdigest(),
            "bytes": len(output.encode()),
            "charts": sorted(self.chart_ids),
            "claim_ids": sorted(set(self.claim_uses)),
            "source_ids": sorted(self.used_sources),
            "dataset_hashes": {
                name: hashlib.sha256((DATA / f"{name}.csv").read_bytes()).hexdigest()
                for name in sorted(self.datasets)
            },
            "d3_version": "7.9.0",
            "d3_sha256": hashlib.sha256(d3.encode()).hexdigest(),
            "scope": "Build receipt only; browser, links and scholarly review require separate evidence",
        }
        (HERE / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(
            json.dumps(
                {key: receipt[key] for key in ["html_sha256", "bytes", "d3_version"]}
            )
        )
        print(
            f"Built {len(sections)-1} chapters and {len(self.chart_ids)} exact chart tables"
        )


if __name__ == "__main__":
    Edition().build()
