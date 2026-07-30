"""Acquisition : client HTTP a debit controle.

Une seule requete a la fois, un delai minimal entre deux requetes, un
compteur de requetes envoyees (utile pour le rapport, rubrique 2.1 et 7),
et des tentatives limitees en cas d'echec reseau transitoire.
"""
from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger("kws_collector.http")


class ThrottledClient:
    def __init__(
        self,
        user_agent: str,
        delay_seconds: float,
        timeout_seconds: float,
        max_retries: int = 3,
    ) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._last_request_at: float | None = None
        self.request_count = 0

    def _wait_for_slot(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def get(self, url: str) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            self._wait_for_slot()
            self._last_request_at = time.monotonic()
            self.request_count += 1
            try:
                response = self.session.get(url, timeout=self.timeout_seconds)
                logger.info("GET %s -> %s (tentative %s)", url, response.status_code, attempt)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                logger.warning("Echec GET %s (tentative %s/%s) : %s", url, attempt, self.max_retries, exc)
        assert last_error is not None
        raise last_error
