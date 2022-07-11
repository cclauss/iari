import logging
from os import getenv
from time import sleep
from unittest import TestCase

import pytest

import config
from src.helpers import console
from src.models.wikibase.sandbox_wikibase import SandboxWikibase
from src.models.wikimedia.enums import WikimediaSite

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaPage(TestCase):
    def test_fix_dash(self):
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        page = WikipediaPage(
            wikibase=SandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
        )
        page.__get_wikipedia_page_from_title__(title="Easter Island")
        page.__extract_and_parse_references__()
        logger.info(f"{len(page.references)} references found")
        for ref in page.references:
            if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
                # console.print(ref.template_name)
                if (
                    ref.url
                    == "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
                ):
                    console.print(ref.url, ref.archive_url)

    def test_fetch_page_data_and_parse_the_wikitext(self):
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        page = WikipediaPage(
            wikibase=SandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
        )
        page.__fetch_page_data__(title="Test")
        assert page.page_id == 11089416
        assert page.title == "Test"

    @pytest.mark.xfail(bool(getenv("CI")), reason="GitHub Actions do not have logins")
    def test_get_wcdqid_from_hash_via_sparql(self):
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        page = WikipediaPage(
            wikibase=SandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Test",
        )
        # page.__fetch_page_data__(title="Test")
        page.extract_and_upload_to_wikicitations()
        wcdqid = page.wikicitations_qid
        console.print(
            f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
        )
        sleep(config.sparql_sync_waiting_time_in_seconds)
        check_wcdqid = page.__get_wcdqid_from_hash_via_sparql__(md5hash=page.md5hash)
        print(wcdqid, check_wcdqid)
        assert wcdqid == check_wcdqid
