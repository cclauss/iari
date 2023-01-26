import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from flask import request
from flask_restful import Resource, abort  # type: ignore

from src import MissingInformationError
from src.helpers.console import console
from src.models.api.get_article_statistics.article_statistics import ArticleStatistics
from src.models.api.get_article_statistics.get_statistics_schema import (
    GetStatisticsSchema,
)
from src.models.api.job import Job
from src.models.file_io import FileIo
from src.models.wikimedia.enums import AnalyzerReturn, WikimediaSite
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_short_tail_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    test_full_article,
)


class GetArticleStatistics(Resource):
    schema = GetStatisticsSchema()
    job: Optional[Job]
    wikipedia_analyzer: Optional[WikipediaAnalyzer] = None
    statistics_dictionary: Dict[str, Any] = {}
    time_of_analysis: Optional[datetime] = None

    def get(self):
        from src.models.api import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if (
            self.job.lang.lower() == "en"
            and self.job.title
            and self.job.site == WikimediaSite.wikipedia
        ):
            app.logger.debug("got valid job")
            if self.job.testing:
                app.logger.debug("testing...")
                self.__prepare_wikipedia_analyzer_if_testing__()
                if not self.wikipedia_analyzer:
                    MissingInformationError("no self.wikipedia_analyzer")
                self.__get_timing_and_statistics__()
                return self.statistics_dictionary, 200
            else:
                app.logger.debug("trying to read from cache")
                self.__read_statistics_from_cache__()
                if (
                    self.statistics_dictionary
                    and not self.__more_than_2_days_old_cache__()
                ):
                    app.logger.debug("got recent json from cache")
                    # We got the statistics from json, return them as is
                    app.logger.info(
                        f"Returning existing json from disk with date: {self.time_of_analysis}"
                    )
                    return self.statistics_dictionary, 200
                else:
                    app.logger.error(
                        "we may have the data but it is too old, refreshing..."
                    )
                    if not self.wikipedia_analyzer:
                        app.logger.info(f"Analyzing {self.job.title}...")
                        # TODO use a work queue here like ReFill so
                        #  we can easily scale the workload from thousands of users
                        self.wikipedia_analyzer = WikipediaAnalyzer(
                            job=self.job, check_urls=True
                        )
                    return self.__analyze_and_write_and_return__()
        else:
            # Something was not valid, return a meaningful error
            app.logger.error("did not get what we need")
            if self.job.lang != "en":
                return "Only language code 'en' is supported, currently", 400
            if self.job.title == "":
                return "Title was missing", 400
            if self.job.site != "wikipedia":
                return "Only 'wikipedia' site is supported", 400

    def __validate_and_get_job__(self):
        """Helper method"""
        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):
        from src.models.api import app

        app.logger.debug("__validate__: running")
        errors = self.schema.validate(request.args)
        if errors:
            app.logger.debug(f"Found errors: {errors}")
            abort(400, error=str(errors))

    def __parse_into_job__(self):
        from src.models.api import app

        app.logger.debug("__parse_into_job__: running")
        # app.logger.debug(request.args)
        self.job = self.schema.load(request.args)
        console.print(self.job.dict())

    def __more_than_2_days_old_cache__(self) -> bool:
        """This reads from the cache and returns a boolean"""
        from src.models.api import app

        app.logger.debug("__not_more_than_2_days_old_cache__: running")
        if not self.statistics_dictionary:
            self.__read_statistics_from_cache__()
        if self.statistics_dictionary:
            now = datetime.utcnow()
            two_days_ago = now - timedelta(hours=48)
            app.logger.debug(f"two days ago {two_days_ago}")
            self.time_of_analysis = datetime.fromtimestamp(
                self.statistics_dictionary["timestamp"]
            )
            app.logger.debug(f"analysis time {self.time_of_analysis}")
            if self.time_of_analysis < two_days_ago:
                app.logger.debug("more than 48h ago")
                return True
            else:
                app.logger.debug("not more than 48h ago")
        # Default to False ie. also return false when no json on disk
        return False

    def __read_statistics_from_cache__(self):
        io = FileIo(job=self.job)
        io.read_from_disk()
        if io.statistics_dictionary:
            self.statistics_dictionary = io.statistics_dictionary

    def __analyze_and_write_and_return__(self) -> Tuple[Any, int]:
        """Analyze, calculate the time, write statistics to disk and return it
        If we did not get statistics, return a meaningful error to the user"""
        from src.models.api import app

        app.logger.info("__analyze_and_write_and_return__: running")
        if not self.wikipedia_analyzer:
            raise MissingInformationError("self.wikipedia_analyzer was None")
        self.__get_timing_and_statistics__()
        if self.wikipedia_analyzer.found:
            app.logger.info("found article")
            if self.wikipedia_analyzer.is_redirect:
                return AnalyzerReturn.IS_REDIRECT.value, 400
            else:
                self.__update_statistics_with_time_information__()
                # app.logger.debug(f"dictionary from analyzer: {self.statistics_dictionary}")
                # we got a json response
                # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
                # flask calls jsonify automatically
                self.__write_to_disk__()
                # app.logger.debug("returning dictionary")
                return self.statistics_dictionary, 200
        else:
            return AnalyzerReturn.NOT_FOUND.value, 404

    def __prepare_wikipedia_analyzer_if_testing__(self):
        from src.models.api import app

        app.logger.debug("__prepare_wikipedia_analyzer_if_testing__: running")
        supported_test_titles = ["Test", "Easter Island", "Electrical breakdown"]
        if self.job.testing and self.job.title in supported_test_titles:
            if self.job.title == "Test":
                app.logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                self.wikipedia_analyzer = WikipediaAnalyzer(
                    job=self.job, wikitext=test_full_article
                )
            elif self.job.title == "Electrical_breakdown":
                app.logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                self.wikipedia_analyzer = WikipediaAnalyzer(
                    job=self.job,
                    wikitext=electrical_breakdown_full_article,
                    check_urls=True,
                )
            elif self.job.title == "Easter Island":
                app.logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                self.wikipedia_analyzer = WikipediaAnalyzer(
                    job=self.job,
                    wikitext=f"{easter_island_head_excerpt}\n{easter_island_short_tail_excerpt}",
                )
            else:
                app.logger.warning(f"Ignoring unsupported test title {self.job.title}")

    def __get_timing_and_statistics__(self):
        from src.models.api import app

        app.logger.debug("__get_timing_and_statistics__: running")
        if not self.wikipedia_analyzer:
            raise MissingInformationError("self.wikipedia_analyzer was None")
        # https://realpython.com/python-timer/
        start_time = time.perf_counter()
        self.statistics_dictionary = self.wikipedia_analyzer.get_statistics()
        # app.logger.debug(f"self.wikipedia_analyzer.found:{self.wikipedia_analyzer.found}")
        end_time = time.perf_counter()
        self.timing = round(float(end_time - start_time), 3)

    def __update_statistics_with_time_information__(self):
        """Update the dictionary before returning it"""
        if self.statistics_dictionary:
            self.statistics_dictionary["timing"] = self.timing
            timestamp = datetime.timestamp(datetime.utcnow())
            self.statistics_dictionary["timestamp"] = int(timestamp)
        else:
            raise ValueError("not a dict")

    def __write_to_disk__(self):
        io = FileIo(job=self.job, statistics_dictionary=self.statistics_dictionary)
        io.write_to_disk()
