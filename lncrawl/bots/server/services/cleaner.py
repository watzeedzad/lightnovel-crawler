import logging
import shutil
import os
from threading import Event

from sqlmodel import asc, select, true

from ..context import ServerContext
from ..models.novel import Artifact, Novel
from ..utils.file_tools import folder_size, format_size
from ..utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)


def microtask(signal=Event()) -> None:
    ctx = ServerContext()
    sess = ctx.db.session()
    output_folder = ctx.config.app.output_path
    size_limit = ctx.config.app.disk_size_limit

    logger.info("=== Cleanup begin ===")
    try:
        # Delete all orphan novels
        logger.info('Cleaning up orphan novels...')
        for novel in sess.exec(
            select(Novel)
            .where(Novel.orphan == true())
        ).all():
            output = novel.extra.get('output_path')
            if output:
                shutil.rmtree(output, ignore_errors=True)
            sess.delete(novel)
            sess.commit()
        if signal.is_set():
            return

        # Delete all unavailable artifacts
        logger.info('Cleaning up unavailable artifacts...')
        for artifact in sess.exec(
            select(Artifact)
        ).all():
            if not artifact.is_available:
                sess.delete(artifact)
                sess.commit()
        if signal.is_set():
            return

        # check if cleaner is enabled
        if size_limit <= 0:
            return

        current_size = folder_size(output_folder)
        logger.info(f"Current folder size: {format_size(current_size)}")
        if current_size < size_limit:
            return

        # Keep deleting novels to reach target disk size limit
        logger.info('Deleting folders to free up space...')
        cutoff = current_timestamp() - 24 * 3600
        for novel in sess.exec(
            select(Novel)
            .where(Novel.updated_at < cutoff)
            .order_by(asc(Novel.updated_at))
        ).all():
            if signal.is_set():
                return
            output = novel.extra.get('output_path')
            if output and os.path.isdir(output):
                current_size -= folder_size(output)
                shutil.rmtree(output, ignore_errors=True)
                if current_size < size_limit:
                    break

        current_size = folder_size(output_folder)
        logger.info(f"Final folder size: {format_size(current_size)}")

    except Exception:
        logger.error("Cleanup failed", exc_info=True)

    finally:
        sess.close()
        logger.info("=== Cleanup end ===")
