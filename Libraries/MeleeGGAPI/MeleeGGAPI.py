
import base64
import json
from urllib.request import Request, urlopen

# https://melee.gg/swagger/ui/index#!/TournamentMatchApi/


class MeleeGGAPI:

    def __init__(self, client_id: str | None = None, client_secret: str | None = None):
        self._client_id = client_id
        self._client_secret = client_secret

    def set_credentials(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def _auth_token(self) -> str:
        token = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode("utf-8")).decode("ascii")
        return token

    def _make_request(self, endpoint: str):
        request = Request(
            f"https://melee.gg/api/{endpoint}",
            headers={"Authorization": f"Basic {self._auth_token}"},
        )

        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data

    def get_player_list(self, tournament_id: int):
        """
        Lists all players in a specific tournament
        """
        return self._make_request(f"player/list/{tournament_id}")

    def get_tournament_list(self):
        """
        Lists tournaments accessible to the authenticated staff member, with support for pagination.
        """
        return self._make_request("tournament/list")

    def get_standing_list_current(self, tournament_id: int):
        """
        Lists the current standings for a specific tournament. Supports pagination through query parameters
        """
        return self._make_request(f"standing/list/current/{tournament_id}")

    def get_standing_list_round(self, round_id: int):
        """
        Lists standings for a specific round of a tournament.
        """
        return self._make_request(f"standing/list/round/{round_id}")
