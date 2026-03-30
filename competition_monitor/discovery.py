"""
Auto-discovery of new underage competitions involving Ballincollig.

Scrapes the rebelog.ie fixtures page for competitions matching the
configured AGE_GROUPS patterns that include Ballincollig but aren't
already in our config.  When a new competition appears (e.g.
championship), sends a notification so the user knows to add it.
"""

import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from competition_monitor.config import (
    AGE_GROUPS, CLUB_NAME, COMPETITIONS, NTFY_COMBINED_TOPIC,
    REBELOG_BASE_URL, get_active_age_groups,
)


# All competition IDs we already monitor
_KNOWN_IDS = {c["competition_id"] for c in COMPETITIONS.values()}


def _active_discovery_patterns():
    """Return discovery patterns for the currently active age groups only."""
    return {
        ag["discovery_pattern"].lower()
        for ag in get_active_age_groups().values()
        if "discovery_pattern" in ag
    }


def _matches_any_age_group(name):
    """Return True if the competition name matches any active age group."""
    lower = name.lower()
    return any(pat in lower for pat in _active_discovery_patterns())


def _age_group_for_name(name):
    """Return the AGE_GROUPS key for a competition name, or None."""
    lower = name.lower()
    for key, ag in AGE_GROUPS.items():
        pat = ag.get("discovery_pattern", "").lower()
        if pat and pat in lower:
            return key
    return None


def _club_in_competition(driver, league_url):
    """Load a league page and check whether CLUB_NAME appears in it."""
    try:
        driver.get(league_url)
        time.sleep(2)
        return CLUB_NAME.lower() in driver.page_source.lower()
    except Exception as e:
        print(f"Discovery: could not verify {league_url} – {e}")
        return False


def discover_new_competitions(driver):
    """Use an existing Selenium driver to scan rebelog.ie for new
    competitions involving Ballincollig across all configured age groups.

    Returns a list of dicts:
        [{"name": ..., "competition_id": ..., "url": ..., "age_group": ...}]
    """
    if not driver:
        return []

    found = []
    url = f"{REBELOG_BASE_URL}/fixtures/"

    try:
        print(f"Discovery: loading {url}")
        driver.get(url)
        time.sleep(3)

        # Wait for fixture elements
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'ul[data-date]'))
            )
        except TimeoutException:
            print("Discovery: no fixture elements found, trying links approach")

        # Approach 1: look for competition links matching age group patterns
        # The fixtures page lists competitions as headings with links to /league/{id}/
        page_source = driver.page_source

        # Find all league links
        league_pattern = re.compile(
            r'href=["\'](?:https?://rebelog\.ie)?/league/(\d+)/?["\'][^>]*>([^<]+)<',
            re.IGNORECASE,
        )
        # Also grab data attributes from fixture elements
        patterns = _active_discovery_patterns()
        comp_attr_pattern = re.compile(
            r'data-compname="([^"]*(?:' +
            '|'.join(re.escape(p) for p in patterns) +
            r')[^"]*)"',
            re.IGNORECASE,
        )
        # Collect all matching competition IDs from league links
        candidate_comps = {}  # id -> name
        for m in league_pattern.finditer(page_source):
            comp_id = int(m.group(1))
            comp_name = m.group(2).strip()
            if _matches_any_age_group(comp_name):
                candidate_comps[comp_id] = comp_name

        # Also check data-compname attributes
        for m in comp_attr_pattern.finditer(page_source):
            comp_name = m.group(1)
            # Try to find a league link for this competition
            link_match = re.search(
                r'href=["\'](?:https?://rebelog\.ie)?/league/(\d+)/?["\']',
                page_source[:m.start()][-2000:],  # search nearby
            )
            if link_match:
                candidate_comps[int(link_match.group(1))] = comp_name

        # Filter to ones we don't already know, then verify Ballincollig
        # is actually listed in the competition before reporting it.
        for comp_id, comp_name in candidate_comps.items():
            if comp_id not in _KNOWN_IDS:
                comp_url = f"{REBELOG_BASE_URL}/league/{comp_id}/"
                if _club_in_competition(driver, comp_url):
                    found.append({
                        "name": comp_name,
                        "competition_id": comp_id,
                        "url": comp_url,
                        "age_group": _age_group_for_name(comp_name),
                    })
                else:
                    print(f"Discovery: skipping {comp_name} ({comp_id}) – "
                          f"{CLUB_NAME} not found on league page")

        # Approach 2: scan fixture elements directly
        try:
            # Need to reload fixtures page since Approach 1 may have navigated away
            driver.get(url)
            time.sleep(3)
            elements = driver.find_elements(By.CSS_SELECTOR, 'ul[data-date]')
            for el in elements:
                comp_name = el.get_attribute('data-compname') or ''
                if not _matches_any_age_group(comp_name):
                    continue

                home = el.get_attribute('data-hometeam') or ''
                away = el.get_attribute('data-awayteam') or ''
                if CLUB_NAME.lower() not in home.lower() and CLUB_NAME.lower() not in away.lower():
                    continue

                # Try to find the competition ID from a nearby link
                # Use JS to find the nearest league link
                try:
                    comp_id = driver.execute_script("""
                        var el = arguments[0];
                        var parent = el.closest('.fixture-group, .competition-fixtures, section, div');
                        if (!parent) parent = el.parentElement;
                        var link = parent ? parent.querySelector('a[href*="/league/"]') : null;
                        if (link) {
                            var match = link.href.match(/\\/league\\/(\\d+)/);
                            return match ? parseInt(match[1]) : null;
                        }
                        return null;
                    """, el)
                    if comp_id and comp_id not in _KNOWN_IDS:
                        # Avoid duplicates
                        if not any(f["competition_id"] == comp_id for f in found):
                            found.append({
                                "name": comp_name,
                                "competition_id": comp_id,
                                "url": f"{REBELOG_BASE_URL}/league/{comp_id}/",
                                "age_group": _age_group_for_name(comp_name),
                            })
                except Exception:
                    pass
        except Exception as e:
            print(f"Discovery: element scan failed – {e}")

    except Exception as e:
        print(f"Discovery: error – {e}")

    if found:
        print(f"Discovery: found {len(found)} new competition(s)!")
        for f in found:
            print(f"  {f['name']} ({f.get('age_group', '?')}) -> {f['url']}")
    else:
        print("Discovery: no new competitions found")

    return found


def notify_new_competitions(new_comps):
    """Send a notification about newly discovered competitions.

    Groups by age group and sends to each relevant combined topic.
    """
    if not new_comps:
        return

    from competition_monitor.notifier import _send

    # Group by age group
    by_group = {}
    for c in new_comps:
        ag = c.get("age_group") or "unknown"
        by_group.setdefault(ag, []).append(c)

    for ag, comps in by_group.items():
        lines = []
        for c in comps:
            lines.append(f"- {c['name']}")
            lines.append(f"  ID: {c['competition_id']}")
            lines.append(f"  {c['url']}")

        # Send to the age-group combined topic
        topic = AGE_GROUPS.get(ag, {}).get("ntfy_combined_topic", NTFY_COMBINED_TOPIC)
        if not topic:
            topic = NTFY_COMBINED_TOPIC

        ag_label = ag.upper() if ag != "unknown" else ""
        _send(
            topic=topic,
            title=f"New {ag_label} Competition Found!".strip(),
            message=(
                f"New competition(s) with {CLUB_NAME} detected:\n\n"
                + "\n".join(lines)
                + "\n\nAdd to competition_monitor/config.py to start tracking."
            ),
            priority="high",
            action_url=comps[0]["url"],
        )
