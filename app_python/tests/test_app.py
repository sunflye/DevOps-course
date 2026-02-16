import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestMainEndpoint:
    """Tests for GET / endpoint"""

    def test_main_endpoint_status_code(self, client):
        """Test that main endpoint returns 200"""
        response = client.get('/')
        assert response.status_code == 200

    def test_main_endpoint_content_type(self, client):
        """Test that response is JSON"""
        response = client.get('/')
        assert response.content_type == 'application/json'

    def test_main_endpoint_service_data(self, client):
        """Test that service metadata is present"""
        response = client.get('/')
        data = response.get_json()
        
        assert 'service' in data
        assert data['service']['name'] == 'devops-info-service'
        assert data['service']['version'] == '1.0.0'
        assert data['service']['framework'] == 'Flask'

    def test_main_endpoint_system_data(self, client):
        """Test that system information is present"""
        response = client.get('/')
        data = response.get_json()
        
        assert 'system' in data
        assert 'hostname' in data['system']
        assert 'platform' in data['system']
        assert 'architecture' in data['system']
        assert 'cpu_count' in data['system']
        assert 'python_version' in data['system']

    def test_main_endpoint_runtime_data(self, client):
        """Test that runtime information is present"""
        response = client.get('/')
        data = response.get_json()
        
        assert 'runtime' in data
        assert 'uptime_seconds' in data['runtime']
        assert 'uptime_human' in data['runtime']
        assert 'current_time' in data['runtime']
        assert 'timezone' in data['runtime']
        
        # Verify uptime_seconds is non-negative integer
        assert isinstance(data['runtime']['uptime_seconds'], int)
        assert data['runtime']['uptime_seconds'] >= 0

    def test_main_endpoint_request_data(self, client):
        """Test that request information is present"""
        response = client.get('/')
        data = response.get_json()
        
        assert 'request' in data
        assert 'client_ip' in data['request']
        assert 'user_agent' in data['request']
        assert 'method' in data['request']
        assert 'path' in data['request']
        
        # Verify HTTP method
        assert data['request']['method'] == 'GET'
        assert data['request']['path'] == '/'

    def test_main_endpoint_endpoints_list(self, client):
        """Test that endpoints list is present"""
        response = client.get('/')
        data = response.get_json()
        
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], list)
        assert len(data['endpoints']) == 2
        
        # Verify endpoints structure
        paths = [ep['path'] for ep in data['endpoints']]
        assert '/' in paths
        assert '/health' in paths


class TestHealthEndpoint:
    """Tests for GET /health endpoint"""

    def test_health_endpoint_status_code(self, client):
        """Test that health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_endpoint_content_type(self, client):
        """Test that response is JSON"""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_health_endpoint_status_field(self, client):
        """Test that status field is healthy"""
        response = client.get('/health')
        data = response.get_json()
        
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_health_endpoint_timestamp(self, client):
        """Test that timestamp is present"""
        response = client.get('/health')
        data = response.get_json()
        
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], str)
        # Verify ISO 8601 format with Z suffix
        assert data['timestamp'].endswith('Z')

    def test_health_endpoint_uptime(self, client):
        """Test that uptime_seconds is present"""
        response = client.get('/health')
        data = response.get_json()
        
        assert 'uptime_seconds' in data
        assert isinstance(data['uptime_seconds'], int)
        assert data['uptime_seconds'] >= 0


class TestErrorHandling:
    """Tests for error handling"""

    def test_404_not_found(self, client):
        """Test that invalid endpoint returns 404"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Not Found'

    def test_404_response_is_json(self, client):
        """Test that 404 response is JSON"""
        response = client.get('/invalid-endpoint')
        assert response.content_type == 'application/json'


class TestDataTypes:
    """Tests for data type validation"""

    def test_main_endpoint_data_types(self, client):
        """Test that response data types are correct"""
        response = client.get('/')
        data = response.get_json()
        
        # Service
        assert isinstance(data['service']['name'], str)
        assert isinstance(data['service']['version'], str)
        
        # System
        assert isinstance(data['system']['hostname'], str)
        assert isinstance(data['system']['platform'], str)
        assert isinstance(data['system']['cpu_count'], int)
        
        # Runtime
        assert isinstance(data['runtime']['uptime_seconds'], int)
        assert isinstance(data['runtime']['uptime_human'], str)
        assert isinstance(data['runtime']['timezone'], str)
        
        # Request
        assert isinstance(data['request']['method'], str)
        assert isinstance(data['request']['path'], str)