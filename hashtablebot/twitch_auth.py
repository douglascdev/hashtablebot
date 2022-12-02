SCOPES = (
    "chat:read",
    "chat:edit",
)


def get_token_url(client_id: str) -> str:
    uri_formatted_scopes = "+".join((scope.replace(":", "%3A") for scope in SCOPES))
    twitch_auth_url = "https://id.twitch.tv/oauth2/authorize"
    params = {
        "response_type": "token",
    }
    return f"{twitch_auth_url}?response_type=token&client_id={client_id}&redirect_uri=http://localhost&scope={uri_formatted_scopes}"
