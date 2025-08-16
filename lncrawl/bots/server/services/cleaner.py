import logging
import shutil
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
    target_size = ctx.config.app.disk_size_limit - 50 * 1024 * 1024

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

        # Keep deleting novels to reach target disk size limit
        logger.info('Deleting older novels to free up disk...')
        cutoff = current_timestamp() - 24 * 3600
        for novel in sess.exec(
            select(Novel)
            .where(Novel.updated_at < cutoff)
            .order_by(asc(Novel.updated_at))
        ).all():
            if signal.is_set():
                return
            output = novel.extra.get('output_path')
            if output:
                shutil.rmtree(output, ignore_errors=True)
                current_size = folder_size(output_folder)
                if current_size < target_size:
                    break

        current_size = folder_size(output_folder)
        logger.info(f'Disk size after cleanup: {format_size(current_size)}')

    except Exception:
        logger.error("Cleanup failed", exc_info=True)

    finally:
        sess.close()
        logger.info("=== Cleanup end ===")
