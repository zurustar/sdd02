def test_index_page_renders(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Team Scheduler' in response.data
