import responses
from version import version_info, update_version_info, ATOM_LINK, APP_VERSION
from unittest.mock import patch


def test_200_response():
    mock_response = """
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/" xml:lang="en-US">
        <id>tag:github.com,2008:https://github.com/jellyfin/jellyfin/releases</id>
        <link type="text/html" rel="alternate" href="https://github.com/jellyfin/jellyfin/releases"/>
        <link type="application/atom+xml" rel="self" href="https://github.com/jellyfin/jellyfin/releases.atom"/>
        <title>Release notes from jellyfin</title>
        <updated>2024-06-25T00:19:28Z</updated>
        <entry>
            <id>tag:github.com,2008:Repository/161012019/v10.9.7</id>
            <updated>2024-06-25T00:37:42Z</updated>
            <link rel="alternate" type="text/html" href="https://github.com/jellyfin/jellyfin/releases/tag/v10.9.7"/>
            <title>10.9.7</title>
            <content type="html"><h1>🚀 Jellyfin Server 10.9.7</h1></content>
            <author><name>jellyfin-bot</name></author>
        </entry>
        <entry>
            <id>tag:github.com,2008:Repository/161012019/v10.9.6</id>
            <updated>2024-06-06T19:11:27Z</updated>
            <link rel="alternate" type="text/html" href="https://github.com/jellyfin/jellyfin/releases/tag/v10.9.6"/>
            <title>10.9.6</title>
            <content type="html"><h1>🚀 Jellyfin Server 10.9.6</h1></content>
            <author><name>jellyfin-bot</name></author>
        </entry>
    </feed>
    """

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_response
        responses.add(responses.GET, ATOM_LINK, body=mock_response, status=200)

        update_version_info()

        assert version_info.get('newest') == '10.9.7'
        assert version_info.get(
            'newest_link') == 'https://github.com/jellyfin/jellyfin/releases/tag/v10.9.7'
        assert version_info.get('current') == APP_VERSION
