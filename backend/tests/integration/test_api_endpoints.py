import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test health check endpoint"""

    async def test_health_check(self, client: AsyncClient):
        """GET /api/v1/health returns 200 with healthy status"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"


@pytest.mark.asyncio
class TestApiResponseEnvelope:
    """Test standard response envelope on all endpoints"""

    async def test_response_envelope_structure(self, client: AsyncClient):
        """All endpoints return success/data/meta/error envelope"""
        endpoints = [
            "/api/v1/venues/",
            "/api/v1/areas/",
            "/api/v1/categories/",
            "/api/v1/properties/",
            "/api/v1/visa-guides/",
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200
            data = response.json()

            # Check envelope structure
            assert "success" in data
            assert "data" in data
            assert "meta" in data
            assert "error" in data

            # For successful responses
            assert data["success"] is True
            assert data["error"] is None

    async def test_venues_list_response(self, client: AsyncClient):
        """GET /api/v1/venues/ returns paginated list"""
        response = await client.get("/api/v1/venues/")
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert data["meta"] is not None

    async def test_pagination_metadata(self, client: AsyncClient):
        """Pagination meta includes required fields"""
        response = await client.get("/api/v1/venues/")
        data = response.json()
        meta = data["meta"]

        assert "total" in meta
        assert "page" in meta
        assert "per_page" in meta
        assert "has_next" in meta
        assert "has_prev" in meta

        # Verify types
        assert isinstance(meta["total"], int)
        assert isinstance(meta["page"], int)
        assert isinstance(meta["per_page"], int)
        assert isinstance(meta["has_next"], bool)
        assert isinstance(meta["has_prev"], bool)

    async def test_pagination_first_page(self, client: AsyncClient):
        """First page should have has_prev=False"""
        response = await client.get("/api/v1/venues/?page=1")
        data = response.json()
        assert data["meta"]["has_prev"] is False

    async def test_areas_list(self, client: AsyncClient):
        """GET /api/v1/areas/ returns list of areas"""
        response = await client.get("/api/v1/areas/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_categories_list(self, client: AsyncClient):
        """GET /api/v1/categories/ returns list of categories"""
        response = await client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_properties_list(self, client: AsyncClient):
        """GET /api/v1/properties/ returns list of properties"""
        response = await client.get("/api/v1/properties/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_visa_guides_list(self, client: AsyncClient):
        """GET /api/v1/visa-guides/ returns list of visa guides"""
        response = await client.get("/api/v1/visa-guides/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_page_paths_venue_area(self, client: AsyncClient):
        """GET /api/v1/page-paths/venue-area/ returns venue paths"""
        response = await client.get("/api/v1/page-paths/venue-area/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_page_paths_properties(self, client: AsyncClient):
        """GET /api/v1/page-paths/properties/ returns property paths"""
        response = await client.get("/api/v1/page-paths/properties/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_page_paths_visa_guides(self, client: AsyncClient):
        """GET /api/v1/page-paths/visa-guides/ returns visa paths"""
        response = await client.get("/api/v1/page-paths/visa-guides/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling and 404 responses"""

    async def test_venue_not_found(self, client: AsyncClient):
        """GET /api/v1/venues/nonexistent-slug/ returns 404"""
        response = await client.get("/api/v1/venues/nonexistent-slug/")
        assert response.status_code == 404
        data = response.json()

        # Check error response structure
        assert data["success"] is False
        assert data["data"] is None
        assert data["meta"] is None
        assert data["error"] is not None

        # Check error detail
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["code"] == "VENUE_NOT_FOUND"

    async def test_area_not_found(self, client: AsyncClient):
        """GET /api/v1/areas/nonexistent-slug/ returns 404"""
        response = await client.get("/api/v1/areas/nonexistent-slug/")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "AREA_NOT_FOUND"

    async def test_category_not_found(self, client: AsyncClient):
        """GET /api/v1/categories/nonexistent-slug/ returns 404"""
        response = await client.get("/api/v1/categories/nonexistent-slug/")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "CATEGORY_NOT_FOUND"

    async def test_property_not_found(self, client: AsyncClient):
        """GET /api/v1/properties/nonexistent-slug/ returns 404"""
        response = await client.get("/api/v1/properties/nonexistent-slug/")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "PROPERTY_NOT_FOUND"

    async def test_visa_guide_not_found(self, client: AsyncClient):
        """GET /api/v1/visa-guides/{nat}/{type}/ returns 404"""
        response = await client.get("/api/v1/visa-guides/nonexistent/nonexistent/")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VISA_GUIDE_NOT_FOUND"


@pytest.mark.asyncio
class TestPagination:
    """Test pagination behavior"""

    async def test_pagination_per_page_param(self, client: AsyncClient):
        """per_page parameter is respected"""
        response = await client.get("/api/v1/venues/?per_page=5")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["per_page"] == 5

    async def test_pagination_page_param(self, client: AsyncClient):
        """page parameter is respected"""
        response = await client.get("/api/v1/venues/?page=2")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["page"] == 2

    async def test_pagination_max_per_page(self, client: AsyncClient):
        """per_page is clamped to max (100)"""
        response = await client.get("/api/v1/venues/?per_page=999")
        assert response.status_code == 200
        data = response.json()
        # Max should be enforced at 100
        assert data["meta"]["per_page"] <= 100
