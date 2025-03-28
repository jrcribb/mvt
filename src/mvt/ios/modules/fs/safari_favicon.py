# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2023 The MVT Authors.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging
from typing import Optional, Union

from mvt.common.utils import convert_mactime_to_iso

from ..base import IOSExtraction

SAFARI_FAVICON_ROOT_PATHS = [
    "private/var/mobile/Library/Image Cache/Favicons/Favicons.db",
    "private/var/mobile/Containers/Data/Application/*/Library/Image Cache/Favicons/Favicons.db",
]


class SafariFavicon(IOSExtraction):
    """This module extracts all Safari favicon records."""

    def __init__(
        self,
        file_path: Optional[str] = None,
        target_path: Optional[str] = None,
        results_path: Optional[str] = None,
        module_options: Optional[dict] = None,
        log: logging.Logger = logging.getLogger(__name__),
        results: Optional[list] = None,
    ) -> None:
        super().__init__(
            file_path=file_path,
            target_path=target_path,
            results_path=results_path,
            module_options=module_options,
            log=log,
            results=results,
        )

    def serialize(self, record: dict) -> Union[dict, list]:
        return {
            "timestamp": record["isodate"],
            "module": self.__class__.__name__,
            "event": "safari_favicon",
            "data": f"Safari favicon from {record['url']} with icon URL "
            f"{record['icon_url']} ({record['type']})",
        }

    def check_indicators(self) -> None:
        if not self.indicators:
            return

        for result in self.results:
            ioc = self.indicators.check_url(result["url"])
            if not ioc:
                ioc = self.indicators.check_url(result["icon_url"])

            if ioc:
                result["matched_indicator"] = ioc
                self.detected.append(result)

    def _process_favicon_db(self, file_path):
        conn = self._open_sqlite_db(file_path)

        # Fetch valid icon cache.
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                page_url.url,
                icon_info.url,
                icon_info.timestamp
            FROM page_url
            JOIN icon_info ON page_url.uuid = icon_info.uuid
            ORDER BY icon_info.timestamp;
        """
        )

        for row in cur:
            self.results.append(
                {
                    "url": row[0],
                    "icon_url": row[1],
                    "timestamp": row[2],
                    "isodate": convert_mactime_to_iso(row[2]),
                    "type": "valid",
                    "safari_favicon_db_path": file_path,
                }
            )

        # Fetch icons from the rejected icons table.
        cur.execute(
            """
            SELECT
                page_url,
                icon_url,
                timestamp
            FROM rejected_resources ORDER BY timestamp;
        """
        )

        for row in cur:
            self.results.append(
                {
                    "url": row[0],
                    "icon_url": row[1],
                    "timestamp": row[2],
                    "isodate": convert_mactime_to_iso(row[2]),
                    "type": "rejected",
                    "safari_favicon_db_path": file_path,
                }
            )

        cur.close()
        conn.close()

    def run(self) -> None:
        for file_path in self._get_fs_files_from_patterns(SAFARI_FAVICON_ROOT_PATHS):
            self.log.info("Found Safari favicon cache database at path: %s", file_path)
            self._process_favicon_db(file_path)

        self.log.info("Extracted a total of %d favicon records", len(self.results))

        self.results = sorted(self.results, key=lambda x: x["isodate"])
