from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp


class ItemDetailsCleanup:
    """Delete items whose deletion lease has passed. Foreign keys cascade to their rows.

    Every write extends the lease of the rows it relies on, so a row past its lease is not
    needed by any unexpired item. Deletes run in small batches so that the item detail
    service can write between them, and a large backlog is spread across maintenance runs.
    """

    batch_size = 100  # Items per delete; one show can cascade to thousands of rows
    batch_limit = 50  # Batches per maintenance run

    delete_statement = (
        'DELETE FROM baseitem WHERE id IN '
        '(SELECT id FROM baseitem WHERE deletion<? LIMIT ?)'
    )

    def __init__(self, database):
        self.database = database

    @cached_property
    def current_time(self):
        """Fixed for the run so that every batch uses the same boundary"""
        return set_timestamp(0, set_int=True)

    def delete_batch(self):
        """Delete one batch and return how many items it removed; execute_sql logs failures"""
        cursor = self.database.execute_sql(self.delete_statement, (self.current_time, self.batch_size))
        return cursor.rowcount if cursor else 0

    def prune(self):
        for _ in range(self.batch_limit):
            if self.delete_batch() < self.batch_size:
                return
