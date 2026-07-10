"""Supported MGnify Genomes catalogue sources."""

from urllib.error import HTTPError, URLError
import urllib.request


# Database source: MGnify Genomes FTP; supported catalog versions are defined in DB_URLS.
DB_URLS = {
    "human-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "human-oral": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-oral/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "human-skin": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-skin/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "human-vaginal": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-vaginal/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "barley-rhizosphere": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/barley-rhizosphere/v2.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "chicken-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/chicken-gut/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "cow-rumen": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/cow-rumen/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "honeybee-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/honeybee-gut/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "marine": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/marine/v2.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "marine-sediment": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/marine-sediment/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "maize-rhizosphere": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/maize-rhizosphere/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "mouse-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/mouse-gut/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "non-model-fish-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/non-model-fish-gut/v2.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "pig-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/pig-gut/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "sheep-rumen": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/sheep-rumen/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "soil": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/soil/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "tomato-rhizosphere": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/tomato-rhizosphere/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
    "zebrafish-fecal": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/zebrafish-fecal/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue",
    },
}

GUI_CATALOGUE_PRIORITY = (
    "human-gut",
    "human-oral",
    "human-skin",
    "human-vaginal",
)


def mgnify_catalogue_display_names():
    """Return stable GUI labels for the supported MGnify catalogues."""
    ordered_db_types = list(GUI_CATALOGUE_PRIORITY) + sorted(
        set(DB_URLS).difference(GUI_CATALOGUE_PRIORITY)
    )
    return [
        f"{db_type} ({DB_URLS[db_type]['base_url'].rsplit('/', 1)[-1]})"
        for db_type in ordered_db_types
    ]


def validate_mgnify_source(db_type, check_catalogue=False, timeout=10):
    """Validate the configured MGnify source and return its source metadata.

    The metadata URL is always checked. Set ``check_catalogue`` to also verify
    that the configured species catalogue directory is reachable.
    """
    if db_type not in DB_URLS:
        supported = ", ".join(DB_URLS)
        raise ValueError(
            f"Unsupported MGnify database type: {db_type}. Supported values: {supported}"
        )

    db_info = DB_URLS[db_type]
    urls = {"metadata": f"{db_info['base_url']}/{db_info['metadata']}"}
    if check_catalogue:
        urls["species catalogue"] = f"{db_info['base_url']}/{db_info['catalogue']}/"

    for label, url in urls.items():
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                if getattr(response, "status", 200) >= 400:
                    raise RuntimeError(f"MGnify {label} URL returned HTTP status {response.status}: {url}")
                if label == "metadata":
                    header = response.read(65536).decode("utf-8-sig").splitlines()[0].split("\t")
        except (HTTPError, URLError, OSError) as error:
            raise RuntimeError(
                f"MGnify {label} URL is unavailable for database type '{db_type}': {url}. "
                "Check the configured catalogue version and the MGnify FTP index."
            ) from error

        if label == "metadata":
            missing_columns = {"Species_rep", "Lineage"}.difference(header)
            if missing_columns:
                raise ValueError(
                    f"MGnify metadata for database type '{db_type}' is missing required columns "
                    f"{', '.join(sorted(missing_columns))}: {url}"
                )

    return db_info
