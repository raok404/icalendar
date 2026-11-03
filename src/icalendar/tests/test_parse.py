from io import BytesIO

import pytest

from icalendar import Calendar, parse

ICAL = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//icalendar tests//
END:VCALENDAR
"""

JCAL = b"""["vcalendar",[
["version",{},"text","2.0"],
["prodid",{},"text","-//icalendar tests//"]
],[]]"""

XCAL = b"""<?xml version="1.0" encoding="UTF-8"?>
<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
  <vcalendar>
    <properties>
      <version><text>2.0</text></version>
      <prodid><text>-//icalendar tests//</text></prodid>
    </properties>
  </vcalendar>
</icalendar>
"""


@pytest.mark.parametrize("data", [ICAL, JCAL, XCAL], ids=["ical", "jcal", "xcal"])
def test_parse_returns_one_calendar_by_default(data):
    calendar = parse(data)

    assert isinstance(calendar, Calendar)
    assert calendar.name == "VCALENDAR"


@pytest.mark.parametrize("data", [ICAL, JCAL, XCAL], ids=["ical", "jcal", "xcal"])
def test_parse_multiple_true_returns_a_list(data):
    calendars = parse(data, multiple=True)

    assert isinstance(calendars, list)
    assert len(calendars) == 1
    assert isinstance(calendars[0], Calendar)


def test_parse_accepts_path(tmp_path):
    path = tmp_path / "calendar.ics"
    path.write_bytes(ICAL)

    calendar = parse(path)

    assert isinstance(calendar, Calendar)


def test_parse_accepts_binary_file_without_closing_it():
    source = BytesIO(ICAL)

    calendar = parse(source)

    assert isinstance(calendar, Calendar)
    assert not source.closed


def test_parse_multiple_ical_calendars():
    data = ICAL + ICAL

    calendars = parse(data, multiple=True)

    assert len(calendars) == 2
    assert all(isinstance(calendar, Calendar) for calendar in calendars)


def test_parse_rejects_multiple_calendars_when_multiple_is_false():
    with pytest.raises(ValueError, match="multiple components"):
        parse(ICAL + ICAL)


@pytest.mark.parametrize("data", [b"", b"not a calendar"])
def test_parse_rejects_empty_or_unknown_format(data):
    with pytest.raises(ValueError, match="determine the format"):
        parse(data)


def test_parse_rejects_unsupported_source_type():
    with pytest.raises(TypeError, match="Expected source"):
        parse("BEGIN:VCALENDAR")
