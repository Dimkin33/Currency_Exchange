from pathlib import Path

from router import Router


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'src' / 'templates' / 'index.html'


def test_router_exposes_canonical_ui_contract():
    router = Router(':memory:')

    assert ('GET', '/') in router.static_routes
    assert ('GET', '/health') in router.static_routes
    assert ('GET', '/currencies') in router.static_routes
    assert ('POST', '/currencies') in router.static_routes
    assert ('GET', '/exchangeRates') in router.static_routes
    assert ('POST', '/exchangeRates') in router.static_routes
    assert ('POST', '/exchangeRates/sync') in router.static_routes
    assert ('GET', '/convert') in router.static_routes

    dynamic = {(method, route) for method, route, _ in router.dynamic_routes}
    assert ('GET', '/currency/:code') in dynamic
    assert ('GET', '/exchangeRate/:pair') in dynamic
    assert ('PATCH', '/exchangeRate/:pair') in dynamic


def test_embedded_ui_targets_canonical_backend_routes():
    html = TEMPLATE.read_text(encoding='utf-8')

    assert 'action="/currencies"' in html
    assert 'action="/exchangeRates"' in html
    assert 'action="/exchangeRates/sync"' in html
    assert 'action="/exchangeRate"' in html
    assert 'action="/convert"' in html
    assert '"/exchangeRate/" + pair' in html

    assert '/currency_exchange_war_exploded' not in html
    assert '/exchange?from=' not in html
