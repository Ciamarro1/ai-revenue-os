from src.revenue_os.plugins.landing.models import BuildResult
from src.revenue_os.plugins.landing.providers import (
    CloudflarePagesProvider,
    VercelProvider,
    NetlifyProvider
)

def test_cloudflare_pages_provider():
    cf = CloudflarePagesProvider()
    assert cf.cdn_name == "cloudflare_pages"
    
    b = BuildResult(build_id="B1", framework="astro", manifest_id="OFFER-1", build_fingerprint="fp1")
    dep = cf.deploy_build(b, "v1.0.0")
    
    assert dep.cdn_provider == "cloudflare_pages"
    assert "pages.dev" in dep.public_url
    assert dep.is_active is True

def test_vercel_provider():
    v = VercelProvider()
    assert v.cdn_name == "vercel"
    
    b = BuildResult(build_id="B2", framework="nextjs", manifest_id="OFFER-2", build_fingerprint="fp2")
    dep = v.deploy_build(b, "v1.0.0")
    
    assert dep.cdn_provider == "vercel"
    assert "vercel.app" in dep.public_url

def test_netlify_provider():
    n = NetlifyProvider()
    assert n.cdn_name == "netlify"
    
    b = BuildResult(build_id="B3", framework="astro", manifest_id="OFFER-3", build_fingerprint="fp3")
    dep = n.deploy_build(b, "v1.0.0")
    
    assert dep.cdn_provider == "netlify"
    assert "netlify.app" in dep.public_url
