import logging

from marshmallow import Schema, post_load
from marshmallow.fields import Int, String, Bool

from src.models.api.job.references_job import ReferencesJob

logger = logging.getLogger(__name__)


class ReferencesSchema(Schema):
    offset = Int()
    wari_id = String()
    chunk_size = Int()
    all = Bool()

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ReferencesJob:  # type: ignore # dead: disable
        """Return job object"""
        logger.debug("return_object: running")
        job = ReferencesJob(**data)
        return job
