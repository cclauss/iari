from unittest import TestCase

from pydantic import ValidationError

from src.models.api.job.article_job import ArticleJob
from src.models.wikimedia.enums import WikimediaDomain


class TestArticleJob(TestCase):
    def test_site(self):
        job = ArticleJob(title="", site="wikipedia")
        assert job.domain == WikimediaDomain.wikipedia

    def test_get_page_id(self):
        job = ArticleJob(title="Test", site="wikipedia.org", lang="en")
        job.get_page_id()
        assert job.page_id == 11089416

    def test_refresh(self):
        job = ArticleJob(title="Test", site="wikipedia", lang="en")
        assert job.refresh is False
        job = ArticleJob(title="Test", site="wikipedia", lang="en", refresh=True)
        assert job.refresh is True
        with self.assertRaises(ValidationError):
            ArticleJob(title="Test", site="wikipedia", lang="en", refresh="123")

    def test_extract_url_http(self):
        job = ArticleJob()
        job.url = "http://en.wikipedia.org/wiki/Test"
        job.__extract_url__()

        self.assertEqual(job.lang, "en")
        self.assertEqual(job.domain, WikimediaDomain.wikipedia)
        self.assertEqual(job.title, "Test")

    def test_extract_url_https(self):
        job = ArticleJob()
        job.url = "https://en.wikipedia.org/wiki/Test"
        job.__extract_url__()

        self.assertEqual(job.lang, "en")
        self.assertEqual(job.domain, WikimediaDomain.wikipedia)
        self.assertEqual(job.title, "Test")

    # noinspection PyStatementEffect
    def test_quoted_title(self):
        job = ArticleJob(
            url="https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy"
        )
        job.__extract_url__()
        assert job.quoted_title == "GNU%2FLinux_naming_controversy"

    def test_valid_regex_valid_input(self):
        job = ArticleJob(regex="test string | another string | a third string")
        assert job.__valid_regex__ is False
        job2 = ArticleJob(regex="test|string|another|string")
        assert job2.__valid_regex__ is True
        job3 = ArticleJob(regex="teststring")
        assert job3.__valid_regex__ is True
        job4 = ArticleJob(
            regex="bibliography|further reading|works cited|sources|external links"
        )
        assert job4.__valid_regex__ is True

    def test_valid_regex_invalid_input(self):
        job = ArticleJob(regex="test string | another string | a third string")
        assert job.__valid_regex__ is False
        job2 = ArticleJob(regex="test||string")
        assert job2.__valid_regex__ is False
        job3 = ArticleJob(regex="teststring_")
        assert job3.__valid_regex__ is False
