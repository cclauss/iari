# from __future__ import annotations
#
# import logging
# import textwrap
# from datetime import datetime, timezone
# from time import sleep
# from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple
#
# from pydantic import validate_arguments
# from wikibaseintegrator import (  # type: ignore
#     WikibaseIntegrator,
#     datatypes,
#     wbi_config,
#     wbi_login,
# )
# from wikibaseintegrator.entities import ItemEntity  # type: ignore
# from wikibaseintegrator.models import (  # type: ignore
#     Claim,
#     Qualifiers,
#     Reference,
#     References,
# )
# from wikibaseintegrator.wbi_exceptions import (  # type: ignore
#     ModificationFailed,
#     NonExistentEntityError,
# )
# from wikibaseintegrator.wbi_helpers import delete_page  # type: ignore
# from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore
#
# import config
# from src.models.exceptions import MissingInformationError
# from src.models.person import Person
# from src.models.return_.wikibase_return import WikibaseReturn
# from src.models.wikibase import Wikibase
# from src.wcd_base_model import WcdBaseModel
#
# if TYPE_CHECKING:
#     from src.models.wikimedia.wikipedia.article import WikipediaArticle
#     from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
#
# logger = logging.getLogger(__name__)
#
#
# class WikibaseCrud(WcdBaseModel):
#     """This class models the WikiCitations Wikibase
#     and handles all preparation of statements before uploading to it
#
#     We want to create items for all Wikipedia articles
#     and references with a unique hash
#
#     Terminology:
#     wikipedia_reference is a reference that appear in a Wikipedia page
#     reference_claim is a datastructure from WBI that contains the
#     revision id and retrieved date of the statement
#
#     The language code is the one used by Wikimedia Foundation"""
#
#     language_code: str = "en"
#     reference_claim: Optional[References]
#     wikibase: Wikibase
#
#     class Config:
#         arbitrary_types_allowed = True
#
#     # @validate_arguments
#     # def __convert_wcd_entity_id_to_item_entity__(self, entity_id: str) -> ItemEntity:
#     #     """Convert and get the item using WBI"""
#     #     self.__setup_wikibase_integrator_configuration__()
#     #     wbi = WikibaseIntegrator()
#     #     return wbi.item.get(entity_id)
#
#     @validate_arguments
#     def __extract_item_ids__(self, sparql_result: Optional[Dict]) -> Iterable[str]:
#         """Yield item ids from a sparql result"""
#         if sparql_result:
#             yielded = 0
#             for binding in sparql_result["results"]["bindings"]:
#                 if item_id := self.__extract_wcdqs_json_entity_id_from_sparql_variable__(
#                     data=binding
#                 ):
#                     yielded += 1
#                     yield item_id
#             if number_of_bindings := len(sparql_result["results"]["bindings"]):
#                 logger.info(f"Yielded {yielded} bindings out of {number_of_bindings}")
#
#     @validate_arguments
#     def __extract_item_ids_and_hashes__(
#         self, sparql_result: Optional[Dict]
#     ) -> Iterable[Tuple[str, str]]:
#         """Yield item ids and hashes from a sparql result"""
#         logger.debug("__extract_item_ids_and_hashes__: Running")
#         if sparql_result:
#             yielded = 0
#             for binding in sparql_result["results"]["bindings"]:
#                 if item_id := self.__extract_wcdqs_json_entity_id_from_sparql_variable__(
#                     data=binding
#                 ):
#                     if hash_value := self.__extract_wcdqs_json_entity_id_from_sparql_variable__(
#                         data=binding, sparql_variable="hash"
#                     ):
#                         yielded += 1
#                         yield item_id, hash_value
#             if number_of_bindings := len(sparql_result["results"]["bindings"]):
#                 logger.info(f"Yielded {yielded} bindings out of {number_of_bindings}")
#
#     @validate_arguments
#     def __extract_wcdqs_json_entity_id_from_sparql_variable__(
#         self, data: Dict, sparql_variable: str = "item"
#     ) -> str:
#         """We default to "item" as sparql value because it is customary in the Wikibase ecosystem"""
#         return str(
#             data[sparql_variable]["value"].replace(
#                 self.wikibase.rdf_entity_prefix_url, ""
#             )
#         )
#
#     def __setup_wikibase_integrator_configuration__(
#         self,
#     ) -> None:
#         wbi_config.config["USER_AGENT"] = "wcdimportbot"
#         wbi_config.config["WIKIBASE_URL"] = self.wikibase.wikibase_url
#         wbi_config.config["MEDIAWIKI_API_URL"] = self.wikibase.mediawiki_api_url
#         wbi_config.config["MEDIAWIKI_INDEX_URL"] = self.wikibase.mediawiki_index_url
#         wbi_config.config["SPARQL_ENDPOINT_URL"] = self.wikibase.sparql_endpoint_url
#
#     def __prepare_all_person_claims__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         if not self.wikibase.FULL_NAME_STRING:
#             raise MissingInformationError(
#                 "self.wikibase.FULL_NAME_STRING was empty string"
#             )
#         if not self.wikibase.EDITOR_NAME_STRING:
#             raise MissingInformationError(
#                 "self.wikibase.EDITOR_NAME_STRING was empty string"
#             )
#         if not self.wikibase.HOST_STRING:
#             raise MissingInformationError("self.wikibase.HOST_STRING was empty string")
#         if not self.wikibase.INTERVIEWER_STRING:
#             raise MissingInformationError(
#                 "self.wikibase.INTERVIEWER_STRING was empty string"
#             )
#         authors = self.__prepare_person_claims__(
#             use_list=page_reference.authors_list,
#             wikibase_property_id=self.wikibase.FULL_NAME_STRING,
#         )
#         if (
#             config.assume_persons_without_role_are_authors
#             and page_reference.persons_without_role
#         ):
#             logger.info("Assuming persons without role are authors")
#         no_role_authors = self.__prepare_person_claims__(
#             use_list=page_reference.persons_without_role,
#             wikibase_property_id=self.wikibase.FULL_NAME_STRING,
#         )
#         editors = self.__prepare_person_claims__(
#             use_list=page_reference.interviewers_list,
#             wikibase_property_id=self.wikibase.EDITOR_NAME_STRING,
#         )
#         hosts = self.__prepare_person_claims__(
#             use_list=page_reference.hosts_list,
#             wikibase_property_id=self.wikibase.HOST_STRING,
#         )
#         interviewers = self.__prepare_person_claims__(
#             use_list=page_reference.interviewers_list,
#             wikibase_property_id=self.wikibase.INTERVIEWER_STRING,
#         )
#         translators = self.__prepare_person_claims__(
#             use_list=page_reference.interviewers_list,
#             wikibase_property_id=self.wikibase.INTERVIEWER_STRING,
#         )
#         return authors + no_role_authors + editors + hosts + interviewers + translators
#
#     @validate_arguments
#     def __prepare_item_citations__(
#         self, wikipedia_article  # type: WikipediaArticle
#     ) -> List[Claim]:
#         """Prepare the item citations and add a reference
#         to in which revision it was found and the retrieval date"""
#         logger.info("Preparing item citations")
#         claims = []
#         for reference in wikipedia_article.references or []:
#             if reference.return_:
#                 logger.debug("Appending to item-citations")
#                 claims.append(
#                     datatypes.Item(
#                         prop_nr=self.wikibase.CITATIONS,
#                         value=reference.return_.item_qid,
#                         references=self.reference_claim,
#                     )
#                 )
#         return claims
#
#     def __login_and_prepare_new_item__(self) -> ItemEntity:
#         self.__setup_wikibase_integrator_configuration__()
#         logger.debug(f"Trying to log in to the Wikibase as {self.wikibase.user_name}")
#         wbi = WikibaseIntegrator(
#             login=wbi_login.Login(
#                 user=self.wikibase.user_name, password=self.wikibase.botpassword
#             ),
#         )
#         return wbi.item.new()
#
#     def __prepare_new_reference_item__(
#         self,
#         page_reference,  # type: WikipediaReference
#     ) -> ItemEntity:
#         """This method converts a page_reference into a new reference wikibase item"""
#         item = self.__login_and_prepare_new_item__()
#         if page_reference.md5hash:
#             # We append the first 7 chars of the hash to the title
#             # to avoid label collision errors
#             # Wikibase does not allow a label longer than 250 characters maximum
#             if page_reference.title:
#                 shortened_title = textwrap.shorten(
#                     page_reference.title, width=240, placeholder="..."
#                 )
#             else:
#                 # Handle title being None
#                 shortened_title = "Title missing"
#             label = f"{shortened_title} | {page_reference.md5hash[:7]}"
#             item.labels.set("en", label)
#             item.descriptions.set(
#                 "en",
#                 # We hardcode Wikipedia here for now.
#                 f"reference from Wikipedia",
#             )
#             persons = self.__prepare_all_person_claims__(page_reference=page_reference)
#             if persons:
#                 item.add_claims(persons)
#             item.add_claims(
#                 claims=self.__prepare_single_value_reference_claims__(
#                     page_reference=page_reference
#                 )
#             )
#             # if config.loglevel == logging.DEBUG:
#             #     logger.debug("Printing the item data")
#             #     print(item.get_json())
#             #     # exit()
#             return item
#         else:
#             raise MissingInformationError("page_reference.md5hash was empty")
#
#     def __prepare_new_website_item__(
#         self,
#         page_reference,  # type: WikipediaReference
#         wikipedia_article,  # type: WikipediaArticle
#     ) -> ItemEntity:
#         """This method converts a page_reference into a new website item"""
#         if page_reference.first_level_domain_of_url is None:
#             raise MissingInformationError(
#                 "page_reference.first_level_domain_of_url was None"
#             )
#         logger.info(
#             f"Creating website item: {page_reference.first_level_domain_of_url}"
#         )
#         self.__setup_wikibase_integrator_configuration__()
#         wbi = WikibaseIntegrator(
#             login=wbi_login.Login(
#                 user=self.wikibase.user_name, password=self.wikibase.botpassword
#             ),
#         )
#         item = wbi.item.new()
#         item.labels.set("en", page_reference.first_level_domain_of_url)
#         item.descriptions.set(
#             "en",
#             f"website referenced from {wikipedia_article.wikimedia_site.name.title()}",
#         )
#         item.add_claims(
#             self.__prepare_single_value_website_claims__(page_reference=page_reference),
#         )
#         # if config.loglevel == logging.DEBUG:
#         #     logger.debug("Printing the item data")
#         #     print(item.get_json())
#         #     # exit()
#         return item
#
#     @validate_arguments
#     def __prepare_new_wikipedia_article_item__(
#         self, wikipedia_article  # type: WikipediaArticle
#     ) -> ItemEntity:
#         """This method converts a page_reference into a new WikiCitations item"""
#         logging.debug("__prepare_new_wikipedia_article_item__: Running")
#         self.__setup_wikibase_integrator_configuration__()
#         wbi = WikibaseIntegrator(
#             login=wbi_login.Login(
#                 user=self.wikibase.user_name, password=self.wikibase.botpassword
#             ),
#         )
#         item = wbi.item.new()
#         if wikipedia_article.title:
#             shortened_title = textwrap.shorten(
#                 wikipedia_article.title, width=250, placeholder="..."
#             )
#         else:
#             shortened_title = None
#         item.labels.set("en", shortened_title)
#         item.descriptions.set(
#             "en",
#             f"article from {wikipedia_article.language_code}:{wikipedia_article.wikimedia_site.name.title()}",
#         )
#         # Prepare claims
#         # First prepare the page_reference needed in other claims
#         citations = self.__prepare_item_citations__(wikipedia_article=wikipedia_article)
#         string_citations = self.__prepare_string_citations__(
#             wikipedia_article=wikipedia_article
#         )
#         if citations:
#             item.add_claims(citations)
#         if string_citations:
#             item.add_claims(string_citations)
#         item.add_claims(
#             self.__prepare_single_value_wikipedia_article_claims__(
#                 wikipedia_article=wikipedia_article
#             ),
#         )
#         if config.loglevel == logging.DEBUG:
#             logger.debug("Printing the item data")
#             print(item.get_json())
#             # exit()
#         return item
#
#     @validate_arguments
#     def __prepare_person_claims__(
#         self,
#         use_list: Optional[List[Person]],
#         wikibase_property_id: str,
#     ) -> List:
#         """Prepare claims using the specified property and list of person objects"""
#         persons = []
#         use_list = use_list or []
#         if use_list:
#             logger.debug(f"Preparing {wikibase_property_id}")
#             for person_object in use_list:
#                 # We use this pythonic way of checking if the string is empty inspired by:
#                 # https://www.delftstack.com/howto/python/how-to-check-a-string-is-empty-in-a-pythonic-way/
#                 if person_object.full_name:
#                     qualifiers = (
#                         self.__prepare_person_qualifiers__(person_object=person_object)
#                         or []
#                     )
#                     if qualifiers:
#                         person = datatypes.String(
#                             prop_nr=wikibase_property_id,
#                             value=person_object.full_name,
#                             qualifiers=qualifiers,
#                         )
#                     else:
#                         person = datatypes.String(
#                             prop_nr=wikibase_property_id,
#                             value=person_object.full_name,
#                         )
#                     persons.append(person)
#         return persons
#
#     @validate_arguments
#     def __prepare_person_qualifiers__(self, person_object: Person):
#         qualifiers = []
#         if (
#             person_object.given
#             or person_object.given
#             or person_object.orcid
#             or person_object.number_in_sequence
#         ):
#             if person_object.given:
#                 given_name = datatypes.String(
#                     prop_nr=self.wikibase.GIVEN_NAME,
#                     value=person_object.given,
#                 )
#                 qualifiers.append(given_name)
#             if person_object.surname:
#                 surname = datatypes.String(
#                     prop_nr=self.wikibase.FAMILY_NAME,
#                     value=person_object.surname,
#                 )
#                 qualifiers.append(surname)
#             if person_object.number_in_sequence:
#                 number_in_sequence = datatypes.Quantity(
#                     prop_nr=self.wikibase.SERIES_ORDINAL,
#                     amount=person_object.number_in_sequence,
#                 )
#                 qualifiers.append(number_in_sequence)
#             if person_object.orcid:
#                 orcid = datatypes.ExternalID(
#                     prop_nr=self.wikibase.ORCID,
#                     value=person_object.orcid,
#                 )
#                 qualifiers.append(orcid)
#             if person_object.url:
#                 url = datatypes.URL(
#                     prop_nr=self.wikibase.URL,
#                     value=person_object.url,
#                 )
#                 qualifiers.append(url)
#             if person_object.mask:
#                 mask = datatypes.String(
#                     prop_nr=self.wikibase.NAME_MASK,
#                     value=person_object.mask,
#                 )
#                 qualifiers.append(mask)
#         return qualifiers
#
#     @validate_arguments
#     def __prepare_reference_claim__(
#         self, wikipedia_article=None  # type: Optional[WikipediaArticle]
#     ):
#         """This reference claim contains the current revision id and the current date
#         This enables us to track references over time in the graph using SPARQL."""
#         logger.info("Preparing reference claim")
#         # Prepare page_reference
#         retrieved_date = datatypes.Time(
#             prop_nr=self.wikibase.RETRIEVED_DATE,
#             time=datetime.utcnow()  # Fetched today
#             .replace(tzinfo=timezone.utc)
#             .replace(
#                 hour=0,
#                 minute=0,
#                 second=0,
#             )
#             .strftime("+%Y-%m-%dT%H:%M:%SZ"),
#         )
#         if wikipedia_article:
#             revision_id = datatypes.String(
#                 prop_nr=self.wikibase.PAGE_REVISION_ID,
#                 value=str(wikipedia_article.latest_revision_id),
#             )
#             claims = [retrieved_date, revision_id]
#         else:
#             claims = [retrieved_date]
#         citation_reference = Reference()
#         for claim in claims:
#             logger.debug(f"Adding reference {claim}")
#             citation_reference.add(claim)
#         self.reference_claim = References()
#         self.reference_claim.add(citation_reference)
#
#     def __prepare_single_value_reference_claims__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         logger.info("Preparing single value claims")
#         if page_reference.md5hash is None:
#             raise ValueError("page_reference.md5hash was None")
#         # Website item
#         if page_reference.website_item:
#             if page_reference.website_item.return_:
#                 if page_reference.website_item.return_.item_qid:
#                     website_item = datatypes.Item(
#                         prop_nr=self.wikibase.WEBSITE,
#                         value=page_reference.website_item.return_.item_qid,
#                     )
#                 else:
#                     raise MissingInformationError("no item_qid in the return_")
#             else:
#                 raise MissingInformationError("no return_ in the website_item")
#         else:
#             website_item = None
#         claims: List[Claim] = []
#         for claim in (website_item,):
#             if claim:
#                 claims.append(claim)
#         return (
#             claims
#             + self.__prepare_single_value_reference_claims_always_present__(
#                 page_reference=page_reference
#             )
#             + self.__prepare_single_value_reference_external_identifier_claims__(
#                 page_reference=page_reference
#             )
#             + self.__prepare_single_value_reference_string_claims__(
#                 page_reference=page_reference
#             )
#             + self.__prepare_single_value_reference_claims_with_dates__(
#                 page_reference=page_reference
#             )
#             + self.__prepare_single_value_reference_claims_with_urls__(
#                 page_reference=page_reference
#             )
#         )
#
#     def __prepare_single_value_reference_claims_always_present__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         # if page_reference.raw_template:
#         #     raw_template = datatypes.String(
#         #         prop_nr=self.wikibase.RAW_TEMPLATE,
#         #         value=page_reference.shortened_raw_template,
#         #     )
#         # else:
#         #     raise MissingInformationError("page_reference.raw_template was None")
#         instance_of = datatypes.Item(
#             prop_nr=self.wikibase.INSTANCE_OF,
#             value=self.wikibase.WIKIPEDIA_REFERENCE,
#         )
#         hash_claim = datatypes.String(
#             prop_nr=self.wikibase.HASH, value=page_reference.md5hash
#         )
#         if page_reference.first_template_name:
#             template_string = datatypes.String(
#                 prop_nr=self.wikibase.TEMPLATE_NAME,
#                 value=page_reference.first_template_name,
#             )
#         else:
#             raise MissingInformationError("no templates name found")
#         retrieved_date = datatypes.Time(
#             prop_nr=self.wikibase.RETRIEVED_DATE,
#             time=datetime.utcnow()  # Fetched today
#             .replace(tzinfo=timezone.utc)
#             .replace(
#                 hour=0,
#                 minute=0,
#                 second=0,
#             )
#             .strftime("+%Y-%m-%dT%H:%M:%SZ"),
#         )
#         if not self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on:
#             raise MissingInformationError(
#                 "self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on was None"
#             )
#         source_wikipedia = datatypes.Item(
#             prop_nr=self.wikibase.SOURCE_WIKIPEDIA,
#             value=self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on,
#         )
#         return [
#             hash_claim,
#             instance_of,
#             # raw_template,
#             retrieved_date,
#             source_wikipedia,
#             template_string,
#         ]
#
#     def __prepare_single_value_reference_external_identifier_claims__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         # DEPRECATED since 2.1.0-alpha3
#         # if page_reference.google_books_id:
#         #     google_books_id = datatypes.ExternalID(
#         #         prop_nr=self.wikibase.GOOGLE_BOOKS_ID,
#         #         value=page_reference.google_books_id,
#         #     )
#         # else:
#         google_books_id = None
#         if page_reference.internet_archive_id:
#             internet_archive_id = datatypes.ExternalID(
#                 prop_nr=self.wikibase.INTERNET_ARCHIVE_ID,
#                 value=page_reference.internet_archive_id,
#             )
#         else:
#             internet_archive_id = None
#         if page_reference.doi:
#             doi = datatypes.ExternalID(
#                 prop_nr=self.wikibase.DOI,
#                 value=page_reference.doi,
#             )
#         else:
#             doi = None
#         if page_reference.isbn_10:
#             isbn_10 = datatypes.ExternalID(
#                 prop_nr=self.wikibase.ISBN_10,
#                 value=page_reference.isbn_10,
#             )
#         else:
#             isbn_10 = None
#         if page_reference.isbn_13:
#             isbn_13 = datatypes.ExternalID(
#                 prop_nr=self.wikibase.ISBN_13,
#                 value=page_reference.isbn_13,
#             )
#         else:
#             isbn_13 = None
#         if page_reference.oclc:
#             oclc = datatypes.ExternalID(
#                 prop_nr=self.wikibase.OCLC_CONTROL_NUMBER,
#                 value=page_reference.oclc,
#             )
#         else:
#             oclc = None
#         if page_reference.orcid:
#             orcid = datatypes.ExternalID(
#                 prop_nr=self.wikibase.ORCID,
#                 value=page_reference.orcid,
#             )
#         else:
#             orcid = None
#         if page_reference.pmid:
#             pmid = datatypes.ExternalID(
#                 prop_nr=self.wikibase.PMID,
#                 value=page_reference.pmid,
#             )
#         else:
#             pmid = None
#         if page_reference.wikidata_qid:
#             wikidata_qid = datatypes.ExternalID(
#                 prop_nr=self.wikibase.WIKIDATA_QID,
#                 value=page_reference.wikidata_qid,
#             )
#         else:
#             wikidata_qid = None
#         claims: List[Claim] = []
#         for claim in (
#             doi,
#             google_books_id,
#             internet_archive_id,
#             isbn_10,
#             isbn_13,
#             oclc,
#             orcid,
#             pmid,
#             wikidata_qid,
#         ):
#             if claim:
#                 claims.append(claim)
#         return claims
#
#     def __prepare_single_value_reference_string_claims__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         if page_reference.location:
#             location = datatypes.String(
#                 prop_nr=self.wikibase.LOCATION_STRING, value=page_reference.location
#             )
#         else:
#             location = None
#         if page_reference.vauthors:
#             lumped_authors = datatypes.String(
#                 prop_nr=self.wikibase.LUMPED_AUTHORS,
#                 value=page_reference.vauthors,
#             )
#         else:
#             lumped_authors = None
#         if page_reference.periodical:
#             periodical_string = datatypes.String(
#                 prop_nr=self.wikibase.PERIODICAL_STRING,
#                 value=page_reference.periodical,
#             )
#         else:
#             periodical_string = None
#         if page_reference.publisher:
#             publisher = datatypes.String(
#                 prop_nr=self.wikibase.PUBLISHER_STRING,
#                 value=page_reference.publisher,
#             )
#         else:
#             publisher = None
#         if page_reference.title:
#             # Wikibase has a default limit of 400 chars for String
#             shortened_title = textwrap.shorten(
#                 page_reference.title, width=400, placeholder="..."
#             )
#             title = datatypes.String(
#                 prop_nr=self.wikibase.TITLE,
#                 value=shortened_title,
#             )
#         else:
#             title = None
#         if page_reference.website:
#             website_string = datatypes.String(
#                 prop_nr=self.wikibase.WEBSITE_STRING,
#                 value=page_reference.website,
#             )
#         else:
#             website_string = None
#         claims: List[Claim] = []
#         for claim in (
#             location,
#             lumped_authors,
#             periodical_string,
#             publisher,
#             title,
#             website_string,
#         ):
#             if claim:
#                 claims.append(claim)
#         return claims
#
#     def __prepare_single_value_reference_claims_with_dates__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         claims = []
#         if page_reference.access_date:
#             claims.append(
#                 datatypes.Time(
#                     prop_nr=self.wikibase.ACCESS_DATE,
#                     time=(
#                         page_reference.access_date.replace(tzinfo=timezone.utc)
#                         .replace(
#                             hour=0,
#                             minute=0,
#                             second=0,
#                         )
#                         .strftime("+%Y-%m-%dT%H:%M:%SZ")
#                     ),
#                 )
#             )
#         if page_reference.publication_date:
#             claims.append(
#                 datatypes.Time(
#                     prop_nr=self.wikibase.PUBLICATION_DATE,
#                     time=(
#                         page_reference.publication_date.replace(tzinfo=timezone.utc)
#                         .replace(
#                             hour=0,
#                             minute=0,
#                             second=0,
#                         )
#                         .strftime("+%Y-%m-%dT%H:%M:%SZ")
#                     ),
#                 )
#             )
#         return claims
#
#     def __prepare_single_value_reference_claims_with_urls__(
#         self, page_reference
#     ) -> List[Claim]:
#         logger.debug("__prepare_single_value_reference_claims_with_urls__: Running")
#         claims = []
#         if page_reference.archive_url:
#             if len(page_reference.archive_url) > 500:
#                 # TODO log to file also
#                 logger.error(
#                     f"Skipping statement for the URL '{page_reference.archive_url}' because it "
#                     f"is longer than 500 characters which this Wikibase currently do not support :/"
#                 )
#             else:
#                 if page_reference.detected_archive_of_archive_url:
#                     logger.debug("Adding qualifier linking to the detected archive")
#                     claims.append(
#                         datatypes.URL(
#                             prop_nr=self.wikibase.ARCHIVE_URL,
#                             value=page_reference.archive_url,
#                             qualifiers=[
#                                 datatypes.Item(
#                                     prop_nr=self.wikibase.ARCHIVE,
#                                     value=self.wikibase.__getattribute__(
#                                         page_reference.detected_archive_of_archive_url.name.upper().replace(
#                                             ".", "_"
#                                         )
#                                     ),
#                                 )
#                             ],
#                         )
#                     )
#                 else:
#                     message = f"No supported archive detected for {page_reference.archive_url}"
#                     logger.debug(message)
#                     self.__log_to_file__(
#                         message=message, file_name="undetected_archive.log"
#                     )
#                     claims.append(
#                         datatypes.URL(
#                             prop_nr=self.wikibase.ARCHIVE_URL,
#                             value=page_reference.archive_url,
#                         )
#                     )
#         if page_reference.url:
#             if len(page_reference.url) > 500:
#                 # TODO log to file also
#                 logger.error(
#                     f"Skipping statement for this URL because it "
#                     f"is too long for Wikibase currently to store :/"
#                 )
#             else:
#                 claims.append(
#                     datatypes.URL(
#                         prop_nr=self.wikibase.URL,
#                         value=page_reference.url,
#                     )
#                 )
#         if page_reference.chapter_url:
#             if len(page_reference.chapter_url) > 500:
#                 # TODO log to file also
#                 logger.error(
#                     f"Skipping statement for this URL because it "
#                     f"is too long for Wikibase currently to store :/"
#                 )
#             else:
#                 claims.append(
#                     datatypes.URL(
#                         prop_nr=self.wikibase.CHAPTER_URL,
#                         value=page_reference.chapter_url,
#                     )
#                 )
#         if page_reference.conference_url:
#             if len(page_reference.conference_url) > 500:
#                 # TODO log to file also
#                 logger.error(
#                     f"Skipping statement for this URL because it "
#                     f"is too long for Wikibase currently to store :/"
#                 )
#             else:
#                 claims.append(
#                     datatypes.URL(
#                         prop_nr=self.wikibase.CONFERENCE_URL,
#                         value=page_reference.conference_url,
#                     )
#                 )
#         if page_reference.lay_url:
#             if len(page_reference.lay_url) > 500:
#                 # TODO log to file also
#                 logger.error(
#                     f"Skipping statement for this URL because it "
#                     f"is too long for Wikibase currently to store :/"
#                 )
#             else:
#                 claims.append(
#                     datatypes.URL(
#                         prop_nr=self.wikibase.LAY_URL,
#                         value=page_reference.lay_url,
#                     )
#                 )
#         if page_reference.transcripturl:
#             if len(page_reference.transcripturl) > 500:
#                 # TODO log to file also
#                 logger.error(
#                     f"Skipping statement for this URL because it "
#                     f"is too long for Wikibase currently to store :/"
#                 )
#             else:
#                 claims.append(
#                     datatypes.URL(
#                         prop_nr=self.wikibase.TRANSCRIPT_URL,
#                         value=page_reference.transcripturl,
#                     )
#                 )
#         return claims
#
#     def __prepare_single_value_website_claims__(
#         self, page_reference  # type: WikipediaReference
#     ) -> Optional[List[Claim]]:
#         logger.info("Preparing single value claims for the website item")
#         # Claims always present
#         instance_of = datatypes.Item(
#             prop_nr=self.wikibase.INSTANCE_OF,
#             value=self.wikibase.WEBSITE_ITEM,
#         )
#         if not self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on:
#             raise MissingInformationError(
#                 "self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on was None"
#             )
#         source_wikipedia = datatypes.Item(
#             prop_nr=self.wikibase.SOURCE_WIKIPEDIA,
#             value=self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on,
#         )
#         first_level_domain_string = datatypes.String(
#             prop_nr=self.wikibase.FIRST_LEVEL_DOMAIN_STRING,
#             value=page_reference.first_level_domain_of_url,
#         )
#         if page_reference.first_level_domain_of_url_hash is None:
#             raise ValueError("page_reference.first_level_domain_of_url_hash was None")
#         hash_claim = datatypes.String(
#             prop_nr=self.wikibase.HASH,
#             value=page_reference.first_level_domain_of_url_hash,
#         )
#         return [
#             claim
#             for claim in (
#                 instance_of,
#                 source_wikipedia,
#                 first_level_domain_string,
#                 hash_claim,
#             )
#             if claim
#         ]
#
#     def __prepare_single_value_wikipedia_article_claims__(
#         self, wikipedia_article
#     ) -> List[Claim]:
#         # There are no optional claims for Wikipedia Pages
#         absolute_url = datatypes.URL(
#             prop_nr=self.wikibase.URL,
#             value=wikipedia_article.absolute_url,
#         )
#         if wikipedia_article.md5hash is None:
#             raise ValueError("wikipedia_article.md5hash was None")
#         hash_claim = datatypes.String(
#             prop_nr=self.wikibase.HASH, value=wikipedia_article.md5hash
#         )
#         instance_of = datatypes.Item(
#             prop_nr=self.wikibase.INSTANCE_OF,
#             value=self.wikibase.WIKIPEDIA_PAGE,
#         )
#         last_update = datatypes.Time(
#             prop_nr=self.wikibase.LAST_UPDATE,
#             time=datetime.utcnow()  # Fetched today
#             .replace(tzinfo=timezone.utc)
#             .replace(
#                 hour=0,
#                 minute=0,
#                 second=0,
#             )
#             .strftime("+%Y-%m-%dT%H:%M:%SZ"),
#         )
#         if wikipedia_article.page_id is None:
#             raise ValueError("wikipedia_article.page_id was None")
#         page_id = datatypes.String(
#             prop_nr=self.wikibase.MEDIAWIKI_PAGE_ID,
#             value=str(wikipedia_article.page_id),
#         )
#         if not self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on:
#             raise MissingInformationError(
#                 "self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on was None"
#             )
#         published_in = datatypes.Item(
#             prop_nr=self.wikibase.PUBLISHED_IN,
#             value=self.wikibase.wcdqid_language_edition_of_wikipedia_to_work_on,
#         )
#         if wikipedia_article.title is None:
#             raise ValueError("wikipedia_article.item_id was None")
#         title = datatypes.String(
#             prop_nr=self.wikibase.TITLE,
#             value=wikipedia_article.title,
#         )
#         wikidata_qid = datatypes.String(
#             prop_nr=self.wikibase.WIKIDATA_QID,
#             value=wikipedia_article.wikidata_qid,
#         )
#         return [
#             absolute_url,
#             hash_claim,
#             instance_of,
#             last_update,
#             page_id,
#             published_in,
#             title,
#             wikidata_qid,
#         ]
#
#     def __prepare_string_authors__(self, page_reference: WikipediaReference):
#         authors = []
#         for author in page_reference.authors_list or []:
#             if author.full_name:
#                 author = datatypes.String(
#                     prop_nr=self.wikibase.FULL_NAME_STRING,
#                     value=author.full_name,
#                 )
#                 authors.append(author)
#         if page_reference.vauthors:
#             author = datatypes.String(
#                 prop_nr=self.wikibase.LUMPED_AUTHORS,
#                 value=page_reference.vauthors,
#             )
#             authors.append(author)
#         if page_reference.authors:
#             author = datatypes.String(
#                 prop_nr=self.wikibase.LUMPED_AUTHORS,
#                 value=page_reference.authors,
#             )
#             authors.append(author)
#         return authors or None
#
#     def __prepare_string_editors__(self, page_reference: WikipediaReference):
#         persons = []
#         for person in page_reference.editors_list or []:
#             if person.full_name:
#                 person = datatypes.String(
#                     prop_nr=self.wikibase.EDITOR_NAME_STRING,
#                     value=person.full_name,
#                 )
#                 persons.append(person)
#         return persons or None
#
#     def __prepare_string_translators__(self, page_reference: WikipediaReference):
#         persons = []
#         for person in page_reference.translators_list or []:
#             if person.full_name:
#                 person = datatypes.String(
#                     prop_nr=self.wikibase.TRANSLATOR_NAME_STRING,
#                     value=person.full_name,
#                 )
#                 persons.append(person)
#         return persons or None
#
#     def __prepare_string_citation__(
#         self, page_reference  # type: WikipediaReference
#     ) -> Claim:
#         """We import citations which could not be uniquely identified
#         as strings directly on the wikipedia page item"""
#         qualifiers = self.__prepare_string_citation_qualifiers__(
#             page_reference=page_reference
#         )
#         claim_qualifiers = Qualifiers()
#         for qualifier in qualifiers:
#             logger.debug(f"Adding qualifier {qualifier}")
#             claim_qualifiers.add(qualifier)
#         string_citation = datatypes.String(
#             prop_nr=self.wikibase.STRING_CITATIONS,
#             value=page_reference.first_template_name,
#             qualifiers=claim_qualifiers,
#             references=self.reference_claim,
#         )
#         return string_citation
#
#     def __prepare_string_citation_qualifiers__(
#         self, page_reference  # type: WikipediaReference
#     ) -> List[Claim]:
#         """Here we prepare all statements we normally
#         would put on a unique separate page_reference item"""
#         claims = []
#         string_authors = self.__prepare_string_authors__(page_reference=page_reference)
#         if string_authors:
#             claims.extend(string_authors)
#         string_editors = self.__prepare_string_editors__(page_reference=page_reference)
#         if string_editors:
#             claims.extend(string_editors)
#         string_translators = self.__prepare_string_translators__(
#             page_reference=page_reference
#         )
#         if string_translators:
#             claims.extend(string_translators)
#         # TODO add FULL_NAME_STRING here for the first author
#         archive_date = None
#         archive_url = None
#         publication_date = None
#         # raw_template = None
#         title = None
#         website_string = None
#         if page_reference.access_date:
#             access_date = datatypes.Time(
#                 prop_nr=self.wikibase.ACCESS_DATE,
#                 time=(
#                     page_reference.access_date.replace(tzinfo=timezone.utc)
#                     .replace(
#                         hour=0,
#                         minute=0,
#                         second=0,
#                     )
#                     .strftime("+%Y-%m-%dT%H:%M:%SZ")
#                 ),
#             )
#         else:
#             access_date = None
#         if page_reference.archive_date:
#             archive_date = datatypes.Time(
#                 prop_nr=self.wikibase.ARCHIVE_DATE,
#                 time=(
#                     page_reference.archive_date.replace(tzinfo=timezone.utc)
#                     .replace(
#                         hour=0,
#                         minute=0,
#                         second=0,
#                     )
#                     .strftime("+%Y-%m-%dT%H:%M:%SZ")
#                 ),
#             )
#         else:
#             access_date = None
#         if page_reference.archive_url:
#             archive_url = datatypes.URL(
#                 prop_nr=self.wikibase.ARCHIVE_URL,
#                 value=page_reference.archive_url,
#             )
#         if page_reference.publication_date:
#             publication_date = datatypes.Time(
#                 prop_nr=self.wikibase.PUBLICATION_DATE,
#                 time=(
#                     page_reference.publication_date.replace(tzinfo=timezone.utc)
#                     .replace(
#                         hour=0,
#                         minute=0,
#                         second=0,
#                     )
#                     .strftime("+%Y-%m-%dT%H:%M:%SZ")
#                 ),
#             )
#         # if page_reference.raw_template:
#         #     raw_template = datatypes.String(
#         #         prop_nr=self.wikibase.RAW_TEMPLATE,
#         #         value=page_reference.shortened_raw_template,
#         #     )
#         # else:
#         #     raise MissingInformationError("page_reference.raw_template was None")
#         if page_reference.title:
#             title = datatypes.String(
#                 prop_nr=self.wikibase.TITLE,
#                 value=page_reference.title,
#             )
#         if page_reference.url:
#             url = datatypes.URL(
#                 prop_nr=self.wikibase.URL,
#                 value=page_reference.url,
#             )
#         else:
#             url = None
#         if page_reference.website:
#             website_string = datatypes.String(
#                 prop_nr=self.wikibase.WEBSITE_STRING,
#                 value=page_reference.website,
#             )
#         for claim in (
#             access_date,
#             archive_date,
#             archive_url,
#             publication_date,
#             # raw_template,
#             title,
#             url,
#             website_string,
#         ):
#             if claim:
#                 claims.append(claim)
#         return claims
#
#     @validate_arguments
#     def __prepare_string_citations__(
#         self, wikipedia_article  # type: WikipediaArticle
#     ) -> List[Claim]:
#         # pseudo code
#         # Return a citation for every page_reference that does not have a hash
#         return [
#             self.__prepare_string_citation__(page_reference=page_reference)
#             for page_reference in (wikipedia_article.references or [])
#             if not page_reference.has_hash
#         ]
#
#     @staticmethod
#     def __wait_for_wcdqs_to_sync__():
#         """This is used by the rebuild cache functionality"""
#         logger.info(
#             f"Sleeping {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
#         )
#         sleep(config.sparql_sync_waiting_time_in_seconds)
#
#     @validate_arguments
#     def entity_url(self, qid: str):
#         return f"{self.wikibase.wikibase_url}wiki/Item:{qid}"
#
#     # TODO: refactor these into one generic method
#     def prepare_and_upload_reference_item(
#         self,
#         page_reference,  # type: WikipediaReference
#     ) -> WikibaseReturn:
#         """This method prepares and then tries to upload the reference to WikiCitations
#         and returns a WikibaseReturn."""
#         item = self.__prepare_new_reference_item__(page_reference=page_reference)
#         from src.models.wikibase.crud.create import WikibaseCrudCreate
#
#         wcc = WikibaseCrudCreate(wikibase=self.wikibase)
#         return_ = wcc.upload_new_item(item=item)
#         if isinstance(return_, WikibaseReturn):
#             return return_
#         else:
#             raise ValueError(f"we did not get a WikibaseReturn back")
#
#     @validate_arguments
#     def prepare_and_upload_website_item(
#         self,
#         page_reference,  # type: WikipediaReference
#         wikipedia_article,  # type: WikipediaArticle
#     ) -> WikibaseReturn:
#         """This method prepares and then tries to upload the website item to WikiCitations
#         and returns the WCDQID either if successful upload or from the
#         Wikibase error if an item with the exact same label/hash already exists."""
#         self.__prepare_reference_claim__(wikipedia_article=wikipedia_article)
#         item = self.__prepare_new_website_item__(
#             page_reference=page_reference, wikipedia_article=wikipedia_article
#         )
#         from src.models.wikibase.crud.create import WikibaseCrudCreate
#
#         wcc = WikibaseCrudCreate(wikibase=self.wikibase)
#         return_ = wcc.upload_new_item(item=item)
#         if isinstance(return_, WikibaseReturn):
#             return return_
#         else:
#             raise ValueError(f"we did not get a WikibaseReturn back")
#
#     @validate_arguments
#     def prepare_and_upload_wikipedia_article_item(
#         self, wikipedia_article: Any
#     ) -> WikibaseReturn:
#         """This method prepares and then tries to upload the page to WikiCitations
#         and returns the WCDQID either if successful upload or from the
#         Wikibase error if an item with the exact same label/hash already exists."""
#         logging.debug("prepare_and_upload_wikipedia_article_item: Running")
#         from src.models.wikimedia.wikipedia.article import WikipediaArticle
#
#         if not isinstance(wikipedia_article, WikipediaArticle):
#             raise ValueError("did not get a WikipediaArticle object")
#         self.__prepare_reference_claim__(wikipedia_article=wikipedia_article)
#         item = self.__prepare_new_wikipedia_article_item__(
#             wikipedia_article=wikipedia_article
#         )
#         from src.models.wikibase.crud.create import WikibaseCrudCreate
#
#         wcc = WikibaseCrudCreate(wikibase=self.wikibase)
#         return_: WikibaseReturn = wcc.upload_new_item(item=item)
#         return return_
